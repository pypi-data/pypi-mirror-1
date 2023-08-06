import musicbutler

# Location of music can be local...
loc = 'c:/Documents and Settings/Michael/My Documents/My Music/'
# remote via ssh...
loc = r'michaelg@example.com:My Music'
# Or network mapped.
loc = r'\\manta\Music'
# But ssh doesn't work all the way yet :)  Network mapped songs will be
# copied to a local temp file just before playing, so there's no skipping
# while the song plays.

#butler = musicbutler.MusicButler("dra meesha mime us")
butler = musicbutler.MusicButler("Einstein")

def main():
    butler.findmusic(loc, background=False)

def profile_main():
    import cProfile, pstats
    prof = cProfile.Profile()
    prof = prof.runctx("main()", globals(), locals())
    print
    print
    stats = pstats.Stats(prof)
    stats.sort_stats("cumulative") # or 'time'
    stats.print_stats(80)

main()
butler.startlistening()

import time
while butler.islistening():
    time.sleep(1)
