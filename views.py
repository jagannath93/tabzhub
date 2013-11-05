#!/usr/bin/env python

# Python imports
import datetime
import urllib
import httplib2
import logging
import cgi
import wsgiref.handlers
import pickle
import json
import os

# Google imports
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from apiclient import discovery
from oauth2client import appengine
from oauth2client import client
from google.appengine.api import memcache

import webapp2
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
        autoescape=True,
        extensions=['jinja2.ext.autoescape'])

CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

MISSING_CLIENT_SECRETS_MESSAGE = """
<h1>Warning: Please configure OAuth 2.0</h1>
<code>%s</code>.
""" % CLIENT_SECRETS

"""
http = httplib2.Http(memcache)
service = discovery.build("plus", "v1", http=http)
decorator = appengine.oauth2decorator_from_clientsecrets(
                CLIENT_SECRETS,
                scope=[
                  'https://www.googleapis.com/auth/plus.login',
                  'https://www.googleapis.com/auth/plus.me', 
                ],
                message=MISSING_CLIENT_SECRETS_MESSAGE)
"""

class Guser(db.Model):
  email = db.EmailProperty()
  name = db.StringProperty()
  registered_on = db.StringProperty()
  sessions_no = db.IntegerProperty(default=0)

  def __str__(self):
    return '%s' %self.email

class Session(db.Model):
  user = db.ReferenceProperty(Guser, required=True, collection_name='sessions_group')
  name = db.StringProperty(required=True)
  urls = db.TextProperty()
  created_on = db.DateTimeProperty(auto_now_add = 1)
  public = db.BooleanProperty(default=0)
  share = db.BooleanProperty(default=0)
  hits = db.StringProperty(default="0")

  def __str__(self):
    return 'Session: %s' %self.name


class Index(webapp2.RequestHandler):

  #@decorator.oauth_required
  def get(self):
    user = users.get_current_user()
    if user:
      print "User detected................ "+user.email()
      #me =  service.people().get(userId='me').execute()
      #guser = Guser.gql("Where gid = "+ str(user.user_id())).get()
      #if guser is None
      gusers = Guser.all()
      gusers.filter("email = ", user.email())
      guser = gusers.get()
      print guser
      tmp = {}
      if guser is None:
        print "guser is None."
        moment = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        guser = Guser(email = user.email(), name=user.nickname())
        guser.put()
      else:
        print "guser is already registered!!"
        sessions = Session.all().filter('user = ', guser)
        i = 1
        for session in sessions:
          sess = {}
          sess['urls'] = session.urls
          sess['created_on'] = session.created_on.strftime('%Y-%m-%dT%H:%M:%S')
          sess['public'] = session.public
          sess['name'] = session.name
          sess['share'] = session.share
          sess['hits'] = session.hits
          tmp[i] = sess
          i += 1
      #path = os.path.join(os.path.dirname(__file__), 'index.html')
      data = {
      'email': user.email(),
      'content': tmp,
      'logout_url': users.create_logout_url('/')
      }
      template = JINJA_ENVIRONMENT.get_template('index.html')
      self.response.write(template.render(data))
    else:
      self.redirect(users.create_login_url(self.request.uri))

class Fetch(webapp2.RequestHandler):

  #@decorator.oauth_required
  def get(self):
    user = users.get_current_user()
    if user:
      #me =  service.people().get(userId='me').execute()
      gusers = Guser.all()
      gusers.filter("email = ", user.email())
      guser = gusers.get()
      #guser = Guser.gql("Where gid = "+ user.user_id()).get()
      if guser is not None:
        #guser = Guser(gid=user.user_id(), name=user.nickname())
        #guser.put()
        sessions = Session.all().filter('user = ', guser)
        #print sessions
        #sessions = Session.gql("Where user = "+ guser).get()
        tmp = {}
        i = 1
        for session in sessions:
          sess = {}
          sess['urls'] = session.urls
          sess['created_on'] = session.created_on.strftime('%Y-%m-%dT%H:%M:%S')
          sess['public'] = session.public
          sess['name'] = session.name
          sess['share'] = session.share
          sess['hits'] = session.hits
          tmp[i] = sess
          i += 1
        self.response.out.write(json.dumps(tmp))
      else:  # Means user logged in to his google account but not have account yet in 'tabzhub'.
        self.response.out.write("Invalid: Register to 'tabZhub' first!!")
    else:
      self.redirect(users.create_login_url(self.request.uri))

class Save(webapp2.RequestHandler):

  #@decorator.oauth_required
  def post(self):
    user = users.get_current_user()
    if user:
      #guser_key = "dskfjksdljfkds"
      #_user = Guser.get_or_insert(guser_key, email = user.email())

      #me =  service.people().get(userId='me').execute()
      guser = gusers = Guser.all().filter("email = ", user.email()).get()
      if guser is not None:
        #guser = Guser(gid=user.user_id, name=user.nickname())

        #sessions = Session.gql("Where user = "+ guser).get()

        name = self.request.get('name')
        urls = self.request.get('urls')
        created_on = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')  #self.request.get('created_on')
        tmp = self.request.get('type')
        if tmp == 1:  # 0-private, 1 - public(default)
          type = True
        else:
          type = False
        session = Session(name=name, urls=urls, \
                  created_on=created_on, public = tmp)
        session.put()
        self.response.out.write("Saved Successfully :)")
      else: # Means user logged in to his google account but not have account yet in 'tabzhub'.
        self.response.out.write("Invalid: Register to 'tabZhub' first!!")
    else:
      self.redirect(users.create_login_url(self.request.uri))

application = webapp2.WSGIApplication([
        ('/fetch', Fetch),
        ('/save', Save),
        ('/index', Index),
        #(decorator.callback_path, decorator.callback_handler()),
        ], debug=True)

