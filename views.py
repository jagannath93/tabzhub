# Python imports
import datetime
import iso8601
import urllib
import cgi
import wsgiref.handlers
import json
import os
# App imports
#import models
#from utils import *

# Google imports
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp import template
import webapp2

"""
class Guser(db.Model):
  email = db.StringProperty()
  sessions_no = db.IntegerProperty(default=0)

  def __str__(self):
    return '%s' %self.email
"""

class Session(db.Model):
 #user = db.ReferenceProperty(Guser)
  name = db.StringProperty()
  urls = db.TextProperty()
  #urls = db.StringProperty(multiline=True)
  user_id = db.StringProperty()
  created_on = db.DateTimeProperty(auto_now_add = 1)
  type = db.BooleanProperty(default=0)

  def __str__(self):
    return 'Session: %s' %self.name


class Index(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    print user
    if user:
      sessions = Session.all().filter('user_id = ', user.user_id())
      tmp = {}
      i = 1
      for session in sessions:
        sess = {}
        sess['urls'] = session.urls
        sess['created_on'] = session.created_on.strftime('%Y-%m-%dT%H:%M:%S')
        sess['type'] = session.type
        sess['name'] = session.name
        tmp[i] = sess
        i += 1
      path = os.path.join(os.path.dirname(__file__), 'index.html')
      data = {
      'email': user.email(),
      'nickname': user.nickname(),
      'content': tmp
      }
      self.response.out.write(template.render(path, {'data': data}))
    else:
      self.response.out.write("<a href='%s'>Signin with your google account</a>" %
          users.create_login_url('/'))

class Fetch(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    print user
    if user:
      #guser_key = "djshfkjsdhfsd sdf"
      #_user = Guser.get_or_insert(guser_key, email = user.email())
      sessions = Session.all().filter('user_id = ', user.user_id())
      tmp = {}
      i = 1
      for session in sessions:
        sess = {}
        sess['urls'] = session.urls
        sess['created_on'] = session.created_on.strftime('%Y-%m-%dT%H:%M:%S')
        sess['type'] = session.type
        sess['name'] = session.name
        tmp[i] = sess
        i += 1
      self.response.out.write(json.dumps(tmp))
    else:
      self.response.out.write("<a href='%s'>signout</a>" % users.create_logout_url('/'))
      # Redirect to google accounts login page.

class Save(webapp2.RequestHandler):
  def post(self):
    user = users.get_current_user()
    if user:
      #guser_key = "dskfjksdljfkds"
      #_user = Guser.get_or_insert(guser_key, email = user.email())
      name = self.request.get('name')
      urls = self.request.get('urls')
      created_on = datetime.datetime.now()  #self.request.get('created_on')
      tmp = self.request.get('type')
      if tmp is 1:  # 1-private, 0 - public(default)
        type = True
      else:
        type = False
      session = Session(name=name, urls=urls, user_id = user.user_id(), \
                created_on=created_on, type = type)
      session.put()
      self.response.out.write("Saved Successfully :)")
    else:
      self.response.out.write("<a href='%s'>Signin with your google account</a>" %users.create_login_url('/'))
      # Redirect to google accounts login page.

application = webapp2.WSGIApplication([
      ('/fetch', Fetch),
        ('/save', Save),
        ('/index', Index)
        ], debug=True)

