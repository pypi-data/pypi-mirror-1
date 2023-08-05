import mechanoid
import BeautifulSoup
import os
import time
import re

import sha
def shash(s):
    o = sha.sha()
    o.update(s)
    return o.hexdigest()

def clean_string_for_filenames(s, FAKESPACE = '.'):
    ''' Takes a string s and converts it into something
    non-controversial for a filename.  Note that "/" will get broken.'''
    s = s.lower()
    s = s.replace(' ', FAKESPACE) # a style choice
    # now replace any remaining non-alphanumerics with "_"
    # screw you, accented characters
    s = re.sub('[^0-9a-z' + FAKESPACE  + ']', '_', s)
    return s

class EmusicSong:
    songId = 0
    artistId = 0
    albumId = 0
    vdlUrl = ''
    def __init__(self, songId, artistId, albumId, vdlUrl):
        self.songId = songId
        self.artistId = artistId
        self.albumId = albumId
        self.vdlUrl = vdlUrl
        assert(self.vdlUrl[0] == '/')
    def url(self):
        return 'http://www.emusic.com' + self.vdlUrl

def url2soup(url):
    soup = BeautifulSoup.BeautifulSoup(fromEncoding='utf-8')
    b = mechanoid.Browser()
    soup.feed(unicode(b.open(url).read(), 'utf-8'))
    return soup

def artistid2name(id):
    idstring = str(id)
    url = 'http://www.emusic.com/artist/%s/%s.html' % (idstring[:5], idstring)
    soup = url2soup(url)
    return soup('div', {'class': 'name'})[0].contents[0]

def albumid2name(id):
    idstring = str(id)
    url = 'http://www.emusic.com/album/%s/%s.html' % (idstring[:5], idstring)
    soup = url2soup(url)
    return soup('div', {'class': 'albumTitle'})[0].contents[0]

def vdl2id(s):
    ''' Takes /vdl/song/10842607/13103750.html?gb=lm and returns
    int(13103750).  Ignores implicit albumId.'''
    s = s.split('?', 1)[0] # throw away question-mark parts
    
    l = s.split('/')
    assert(len(l) == 5)
    assert(l[0] == '')
    assert(l[1] == 'vdl')
    assert(l[2] == 'song')
    albumId = l[3] # I ignore this
    basename, extension = l[4].rsplit('.', 1)
    assert(extension == 'mp3' or extension == 'html')
    return int(basename)

def href2id(s):
    ''' embodies built-in assumptions about eMusic links, and returns
    the ID number that this signifies
    example: /artist/11577/11577907.html
    example: /artist/11577/11577907.html?no-one-cares
    example: http://www2.emusic.com/album/10842/10842607.html'''
    s = s.split('?', 1)[0] # throw away question-mark parts
    # try to remove emusic.com junk
    emusicsplitted = re.split(r'http://www.*?\.emusic\.com(/.*)', s, 1)
    if len(emusicsplitted) == 3:
        s = emusicsplitted[1]

    l = s.split('/')
    assert(len(l) == 4)
    assert(l[0] == '')
    assert(l[1] in ('artist', 'album', 'song'))
    assert(len(l[2]) == 5)
    assert(l[2] == l[3][:5])
    assert(l[3][-5:] == '.html')
    return l[3][:-5]

class AlbumPage:
    """ Note: When you're not logged in, you get a link to .emp files
    rather than /vdl/ links.  This breaks AlbumPage.  Therefore, pass it
    a logged-in Browser object. """
    artistId = 0
    albumId = 0
    songs = None
    def __init__(self, url, b = None):
        """ Parse the AlbumPage at url and become at one with the page's contents """
        self.songs = []
        self.albumId = href2id(url)
        soup = BeautifulSoup.BeautifulSoup(fromEncoding='utf-8')
        if b is None:
            b = mechanoid.Browser()
        soup.feed(unicode(b.open(url).read(), 'utf-8'))
        self.artistId = href2id(soup('span', {'class':'artist'})[0].findNext('a')['href'])
        for link in soup('a'):
            href = link['href']
            if '/vdl/' in href:
                songId = vdl2id(href)
                song = EmusicSong(songId, self.artistId, self.albumId, href)
                self.songs.append(song)

class Emusic:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.b = mechanoid.Browser()
        #self.b.set_handle_robots(False)# my mechanoid lacks this, wonder why
        self.login()

    def downloads_remaining(self):
        ''' Returns an integer of how many songs you can downloads '''
        accountpage = self.b.open('https://www.emusic.com/account/index.html').read()
        soup = BeautifulSoup.BeautifulSoup(fromEncoding='utf-8')
        soup.feed(accountpage)
        # first accountDownloads is "You have XX downloads remaining"
        # next two are "XX subscription downloads", and "XX Booster Pack downloads"
        # who cares about details?  We want the first one.
        return int(str(soup('span', {'class': 'accountDownloads'})[0].contents[0]))

    def login(self):
        self.b.open('https://www.emusic.com/sessions/signon.html')
        self.b.select_form(name="login")
        self.b['email'] = self.username
        self.b['password'] = self.password
        self.b.submit()

    def get(self, url):
        self.b.open(url)
        return self.b.response.read()

    def get_song_url(self, song):
        ''' Take the song and return its (url, nicename) pair '''
        url = song.url()
        urlfd = self.b.open(url)
        disposition = self.b.response.wrapped.headers.getheader('content-disposition')
        url = urlfd.url
        nicename = url.split('/')[-1]
        if disposition:
            if 'filename' in disposition:
                nicename = disposition.split('filename=')[1].strip()
        if 'mp3' in url:
            return (url, nicename)
        else:
            print "Sad that", url, "isn't an mp3 file."

    def list_old_downloads(self):
        '''Just a list of EmusicSongs. '''
        ret = []
        masterpage = self.b.open('http://www.emusic.com/profile/profDwnldsFrameArtists.html').read()
        artistPages = re.findall(r'profDwnldsFrameAlbums.html\?artistId=[0-9]*', masterpage)
        for artistPage in artistPages:
            artistId = int(artistPage.split('artistId=')[1])
            artistContents = self.b.open('http://www.emusic.com/profile/' + artistPage).read()
            albumPages = re.findall(r'profDwnldsFrameTracks.html\?albumId=[0-9]*', artistContents)
            for albumPage in albumPages:
                albumId = int(albumPage.split('albumId=')[1])
                albumContents = self.b.open('http://www.emusic.com/profile/' + albumPage).read()
                songVdls = re.findall(r'/vdl/song/[0-9]*/[0-9]*.(?:mp3|html)', albumContents)
                for songVdl in songVdls:
                    songId = vdl2id(songVdl)
                    song = EmusicSong(songId, artistId, albumId, songVdl)
                    ret.append(song)
        return ret
