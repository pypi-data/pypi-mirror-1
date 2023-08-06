import speech
import random
import thread

class MusicButler:
    def __init__(self, name):
        self._collection = {}
        self._speechlistener = None
        self._actions = None
        self.name = name

    def addalbum(self, band, album):
        band = band.lower()
        album = album.lower()
        
        collection = self._collection
        
        if band not in collection:
            collection[band] = []
        if album not in collection[band]:
            collection[band].append(album)
            collection[band].sort()

        if self._speechlistener: # update our knowledge
            self.stoplistening()
            self.listen()

    def listen(self):
        collection = self._collection
        name = self.name
        actions = {}

        # build a list of commands and actions from our collection
        for (band, albums) in collection.items():
            for album in albums:
                actions["%s, play some %s %s" % (name, band, album)] = (self._play, band, album)
                
        for band in collection.keys():
            command = (self._playband, band)
            actions["%s, play some %s, any album" % (name, band)] = command
            actions["%s, play some %s" % (name, band)] = command
            actions["%s, play %s" % (name, band)] = command
            actions["%s, what %s albums do i have?" % (name, band)] = (self._listalbums, band)
            actions["%s, what albums do i have by %s?" % (name, band)] = (self._listalbums, band)
            actions["%s, what albums do i have?" % (name)] = (self._listalbums,)
            
        for albums in collection.values():
            for album in albums:
                actions["%s, play the album %s" % (name, album)] = (self._playalbum, album)
                
        actions["%s, stop playing" % name] = (self._stopthemusic,)
        actions["%s, turn off" % name] = (self._turnoff,)
        actions["%s, what bands do i have?" % name] = (self._listbands,)
        actions["%s, can you hear me?" % name] = (self._ping,)
        actions["%s, are you there?" % name] = (self._ping,)
        actions["%s, help!" % name] = (self._help,)
        actions["%s, more help please" % name] = (self._morehelp,)
        actions["%s, more help" % name] = (self._morehelp,)
        actions["What's your name?"] = (self._sayname,)

        if self._speechlistener:
            self.stoplistening()

        self._actions = actions
        self._speechlistener = speech.listenfor(actions.keys(), self._respond_to_command)
        speech.keeplistening()
        self.say("your selection?")
        
    def stoplistening(self):
        if self._speechlistener:
            speech.stoplistening(self._speechlistener)
        self._speechlistener = None

    def say(self, phrase):
        print phrase
        print
        speech.say(phrase)        

    def _respond_to_command(self, phrase, listener):
        if phrase not in self._actions:
            # TODO: is this the right behavior?
            self.say("I don't know the phrase. %s" % phrase)
            return
        command = self._actions[phrase]
        function = command[0]
        args = command[1:]
        function(*args)

    def _sayname(self):
        self.say("My name is %s.  Always say my name "
                 "first to get my attention." % self.name)

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

    def _play(self, band, album):
        if band in collection.keys() and album in collection[band]:
            self.say("Playing %s by %s" % (album, band))
        else:
            self.say("Not found")

    def _playalbum(self, album):
        for (band, albums) in collection.items():
            if album in albums:
                self._play(band, album)
                return
        else:
            self.say("No such album. %s" % album)

    def _playband(self, band):
        if band in collection:
            self._play(band, random.choice(collection[band]))
        else:
            self.say("No such band. %s" % band)

    def _stopthemusic(self):
        self.say("Stopped.")

    def _turnoff(self):
        self.say("Goodbye.")
        self.stoplistening()

    def _listbands(self):
        bands = self._collection.keys()
        indexes = range(len(bands))
        random.shuffle(indexes)

        if len(bands) == 0:
            self.say("You don't have any bands.")
            return
        
        if len(bands) == 1:
            self.say("You have one band: %s" % bands[0])
            return

        if len(bands) > 3:
            message = "Here are 3 bands out of your %d: " % len(bands)
        else:
            message = "You have %d bands: " % len(bands)
            
        count = min(3, len(bands))
        choices = [ bands[indexes[i]] for i in range(count) ]

        while len(choices) > 1:
            choice = choices.pop()
            message += "%s, " % choice
        message += "and %s." % choices[0]
            
        self.say(message)

    def _listalbums(self, bandOfChoice=None):
        collection = self._collection
        if bandOfChoice:
            albums = [ album for album in collection[bandOfChoice] ]
        else:
            albums = [ "%s by %s" % (album, band)
                       for band in collection
                       for album in collection[band] ]
                    
        indexes = range(len(albums))
        random.shuffle(indexes)

        if len(albums) == 0:
            message = "You don't have any albums"
            if bandOfChoice:
                message += " by %s" % bandOfChoice
            self.say("%s." % message)
            return

        if len(albums) == 1:
            message = "You have one album"
            if bandOfChoice:
                message += " by %s" % bandOfChoice
            self.say("%s: %s" % (message, albums[0]))
            return

        if len(albums) > 3:
            message = "Here are 3 albums out of your %d" % len(albums)
        else:
            message = "You have %d albums" % len(albums)
            
        if bandOfChoice:
            message += " by %s" % bandOfChoice

        count = min(3, len(albums))
        choices = [ albums[indexes[i]] for i in range(count) ]
        
        message += ": "
        while len(choices) > 1:
            choice = choices.pop()
            message += "%s, " % choice
        message += "and %s." % choices[0]

        self.say(message)
