import webapp2
import json
import hashlib
import pytumblr
import urlparse
import code
import oauth2 as oauth
from webapp2_extras import sessions

from ignore_me import pokedex
from models import Author

request_token_url = 'http://www.tumblr.com/oauth/request_token'
authorize_url = 'http://www.tumblr.com/oauth/authorize'
access_token_url = 'http://www.tumblr.com/oauth/access_token'

class SessionHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

class TumblrLogin(SessionHandler):
	def get(self):
		consumer_key = pokedex['tumblr']['rokku']
		consumer_secret = pokedex['tumblr']['himitsu']
		consumer = oauth.Consumer(consumer_key, consumer_secret)
		client = oauth.Client(consumer)
		resp, content = client.request(request_token_url, "POST")
		request_token =  urlparse.parse_qs(content)
		token = request_token['oauth_token'][0]
		secret = request_token['oauth_token_secret'][0]
		self.session['oauth_token'] = token
		self.session['token_secret'] = secret
		go_to = '%s?oauth_token=%s' % (authorize_url, token)
		self.redirect(go_to)

class TumblrCallback(SessionHandler):
	def get(self):
		oauth_token = self.request.get('oauth_token')
		oauth_verify = self.request.get('oauth_verifier')

		token = oauth.Token(self.session.get('oauth_token'), self.session.get('token_secret'))
		token.set_verifier(oauth_verify)

		consumer_key = pokedex['tumblr']['rokku']
		consumer_secret = pokedex['tumblr']['himitsu']
		consumer = oauth.Consumer(consumer_key, consumer_secret)
		client = oauth.Client(consumer, token)

		resp, content = client.request(access_token_url, "POST")
		access_token = urlparse.parse_qs(content)

		user_token = access_token['oauth_token'][0]
		user_secret = access_token['oauth_token_secret'][0]

		new_client = pytumblr.TumblrRestClient(consumer_key,consumer_secret,user_token,user_secret)
		user_info = new_client.info()
		#self.response.write(user_info)
		
		username = str(user_info['user']['name'])
		a = Author.query(Author.tumblr_username==username).get()
		if a==None:
			a = Author(tumblr_token=user_token, tumblr_secret=user_secret, tumblr_username=username) 
		else:
			a = Author(tumblr_token=user_token, tumblr_secret=user_secret)
		a.put()

		self.redirect('/')
		

