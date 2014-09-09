from google.appengine.ext import ndb
from webapp2_extras import security

class Author(ndb.Model):
	tumblr_token = ndb.StringProperty()
	tumblr_username = ndb.StringProperty()

class Story(ndb.Model):
	author = ndb.KeyProperty(kind='Author')
	title = ndb.StringProperty()
	tumblr_post_id = ndb.StringProperty()

class Chapter(ndb.Model):
	story = ndb.KeyProperty(kind='Story')
	number = ndb.IntegerProperty(default=0)
	tumblr_post_id = ndb.StringProperty()