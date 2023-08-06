from setuptools import setup

setup(name='musicbutler',
      version='0.1.7',
      packages=['musicbutler'],
      install_requires=['speech', 'mutagen', 'mp3play'],

      description="A robot that receives voice commands to play albums"
         " from your MP3 collection",

      long_description="""
-----------
MusicButler
-----------

*** NOTE: This is an alpha product.  The example.py file can get you
going, but it has no GUI and the underlying mp3play module doesn't
work with all mp3s yet for some reason.***

When MusicButler has been told what albums you own, a spoken
conversation with it might go like this:

  * "Afred, what albums do I have?"
  * "Here are 3 out of your 58 albums: In Rainbows by Radiohead, Deja Vu by Crosby Stills Nash and Young, and Atlanta by Alison Krauss."
  * "Afred, what Radiohead albums do I have?"
  * "You have 2 albums by Radiohead: In Rainbows, and OK Computer."
  * "Afred, play me some Alison Krauss, any album."
  * "Playing New Favorite by Alison Krauss."

Requirements
-----------------
Requires Windows XP, and Python2.5.  Windows XP because it uses
the 'speech' module -- see that on pypi for prerequisites.  And
Python2.5 because it uses the mp3play module -- which is still in
alpha too so don't be surprised if some songs don't play properly.

Please let me know if you like or use this module - it would make
my day!
""",

      author='Michael Gundlach',
      author_email='gundlach@gmail.com',
      url='http://musicbutler.googlecode.com/',
      keywords = "speech recognition music stereo control mp3 robot butler",

      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Win32 (MS Windows)',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: Microsoft :: Windows',
          'Programming Language :: Python',
          'Topic :: Multimedia :: Sound/Audio :: Speech',
          'Topic :: Multimedia :: Sound/Audio',
          'Topic :: Home Automation',
          'Topic :: Scientific/Engineering :: Human Machine Interfaces',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Desktop Environment',
          ]

     )
