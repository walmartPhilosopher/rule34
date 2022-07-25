import requests
from json import JSONDecodeError

class Rule34Post():
    """
    Class to access attributes of a post
    """
    def __init__(self, post_dict:dict) -> None:
        self.preview_url = post_dict['preview_url']
        self.sample_url = post_dict['sample_url']
        self.file_url = post_dict['file_url']
        self.directory = post_dict['directory']
        self.hash = post_dict['hash']
        self.height = post_dict['height']
        self.width = post_dict['width']
        self.id = post_dict['id']
        self.image = post_dict['image']
        self.change = post_dict['change']
        self.owner = post_dict['owner']
        self.parent_id = post_dict['parent_id']
        self.rating = post_dict['rating']
        self.sample = post_dict['sample']
        self.sample_height = post_dict['sample_height']
        self.sample_width = post_dict['sample_width']
        self.score = post_dict['score']
        self.tags = post_dict['tags']

class Rule34Cache():
    """
    Class to cache searches for easier access the second time
    """
    def __init__(self):
        self.id_cache = {}
        self.cid_cache = {}
        self.tags_cache = {}

    def insert_into_id(self, post, id):
        self.id_cache[id] = post

    def insert_into_cid(self, post_list, cid):
        self.cid_cache[cid] = post_list
    
    def insert_into_tags(self, post_list, tags):
        self.tags_cache[tags] = post_list
    
    def retrieve_from_id(self, id):
        try:
            return self.id_cache[id]
        except KeyError:
            return None

    def retrieve_from_cid(self, cid):
        try:
            return self.cid_cache[cid]
        except KeyError:
            return None
    
    def retrieve_from_tags(self, tags):
        try:
            return self.id_cache[tags]
        except KeyError:
            return None

class Rule34():
    """
    Base class for Wrapper. Used to access methods
    - search_by_id
    - search_by_change
    - search_by_tags
    - get_random
    - get_latest

    Optimal for use in discord bots/systems that will continually run without stopping
    Designed with a cache system to reduce result time for second searches
    """


    def __init__(self):
        self.POST_API = 'https://api.rule34.xxx/index.php?page=dapi&s=post&q=index'
        self.cache = Rule34Cache()
    
    def search_by_id(self, id:int) -> Rule34Post:
        """Searches https://rule34.xxx using Post ID

        Args:
            id (int): ID of the post you want to search

        Returns:
            Rule34Post
        
        Exceptions:
            - Post Not Found
        """

        if x := self.cache.retrieve_from_id(id) is not None:
            return x

        r = requests.get(self.POST_API, params={'id' : id, 'json' : 1})
        try:
            self.cache.insert_into_id(Rule34Post(r.json()[0]), id=id)
            return Rule34Post(r.json()[0])
        except JSONDecodeError:
            return print(f'Post with ID:{id} does not exist or has been deleted')

    def search_by_change(self, cid:int, limit:int=1000) -> list:
        
        """Searches https://rule34.xxx using Change ID

        Args:
            cid (int): Change ID of the post you want to search
            limit (int, optional): How many posts are returned. Defaults to 1000.

        Returns:
            list (Rule34Post): List of search results
        
        Exceptions:
            - Posts Not Found
        """
        if limit <= 0:
            return print('Limit must be greater than 0')

        if x := self.cache.retrieve_from_cid(cid) is not None:
            return x

        r = requests.get(self.POST_API, params={'cid' : cid, 'limit' : limit, 'json' : 1})
        try:
            self.cache.insert_into_cid([Rule34Post(post) for post in r.json()])
            return [Rule34Post(post) for post in r.json()]
        except JSONDecodeError:
            return print(f'Post with Change:{cid} does not exist or has been deleted')
    
    def search_by_tags(self, tags:str, limit:int=1000) -> list:
        """Searches https://rule34.xxx using Tags

        Args:
            tags (str): Tags you want to search
            limit (int, optional): How many posts are returned. Defaults to 1000.

        Returns:
            list (Rule34Post): List of search results
        
        Exceptions:
            - Post Not Found
        
        Tag Guide for https://rule34.xxx
        Tags with spaces in them are filled by underscores(_). Ex: `female penetrated` becomes `female_penetrated`
        `female penetrated` will result in rule34 displaying posts with tags `female` and `penetrated` as separate tags
        `female_penetrated` will result in rule34 displaying posts with `female_penetrated` as a single tag

        Tags with a hyphen(-) as their prefix are considered blacklisted tags and will be removed from search results.

        Make sure to not have the same tag blacklisted, i.e, a search `female_penetrated sex -female_penetrated` will give you 0 results
        """
        if limit <= 0:
            return print('Limit must be greater than 0')

        if x:= self.cache.retrieve_from_tags(tags) is not None:
            return x
        
        r = requests.get(self.POST_API, params={'tags' : tags, 'limit' : limit, 'json' : 1})
        try:
            self.cache.insert_into_tags([Rule34Post(post) for post in r.json()])
            return [Rule34Post(post) for post in r.json()]
        except:
            return print(f'Posts with Tags:{tags} does not exist.')
    
    def get_random(self, blacklist:str='', limit:int=1000) -> list:
        """
        Get a list of random posts from https://rule34.xxx

        Args:
            blacklist (str, optional): Tags you want to avoid. All tags need to have a hyphen(-) as their prefix
            limit (int, optional): How many posts are returned. Defaults to 1000.

        Returns:
            list (Rule34Post): List of search results
        """
        if limit <= 0:
            return print('Limit must be greater than 0')


        if x := self.cache.retrieve_from_tags(blacklist) is not None:
            return x
        
        r = requests.get(self.POST_API, params={'tags' : blacklist, 'limit' : limit, 'json' : 1})
        self.cache.insert_into_tags([Rule34Post(post) for post in r.json()])
        return [Rule34Post(post) for post in r.json()]            

    def get_latest(self) -> Rule34Post:
        """
        Returns latest post from https://rule34.xxx

        Returns:
            Rule34Post
        """
        return Rule34Post(requests.get(self.POST_API, params={'tags' : '', 'limit' : 1, 'json' : 1}).json()[0])