#from django.db import models
from google.appengine.ext import db

class Guser(db.Model):
  email = db.StringProperty()
  sessions_no = db.IntegerProperty(default=0)

  def __str__(self):
    return '%s' %self.email

class Session(db.Model):
  user = db.ReferenceProperty(Guser)
  name = db.StringProperty()
  urls = db.StringProperty(multiline=True)
  created_on = db.DateTimeProperty(auto_now_add = 1)
  public = db.BooleanProperty(default=False)

  def __str__(self):
    return 'Session: %s' %self.name

