
from urllib2 import urlopen
import elementtree.ElementTree as etree

class Enclosure(object):
    """holds a version of an episode"""
    
    def __init__(self, url, filetype=None, filesize=None, height=None, width=None):
        self.url = url
        self.filetype = filetype
        if filesize is not None:
            self.filesize = int(filesize)
        else:
            self.filesize = None
        if height is not None:
            self.height = int(height)
        else:
            self.height = None
        if width is not None:
            self.width = int(width)
        else:
            self.width = None

class Episode(object):
    """an episode"""
    
    def __init__(self, show, episode):        
        self.url = episode.find("link").text
        self.title = episode.find("title").text
        self.rating = episode.find("{http://blip.tv/dtd/blip/1.0}contentRating").text
        self.pureDescription = episode.find("{http://blip.tv/dtd/blip/1.0}puredescription").text
        self.description = episode.find("description").text
        keywords = episode.find("{http://search.yahoo.com/mrss/}keywords").text.split(",")
        self.keywords = [k.strip() for k in keywords]
        files = episode.findall('{http://search.yahoo.com/mrss/}group/{http://search.yahoo.com/mrss/}content')
        self.enclosures={}
        for f in files:
            _type = f.get("type")
            url = f.get("url")
            filesize = f.get("fileSize")
            height = f.get("height")
            width = f.get("width")
            enclosure = Enclosure(url, _type, filesize, height, width)
            self.enclosures[_type] = enclosure

class EpisodePage(object):
    """a page of episodes"""
        
    def __init__(self, show, nr):
        """initialize an episode page"""
        self.show = show
        self.nr = nr
        url = self.show.url+"/?sort=date;date=;view=archive;user=%s;nsfw=dc;s=posts;page=%s;pagelen=10;skin=rss" %(self.show.showname,nr)
        xml = urlopen(url)
        self.parser = etree.parse(xml)
        root = self.parser.getroot()
        
        # now find the episodes via XPath
        episodes = root.findall('channel/item')
        self.episodes = []
        for episode in episodes:
            self.episodes.append(Episode(show, episode))

    @property
    def next(self):
        """return the next page of episodes"""
        return EpisodePage(self.show, self.nr+1)
        
    @property
    def prev(self):
        if self.nr==1: return None
        return EpisodePage(self.show, self.nr-1)
        
    # make this a container type
    def __len__(self):
        return len(self.episodes)

    def __getitem__(self, item):
        return self.episodes[item]
        
    def __iter__(self):
        return iter(self.episodes)


class Pages(object):
    """a virtual list for pages"""
    
    def __init__(self, show):
        """initialize this adapter like wrapper"""
        self.show = show
    
    def __getitem__(self,nr):
        """return the identified page"""
        return EpisodePage(self.show, nr)


class Episodes(object):
    
    def __init__(self, show):
        self.show = show
    
    @property
    def pages(self):
        """return a paged view on episodes"""
        return Pages(self.show)

class Show(object):
    """a blip.tv show"""
        
    def __init__(self,showname):
        self.showname = showname        
        
    @property
    def url(self):
        """return the url of this show"""
        return "http://%s.blip.tv" %self.showname
    
    @property
    def episodes(self):
        """return an episode list object"""
        return Episodes(self)
        
    