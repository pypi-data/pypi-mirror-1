#!/usr/bin/python
# Author: Daniel Garcia <dani@danigm.net>

import gtk
import pynotify
import pysweetter
import time
import urllib2
import sys

pynotify.init("SweetNotify")
s = pysweetter.Sweetter()
get_sweets = s.get_last_followings
user = 'danigm'
path = '/tmp/image.png'

for i in sys.argv:
    if i == '-a':
        get_sweets = s.get_last_comments
        user = 'index'
last2 = None

while True:
    latest = get_sweets(user)
    latest.reverse()
    if not last2:
        latest = latest[-1:]
    for last in latest:
        if not last2 or last.created > last2.created:
            last2 = last

            title = '@'+last2.user 
            text = last2.sweet + '\n(%s)' % last2.created.ctime()
            image_path = last2.avatar

            note = pynotify.Notification(title, text)

            file = urllib2.urlopen(image_path)
            file2 = open(path, 'w')
            file2.write(file.read())
            file2.close()
            file.close()

            helper = gtk.Image()

            helper.set_from_file(path)
            icon = helper.get_pixbuf()
            note.set_icon_from_pixbuf(icon)

            seconds = 10
            note.set_timeout(seconds*1000)
            note.show()
    time.sleep(30)
