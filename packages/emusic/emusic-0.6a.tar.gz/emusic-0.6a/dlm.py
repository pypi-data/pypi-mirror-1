#!/usr/bin/python
DEBUG=1
def debug(o):
	global DEBUG
	if DEBUG:
		print o

import ConfigParser
import os
import dialog
import sys
import emusic
import re

artists = {}
albums = {}

def artistid2name(id):
    global artists
    if id in artists:
        return artists[id]
    else:
        result = emusic.artistid2name(id)
        result = emusic.clean_string_for_filenames(result, ' ') # artists get spaces in their names
        artists[id] = result
        return result

def albumid2name(id):
    global albums
    if id in albums:
        return albums[id]
    else:
        result = emusic.albumid2name(id)
        result = emusic.clean_string_for_filenames(result)
        albums[id] = result
        return result

config = ConfigParser.ConfigParser()
config.read(os.path.expanduser('~/.emusic'))

# XXX We should handle the new DIALOG_HELP and DIALOG_EXTRA return codes here.
def handle_exit_code(d, code):
    """Sample function showing how to interpret the dialog exit codes.

    This function is not used after every call to dialog in this demo
    for two reasons:

       1. For some boxes, unfortunately, dialog returns the code for
          ERROR when the user presses ESC (instead of the one chosen
          for ESC). As these boxes only have an OK button, and an
          exception is raised and correctly handled here in case of
          real dialog errors, there is no point in testing the dialog
          exit status (it can't be CANCEL as there is no CANCEL
          button; it can't be ESC as unfortunately, the dialog makes
          it appear as an error; it can't be ERROR as this is handled
          in dialog.py to raise an exception; therefore, it *is* OK).

       2. To not clutter simple code with things that are
          demonstrated elsewhere.

    """
    # d is supposed to be a Dialog instance
    if code in (d.DIALOG_CANCEL, d.DIALOG_ESC):
        if code == d.DIALOG_CANCEL:
            msg = "You chose cancel in the last dialog box. Do you want to " \
                  "quit this program?"
        else:
            msg = "You pressed ESC in the last dialog box. Do you want to " \
                  "quit this program?"
        # "No" or "ESC" will bring the user back to the demo.
        # DIALOG_ERROR is propagated as an exception and caught in main().
        # So we only need to handle OK here.
        if d.yesno(msg) == d.DIALOG_OK:
            sys.exit(0)
        return 0
    else:
        return 1                        # code is d.DIALOG_OK

def textinput(d, message):
    ''' Tell the user message, and get his input. '''
    while 1:
        (code, response) = d.inputbox(message)
        if handle_exit_code(d, code):
            break
    return response.strip()

def prompt_for_login(d):
    # Get the username and password from the user.
    username = textinput(d, "What's the email address you use for emusic?")
    
    while 1:
        (code, password) = d.passwordbox("What is your emusic password?")
        if handle_exit_code(d, code):
            break
    return username, password

def quit(d, em):
    print "Bye!"

def download_save_for_later(d, em):
    saved = em.get('http://www.emusic.com/lists/saveforlater.html')
    albums = re.findall('/album/[0-9]*/[0-9]*.html', saved)
    done = []
    for album in albums:
        if album not in done:
            download_album_with_url(d, em, 'http://www.emusic.com' + album)
        done.append(album)

def download_one(em, song, path, loop_function = None):
    if loop_function is None:
        loop_function = lambda: True
    if loop_function():
        try:
            os.makedirs(path)
        except OSError, e:
            if e.errno == 17:
                pass
            else:
                raise e
        url, nicename = em.get_song_url(song)
        fullpath = os.path.join(path, nicename)
        if not os.path.exists(fullpath):
            partpath = fullpath + '.part'
            fd = open(partpath, 'w')
            fd.write(em.get(url))
            fd.close()
            os.rename(partpath, fullpath)

def download_album(d, em):
    albumurl = textinput(d, "What's the URL to that album?")
    download_album_with_url(d, em, albumurl)

