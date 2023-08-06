import string
import urllib
import os.path
from BeautifulSoup import BeautifulSoup

PWN = 'http://www.pwnyoutube.com/watch?v=%s'
VIDEOLIST = 'http://www.youtube.com/profile?user=%s&view=videos&start=%s'

class Candy:
    
    KO = 0
    OK = 1
    CANNOT_SAY= 2
    
    def __init__(self, user, path = None, howmany=250):
        """
        you have to set the 'user' and optionally 'path' and 'howmany' video you want to 
        download
        """
        self.user = user
        if not path:
            path = os.path.abspath(os.curdir)
        self.path = path
        self.howmany = howmany
        self.nr_downloaded = 0
        
    def run(self):
        """
        it runs the download of all the videos
        """
        self.nr_downloaded = 0
        for i in range(0,self.howmany,20):
            print 'Analyzing page %s' % (i+1, )
            url = VIDEOLIST % (self.user,i,)
            html = urllib.urlopen(url)
            for name, id in self._getMetadata(html):
                if self.nr_downloaded == self.howmany:
                    return
                self._download(name, self._getPWN(id))

    def _getMetadata(self, html):
        """
        get the 'a' inside a 'div' with class 'video-short-title':
        
        
        I need the title as 'name' and the id (fourth part in the id of the 'a')
        >>> c = Candy('user')
        >>> html = '''<div class="video-short-title">
        ...              <a  id="video-short-title-LWLtQFk61pY" rel="nofollow" 
        ...              title="Candy Candy(Dolce Candy) 115 Ultimo episodio 2/2" 
        ...              href="/watch?v=LWLtQFk61pY&feature=channel_page">Candy Candy(Dolce Candy) 115 Ult...</a>
        ...              </div>'''
        >>> name, id = c._getMetadata(html).next()
        >>> name
        u'Candy Candy(Dolce Candy) 115 Ultimo episodio 2/2'
        >>> id
        u'LWLtQFk61pY'
        """
        
        soup = BeautifulSoup(html)
        allDivs = soup.findAll('div', { "class" : "video-short-title"})
        for div in allDivs:
            anchor = div.a
            id = anchor['id'].split('-')[3]
            name = anchor['title']
            yield name, id
            
    def _getPWN(self, id):
        pwn_url = PWN % id
        html = urllib.urlopen(pwn_url)
        soup = BeautifulSoup(html)
        table = soup.find('table')
        if table:
            a = table.findAll('a')
            anchor = a[2] # the third link :)
            url = anchor['href']
            return url
        return None
        
    def _download(self, name, url):
        """
        >>> c = Candy('user')
        >>> c._download('google', 'http://www.google.com')
        downloading google
        downloaded google: but not sure about size
        >>> os.remove('%s/%s.mp4' % (c.path, 'google'))

        """
        if url:
            fileobject = urllib.urlopen(url)
            print 'downloading %s' % (name, )
            filename = '%s/%s.mp4' % (self.path, name.replace('/','-'))
            urllib.urlretrieve(url,filename) 
            complete = self._download_complete(fileobject, filename)
            if complete == self.KO:
                print 'the file %s is not fully downloaded' % (name, )
                os.remove(filename)
                self._download(name, url)
            elif complete == self.OK:
                print 'downloaded %s' % (name, )
                self.nr_downloaded +=1
            else:
                print 'downloaded %s: but not sure about size' % (name, )
                self.nr_downloaded +=1
            
    def _download_complete(self, fileobject, filename):
        """
        >>> c = Candy('user')
        >>> c._download('google', 'http://www.google.com')
        downloading google
        downloaded google: but not sure about size
        >>> c._download_complete(urllib.urlopen('http://www.google.com'), '%s/%s.mp4' % (c.path, 'google'))
        2
        
        >>> os.remove('%s/%s.mp4' % (c.path, 'google'))

        """
        if fileobject.info().getheaders('Content-Length'):
            if string.atol(fileobject.info().getheaders('Content-Length')[0]) == os.stat(filename).st_size:
                return self.OK
            else: 
                return self.KO
        else: 
            return self.CANNOT_SAY
        

def _test():
    import doctest
    doctest.testmod()
    #doctest.testfile('../../README.txt')

if __name__ == "__main__":
    _test()