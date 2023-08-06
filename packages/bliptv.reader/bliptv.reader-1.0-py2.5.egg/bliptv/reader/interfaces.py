from zope.interface import Interface, Attribute

class IShow(Interface):
    
    episodes = Attribute("""list of attributes: IEpisodeList""")
    showname = Attribute("""short name of show, as in <showname>.blip.tv""")
    

class IEpisodes(Interface):
    """holds a virtual list of episodes"""
    
    all = Attribute("""all episodes in one big list, return IEpisodeList""")
    page = Attribute("""a virtual list of pages, returns [IEpisodePage]""")
    

class IEpisodeList(Interface):
    """a list of IEpisode objects"""
    
    
class IEpisodePage(IEpisodeList):
    """an IEpisodeList but in page form
    
    this means it has additional functions for paging
    """
    
    next = Attribute("""next page which follows, None if it's the last one""")
    prev = Attribute("""previous page, None if it's the first one""")
    
class IEpisode(Interface):
    """an episode"""
    
    title = Attribute("""the title of the show""")
    url = Attribute("""the url of the show""")