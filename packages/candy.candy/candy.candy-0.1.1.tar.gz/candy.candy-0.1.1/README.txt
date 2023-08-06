Introduction
------------

This library, given an user, gets his/her videos saved on youtube. 
For each video gets his name and his id. 
Then, asks to pwnyoutube to generate a valid url for the "High Quality Video (MP4)"
Downloads it in a specified folder.

that's it!

Howto use it
------------

NB this test takes some minutes to run due to download time:
>>> from candy.candy import Candy
>>> import os

Create a Candy object:
>>> c = Candy('massimoazzolini', howmany=1)
>>> namedownloadedvideo = u'Plone video used for testing purposes'

Let's download it:
>>> c.run()
Analyzing page 1
downloaded Plone video used for testing purposes

>>> filename = '%s.mp4' % (namedownloadedvideo.replace('/','-'), )
>>> filename in os.listdir(os.path.abspath(os.curdir))
True

>>> os.remove(filename)


Disclaimers
------------
I'm not affiliated in any way with both pwnyoutube.com and YouTube.com.
"YouTube" is a copyright of YouTube, LLC. 
"PWNyoutube": see http://pwnyoutube.com/

