import speech
import random
import thread
import time
import math
import mp3play

from locators import FileSearcher

from mutagen.easyid3 import EasyID3

class MusicButler:
    def __init__(self, name):
        self._clip = None
        self._volumelevel = 100
        self._collection = {}
        self._speechlistener = None
        self._commands = None
        self.name = name

    def findmusic(self, location, background=True):
        """
        Scours the given location for all MP3s, and adds them to
        the butler's collection.  If background, runs on a separate
        thread and rebuilds the collection every few hundred files,
        so that the butler is quickly responsive if not omniscient.
        Otherwise, blocks until finished.
        """
        if not background:
            self._findmusic(location, rebuild_commands=False)
        else:
            thread.start_new_thread(self._findmusic, (location,) )

        self._rebuild_commands()

    def _findmusic(self, location, rebuild_commands=True):
        """
        Scours the given location for all MP3s, and adds them to
        the butler's collection.  If rebuild_commands and the butler is
        currently listening, rebuild the list of understood commands
        every few hundred files.
        """
        count, last_count_learned, secs = 0, 0, 0
        start = time.time()
        for (band, album, song, locator) in ID3Reader(location).read():
            self.addsong(band, album, song, locator, rebuild_commands=False)

            count += 1
            secs_passed = math.floor(time.time() - start)
            if secs_passed >= secs + 5:
                secs = secs_passed
                print "Songs found: %s..." % count

                if rebuild_commands and count - last_count_learned > 200:
                    last_count_learned = count
                    self._rebuild_commands()

    def addsong(self, band, album, song, locator, rebuild_commands=True):
        """Either locator is a string filename, or a Locator instance that
        can be later used to fetch the filename.  If rebuild_commands,
        rebuild the list of voice commands to respond to.
        """
        def clean(s):
            if not s:
                return ''
            s = s.strip().lower()
            numbers = ['zero','one','two','three','four','five','six','seven',
                       'eight','nine']
            for (number, word) in enumerate(numbers):
                s = s.replace(str(number), ' %s ' % word)

            s = s.replace('/', ' slash ').strip()
            while '  ' in s:
                s = s.replace('  ', ' ')

            return s

        band = clean(band)
        album = clean(album)
        song = clean(song)

        if band.endswith(', the'):
            band = band[:-5]
        if band.startswith('the '):
            band = band[4:]

        if not band or not album or not song:
            return

        album = self._collection.setdefault(band, {}).setdefault(album, [])
        if (song, locator) not in album:
            album.append( (song, locator) )

        if rebuild_commands:
            self._rebuild_commands()

    def islistening(self):
        return not not self._speechlistener

    def _addaction(self, commanddict, action, commands, strings):
        for command in commands:
            command = command % strings
            commanddict["%s, %s" % (self.name, command)] = action

    def _rebuild_commands(self):
        """Rebuild self._commands from self._collection."""
        collection = self._collection
        name = self.name
        commands = {}

        # build a list of commands and actions from our collection
        for (band, albums) in collection.items():
            self._addaction(commands, (self._playalbum, band),
                [ "play some %s, any album",
                  "play some %s",
                  "play %s"
                ], band)

            self._addaction(commands, (self._playsong, band),
                  [ "play a song by %s",
                    "play something by %s"
                  ], band)

            self._addaction(commands, (self._listalbums, band),
                [ "what albums do I have by %s",
                  "what albums do I have by the band %s",
                  "what %s albums do I have"
                ], band)

            self._addaction(commands, (self._listsongs, band),
                [ "what songs do I have by %s",
                  "what songs do I have by the band %s",
                  "what %s songs do I have"
                ], band)

            # album-specific commands for this band
            for (album, songs) in albums.items():
                self._addaction(commands, (self._playalbum, band, album),
                    [ "play %s by %s",
                      "play the album %s by %s",
                      "play %s by the band %s",
                      "play the album %s by the band %s"
                    ], (album, band))

                self._addaction(commands, (self._playalbum, band, album),
                    [ "play some %s, %s",
                      "play %s: %s"
                    ], (band, album))

                self._addaction(commands, (self._playalbum, band, album),
                    [ "play the album %s",
                      "play %s" ], album)

                # song-specific commands for this band and album
                for (song, locator) in songs:
                    self._addaction(commands, (self._playsong, band,album,song),
                        [ "play %s",
                          "play the song %s",
                        ], song)

                    self._addaction(commands, (self._playsong, band,album,song),
                        [ "play %s by %s",
                          "play the song %s by %s",
                          "play %s by the band %s",
                          "play the song %s by the band %s"
                        ], (song, band))

        #commands["%s, help!" % name] = (self._help,)
        #commands["%s, more help please" % name] = (self._morehelp,)
        #commands["%s, more help" % name] = (self._morehelp,)
        commands["%s, are you there" % name] = (self._ping,)
        #commands["What's your name"] = (self._sayname,)
        commands["%s, what bands do i have" % name] = (self._listbands,)
        commands["%s, what albums do i have" % name] = (self._listalbums,)
        commands["%s, what songs do i have" % name] = (self._listsongs,)
        commands["%s, pause" % name] = (self._pause, True)
        commands["%s, unpause" % name] = (self._pause, False)
        commands["%s, stop playing" % name] = (self._stopthemusic,)
        commands["%s, stop the music" % name] = (self._stopthemusic,)
        commands["%s, start over" % name] = (self._rewind,)
        commands["%s, turn off" % name] = (self._turnoff,)
        commands["%s, play a random song" % name] = (self._playsong,)
        commands["%s, play something" % name] = (self._playsong,)

        numbers = ("zero ten twenty thirty fourty fifty sixty seventy" +
                   "eighty ninety").split()

        for (i, number) in enumerate(numbers):
            commands["%s, volume %s" % (name, number)] = (self._volume, i*10)

        self._addaction(commands, (self._volume, 100),
                ["volume one hundred",
                 "volume a hundred"
                ], () )

        commands["%s, louder" % name] = (self._volumechange, True, False)
        commands["%s, quieter" % name] = (self._volumechange, False, False)
        commands["%s, much louder" % name] = (self._volumechange, True, True)
        commands["%s, much quieter" % name] = (self._volumechange, False, True)
        commands["%s, again please" % name] = (self._repeatcommand, )
        commands["Why do you suck so much"] = (self.say,
                "Because my creator is an idiot.")
        commands["I will kill you."] = (self.say, "That's fair.")

        self._commands = commands

    def startlistening(self):
        self._rebuild_commands()

        if self.islistening():
            self.stoplistening()

        self._speechlistener = speech.listenfor(
                self._commands.keys(), self._respond_to_command)
        self.say("Your selection?")

    def stoplistening(self):
        if self.islistening():
            self._speechlistener.stoplistening()
        self._speechlistener = None

    def say(self, phrase):
        print phrase
        print
        speech.say(phrase)

    def _respond_to_command(self, phrase, listener):
        if phrase not in self._commands:
            # TODO: is this the right behavior?
            self.say("I don't know the phrase. '%s'" % phrase)
            return
        command = self._commands[phrase]
        function = command[0]
        args = command[1:]
        if command[0] != self._repeatcommand:
            self._lastcommand = function
            self._lastcommandargs = args
        function(*args)

    def _sayname(self):
        self.say("My name is %s.  Always say my name "
                 "first to get my attention." % self.name)

    def _rewind(self):
        if self._clip and self._clip.isplaying():
            self._clip.play()
        else:
            self.say("Nothing is playing.")

    def _repeatcommand(self):
        if hasattr(self, "_lastcommand"):
            self._lastcommand(*self._lastcommandargs)

    def _volume(self, level):
        if not self._clip or not self._clip.isplaying():
            return
        self._volumelevel = level
        self._clip.volume(self._volumelevel)
        self.say("Done.")

    def _volumechange(self, increase, big):
        """Increase or decrease volume by 20%.  If big, go straight to 100%%
        or 10%%.  This function won't decrease quite all the way to silent.
        """
        if not self._clip or not self._clip.isplaying():
            return

        vol = self._volumelevel
        if big:
            target = 100 if increase else 10
        else:
            target = vol + 20 if increase else vol - 20

        if increase:
            self._volumelevel = target if target <= 100 else 100
        else:
            self._volumelevel = target if target >= 10 else 10
        self._clip.volume(self._volumelevel)
        self.say("Done.")

    def _pause(self, pause):
        """Pause"""
        if not self._clip:
            return

        if self._clip.isplaying() and pause:
            self._clip.pause()
        elif self._clip.ispaused() and not pause:
            self._clip.unpause()

    def _help(self):
        message = """
        Always say my name, %s, first.
        You can ask me what bands or albums you have,
        or you can say, %s, play the album pet sounds by beach boys.
        Or, just say, %s, play some beach boys.
        Say, %s stop playing, to stop the music.
        Say, %s more help please, if you really need to.
        """ % ((self.name,) * 5)
        self.say(message)

    def _morehelp(self):
        message = """
        Always say my name, %s, first.
        You can say, play some beach boys, any album.
        Or, play the album pet sounds by beach boys.
        Or, stop playing, to stop the music.
        Or, turn off, to turn me off entirely.
        Or, are you there?, to see if I can hear you.
        You can ask, what albums do I have by the beach boys?
        Or, what albums do I have?
        Or, what bands do I have?
        Remember, always say my name, %s, first.
        """ % (self.name, self.name)
        self.say(message)

    def _ping(self):
        self.say("Yes")

    def _getalbum(self, band=None, album=None):
        """Return (band, album, songlist).  If no album is given,
        choose a random one by the band.  If no band is given, choose
        a random band.  If the band or album is not known, return
        (None, None, None).
        """
        collection = self._collection
        try:
            if not band:
                band = random.choice(collection.keys())
            if not album:
                album = random.choice(collection[band].keys())
            songs = collection[band][album]
            return (band, album, songs)
        except:
            return (None, None, None)

    def _getsong(self, band=None, album=None, song=None):
        """Return (band, album, song, locator).  If no band is given, choose a
        random band.  If no album is given, choose a random album by the band.
        If no song is given, choose a random song from the album.  If the band
        or album or song is not known, return (None, None, None).
        """
        collection = self._collection
        try:
            (band, album, songs) = self._getalbum(band, album)
            if not song:
                song = random.choice(songs)[0]
            for (title, locator) in songs:
                if title == song:
                    return (band, album, song, locator)
            else:
                raise Exception # song name not found, so return (None,)*4
        except:
            return (None, None, None, None)


    def _playalbum(self, band=None, album=None):
        (band, album, songs) = self._getalbum(band, album)
        if not songs:
            self.say("Not found")
            return

        self._stop()
        self.say("Playing %s: %s" % (band, album) )
        self._playfile(songs[0][1])

    def _playsong(self, band=None, album=None, song=None):
        (band, album, song, locator) = self._getsong(band, album, song)
        if not locator:
            self.say("Not found")
            return

        self._stop()
        self.say("%s: %s" % (band, song) )
        self._playfile(locator)
        return

    def _playfile(self, locator):
        filename = locator.filename()
        self._clip = mp3play.load(filename)
        self._clip.volume(self._volumelevel)
        self._clip.play()

    def _stop(self):
        if self._clip:
            self._clip.stop()

    def _stopthemusic(self):
        self._stop()
        self.say("Stopped.")

    def _turnoff(self):
        if self._clip:
            self._clip.stop()

        self.say("Goodbye.")
        self.stoplistening()

    def _listthings(self, thingname, things, bandOfChoice=None):
        things = list(things)
        random.shuffle(things)

        if len(things) == 0:
            msg = "You don't have any %ss" % thingname
            if bandOfChoice:
                msg += " by %s" % bandOfChoice
            self.say("%s." % msg)
            return

        if len(things) == 1:
            msg = "You have one %s" % thingname
            if bandOfChoice:
                msg += " by %s" % bandOfChoice
            self.say("%s: %s" % (msg, things[0]))
            return

        if len(things) > 3:
            msg = "Here are 3 %ss out of your %d" % (thingname, len(things))
        else:
            msg = "You have %d %ss" % (len(things), thingname)
        if bandOfChoice:
            msg += " by %s" % bandOfChoice
        msg += ": "

        count = min(3, len(things))
        choices = things[ :count]

        while len(choices) > 1:
            choice = choices.pop()
            msg += "%s, " % choice
        msg += "and %s." % choices[0]

        for thing in things[-200: ]:
            print thing

        self.say(msg)

    def _listbands(self):
        self._listthings("band", self._collection.keys())

    def _listalbums(self, bandOfChoice=None):
        collection = self._collection
        if bandOfChoice:
            albums = [ album for album in collection[bandOfChoice] ]
        else:
            albums = [ "%s by %s" % (album, band)
                       for band in collection
                       for album in collection[band] ]
        self._listthings("album", albums, bandOfChoice=bandOfChoice)

    def _listsongs(self, bandOfChoice=None):
        collection = self._collection
        if bandOfChoice:
            titles = [ title
                       for (album, songs) in collection[bandOfChoice].items()
                       for (title, locator) in songs ]
        else:
            titles = [ "%s by %s" % (title, band)
                       for band in collection
                       for (album, songs) in collection[band].items()
                       for (title, locator) in songs ]
        self._listthings("song", titles, bandOfChoice=bandOfChoice)


class ID3Reader(object):
    def __init__(self, location):
        self._searcher = FileSearcher.FileSearcher(location)

    def read(self):
        """
        Read all mp3 tag information in our location.

        Returns an iterator of (artist, album, title, locator) tuples.
        """
        for locator in self._searcher.search():
            try:
                data = EasyID3(locator.filename_for_tagging())
            except:
                continue
            if 'album' not in data or 'artist' \
                    not in data or 'title' not in data:
                continue
            artist, album, title = data['artist'], \
                    data['album'], data['title']

            artist = artist if type(artist) is str else artist[0]
            album = album if type(album) is str else album[0]
            title = title if type(title) is str else title[0]

            yield (artist, album, title, locator)