def download_album_with_url(d, em, albumurl):
    ap = emusic.AlbumPage(albumurl, em.b)
    debug(ap.songs)
    so_far = 0
    total = len(ap.songs) * 1.0
    d.gauge_start("Progress: 0%", title="Download album %s (#%d)" % (emusic.albumid2name(ap.albumId), int(ap.albumId)))
    for song in ap.songs:
        so_far += 1
        i = int(100.0 * so_far / total)
        if em.downloads_remaining():
            artistdir = artistid2name(ap.artistId)
            albumdir = albumid2name(ap.albumId)
            path = os.path.join(config.get('storage', 'base_dir'), artistdir, albumdir)
            download_one(em, song, path, em.downloads_remaining)
	if i < 50:
	    d.gauge_update(i, "Progress: %d%%" % i, update_text=1)
	elif 50 < i < 80:
	    d.gauge_update(i, "Over %d%%. Good." % i, update_text=1)
	elif 80 < i < 100:
	    d.gauge_update(i, "You're so close!", update_text=1)
	else:
            d.gauge_update(i)
            
def download(d, em):
    l = em.list_old_downloads()
    total = len(l) * 1.0
    so_far = 0
    d.gauge_start("Progress: 0%", title="Downloading all songs")
    for song in l:
        so_far += 1
        i = int(100.0 * so_far / total)
        artistdir = artistid2name(song.artistId)
        albumdir = albumid2name(song.albumId)
        path = os.path.join(config.get('storage', 'base_dir'), artistdir, albumdir)
        download_one(em, song, path)
	if i < 50:
	    d.gauge_update(i, "Progress: %d%%" % i, update_text=1)
	elif 50 < i < 80:
	    d.gauge_update(i, "Over %d%%. Good." % i, update_text=1)
	elif 80 < i < 100:
	    d.gauge_update(i, "You're so close!", update_text=1)
	else:
            d.gauge_update(i)

    d.gauge_stop()

def downloads_remaining(d, em):
    d.msgbox("You have %d downloads remaining" % em.downloads_remaining())

def mainloop(d, em):
    choice2action = {'Leech': download,
                     'Account check': downloads_remaining,
                     'Download album': download_album,
                     'Save from later': download_save_for_later,
                     'Quit': quit}
    message = 'What do you want to do?'
    choices = [
        ('Leech', 'Download all songs from your eMusic library.'),
        ('Account check', 'See how many downloads you have available for the month'),
        ('Download album', "Give me an album URL and I'll download it"),
        ('Complete albums', 'For any album you have one song from, download all songs from it'),
        ('Save from later', "Download all the albums you've saved for later"),
        ('Quit', 'Quit this program.')]
    choice = menu(d, message, choices)
    while (choice != 'Quit'):
        choice2action[choice](d, em)
        choice = menu(d, message, choices)

def main():
    d = dialog.Dialog(dialog="Xdialog")
    #d.add_persistent_args(["--backtitle", "Emusic download manager"])
    
    # Login configuration
    if 'login' not in config.sections():
        config.add_section("login")
        username, password = prompt_for_login(d)
        config.set("login", "username", username)
        config.set("login", "password", password)

    # I should be smarter about checking for values, not just sections, but whatev
    if 'storage' not in config.sections():
        config.add_section('storage')
        base_dir = textinput(d, "Where do you want to store your eMusic songs?  It must be an absolute path.")
        config.set("storage", "base_dir", base_dir)

    em = emusic.Emusic(config.get("login", "username"),
                       config.get("login", "password"))

    # He will loop forever 'neath the streets of Boston
    mainloop(d, em)
    
    
def menu(d, message, choices):
    while 1:
        (code, tag) = d.menu(
            message,
            width=80,
            choices=choices)
        if handle_exit_code(d, code):
            break
    return tag.strip() # Xdialog returns a trailing newline

def saveconfig():
    fd = open(os.path.expanduser('~/.emusic'), 'w')
    config.write(fd)
    fd.close()

if __name__ == '__main__':
    main()
    saveconfig()
