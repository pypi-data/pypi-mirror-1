'''
Python module to access to sweetter application
Author: danigm <dani@danigm.net>

# how to use:

from pysweetter import Sweetter

s = Sweetter()
# Last 10 comments
comments = s.get_last_comments('index')

# Last danigm 10 comments
comments = s.get_last_comments('danigm')
# Last danigm and danigm's followings 10 comments
comments = s.get_last_followings('danigm')

for comment in comments:
    text = comment.sweet
    username = comment.user
    avatar_uri = comment.avatar
    created = comment.created
    print text, username, avatar_uri, created

# To post or set location you need to be authenticated
my_api_key = 'asdfasdfasfq23l4rq'
# Your apikey is in http://sweetter.net/edit_profile
s.autenticate(my_api_key)
s.post('my text in sweetter')

'''


from xmlrpclib import ServerProxy, Error
import datetime

class Comment:
    def __init__(self, sweet, user, avatar, created):
        self.sweet = sweet
        self.user = user
        self.avatar = avatar
        self.created = datetime.datetime.fromtimestamp(created)

class Sweetter:
    def __init__(self, apikey='', server='http://sweetter.net'):
        self.url = server
        self.server = ServerProxy(self.url + '/rpc/')
        self.apikey = apikey

    def autenticate(self, apikey):
        self.apikey = apikey

    def get_location(self, username):
        return self.server.get_location(username)

    def set_location(self, location):
        if not self.apikey: raise Exception("You aren't authenticated")
        ret = self.server.set_location(location, self.apikey)
        if ret < 0:
            raise Exception("Can't set location, I don't know why")

    def post(self, comment):
        if not self.apikey: raise Exception("You aren't authenticated")
        ret = self.server.post(comment, self.apikey)

        if ret < 0:
            raise Exception("Can't post, I don't know why")

    def get_last_comments(self, username):
        return self.get_something(username, self.server.get_last_comments)

    def get_replies(self, username):
        return self.get_something(username, self.server.get_replies)

    def get_last_followings(self, username):
        return self.get_something(username, self.server.get_last_followings)

    def get_TODO_list(self, username):
        return self.get_something(username, self.server.get_TODO_list)


    def get_something(self, username, func):
        lista = func(username)

        comments = [Comment(i['sweet'], i['user'], self.url +\
        i['avatar'], i['created']) for i in lista]

        return comments

