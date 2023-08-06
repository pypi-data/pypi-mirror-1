import tempfile
import os

class FileSearcher(object):
    @staticmethod
    def FileSearcher(location):
        if '@' in location:
            return SshFileSearcher(location)
        elif location.startswith(r'\\'): # two backslashes
            return NetworkFileSearcher(location)
        else:
            return NormalFileSearcher(location)

class NormalLocator(object):
    """Doesn't do anything fancy, just hands back the filename."""
    __slots__ = '_filename'

    def __init__(self, filename):
        self._filename = filename

    def filename_for_tagging(self):
        return self._filename

    def filename(self):
        return self._filename

class NormalFileSearcher(FileSearcher):
    def __init__(self, location):
        self.location = location

    def search(self):
        for (dirname, dirs, files) in os.walk(self.location):
            for filename in files:
                if filename.lower().endswith('.mp3'):
                    yield self.make_locator(dirname + '/' + filename)

    def make_locator(self, path):
        return NormalLocator(path)

class NetworkLocator(object):
    def __init__(self, filename):
        self._filename = filename
        self._cachedfilename = None

    def filename(self):
        if not self._cachedfilename:
            self._cachedfilename = self._fetch()
        return self._cachedfilename

    def filename_for_tagging(self):
        # safe to tag over the network, as it doesn't read the whole file
        return self._filename

    def _fetch(self):
        fd, tmpname = tempfile.mkstemp()
        os.close(fd)
        # make a local copy of the file
        file(tmpname, 'wb').write(file(self._filename, 'rb').read())
        return tmpname

class NetworkFileSearcher(NormalFileSearcher):
    def __init__(self, location):
        self.location = location

    def make_locator(self, path):
        return NetworkLocator(path)

class SshFileSearcher(FileSearcher):
    # TODO: get working.  the scripting approach is frail because it
    # relies on cat being installed.  Maybe use 'type' instead, which
    # binds us to Windows.

    def __init__(self, location):
        try:
            self.userAndHost = location[0 : location.index(':')]
        except ValueError:
            raise Exception('SshFileSearcher expects a ":" in the location.')

        self.location = location
        self._password = None

    def _getPassword(self):
        while not self._password:
            password = raw_input("Enter the password for %s: "
                    % self.userAndHost)
            try:
                self.ssh(password, "")
            except Exception:
                print "Not the correct password."
                raise
            else:
                self._password = password

    def search(self):
        """Get a password, connect, build all the file envelopes,
        store them locally.  Yield SshLocators for each file.
        """
        self._getPassword()

        sh_program = """
            #!/bin/bash

            # Script to print the names and envelopes of all mp3s
            # found on a system.  Used over ssh to gather tag info
            # from a remote host.

            filenames=/tmp/filenames.$$
            halfoffile=512

            # Find all mp3 files, and put their names in $filenames.
            find music -iname '*.mp3' > $filenames

            # Print out the number of files found.
            cat $filenames | wc -l

            # For each file,
            cat $filenames | while read file; do
                # Print out the name,
                echo "$file"

                # and the first and last 512 bytes.  This is where the ID3 tags
                # hide, so we only need this part of the file.  Note that we
                # don't print a newline, so we can later read exactly 1024
                # bytes and be ready to read the next filename.
                head -c $halfoffile "$file"
                tail -c $halfoffile "$file"
            done
            """

        output_file = self.ssh(self._password, sh_program)
        for (mp3file, artist, album, title) in self.getTagInfo(output_file):
            yield SshLocator(self, mp3file)

    def ssh(self, password, command):
        """Run the command on the remote host and return the output pipe."""
        fd, tmpname = tempfile.mkstemp()
        os.close(fd)
        file(tmpname, 'w').write(command)

        # TODO: how to use the password?
        cmd = "cat %s | ssh %s" % (tmpname, self.userAndHost)
        print cmd
        return os.popen(cmd)

    def getTagInfo(self, f):
        """
        Format of the file f that this reads:

        <Number of mp3s in this file, eg 3 in this example>
        <mp3 #1 filename>
        <1024 bytes of mp3, no newline><mp3 #2 filename>
        <1024 bytes of mp3, no newline><mp3 #3 filename>
        <1024 bytes of mp3, no newline>

        Yields (filename, artist, album, title) tuples as it reads them.
        """

        # 1st line: number of mp3s.
        count = int(f.readline().rstrip())

        result = []

        tmpfile = '_taginfo_.tmp'
        for i in range(count):
            # next line: filename.
            filename = f.readline().rstrip()

            # next 1024 bytes: mp3 info.
            file(tmpfile, 'wb').write(f.read(1024))

            tags = eval(repr(EasyID3(tmpfile))) # convert to dict
            os.remove(tmpfile)
            yield (filename,
                    tags['artist'][0], tags['album'][0], tags['title'][0])
