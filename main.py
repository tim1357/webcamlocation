from flask import Flask,jsonify,request,render_template,redirect, url_for,Response

import logging
from google.appengine.ext import ndb
import numpy as np
from time import time 
from furllib2 import urlopen
from urllib import quote 
from json import dumps
from google.appengine.api import images

app = Flask(__name__)


#Each pixel has an intensity in [0,255]
INTENSITIES = np.arange(256).T

#Number of samples taken per day
NUM_SAMPLES = 24*(60/5)

#Maximum number of bytes to download from a webcam before giving up
MAX_BYTES=1024*1024*5

#Number of bytes to download from webcam at once
BATCH_BYTES = 4096


class Session(ndb.Model):
  """Models an individual Guestbook entry with content and date."""
  url = ndb.StringProperty()
  dates = ndb.PickleProperty()
  vals = ndb.PickleProperty()
  complete = ndb.BooleanProperty()
  err = ndb.StringProperty()
  @property
  def json(self):
      return dumps({'dates':self.dates,'vals':self.vals})
  

def get_key_if_any(url):
    '''Given a url, find the corresponding session'''
    q=Session.query(Session.url==url)
    return q.get()

def get_all_active():
  '''Simple query to return all Sessions that have not 
  yet finished their 24 hour observation period'''
  return Session.query(Session.complete==False)


def get_frame(url):
  '''Download a frame of one url'''
  r=urlopen(url)
  i=0
  s=''
  #First we wait untill a fresh frame.
  while i*BATCH_BYTES < MAX_BYTES:
    i+=1
    l=r.read(BATCH_BYTES)
    #When we find the begining of a frame...
    if '\xff\xd8' in l:
      if '\xff\xd9' not in l:
        s+=l[l.index('\xff\xd8'):]
        break
      else:
        #Case when there is the end of the frame also in this batch
        return l[l.index('\xff\xd8'):l.index('\xff\xd9')+2]

  #Now we read untill the end of the frame
  while i*BATCH_BYTES < MAX_BYTES:
    i+=1
    l=r.read(BATCH_BYTES)
    if '\xff\xd9' not in l:
      s+=(l)
    else:
      return s+l[:l.index('\xff\xd9')+2]
  raise RuntimeError("Does not work with image sizes >= 1MB")

def get_intensity(image):
  '''Take an image (bytes of an image) and find the average
  pixel intensity from [0,1]'''
  i=images.Image(image)
  #A nifty Google Image API function to get
  #a histogram of intensities. 
  r,g,b =images.Image(image).histogram()
  #Find sum red intensity
  r=np.asarray(r).dot(INTENSITIES)
  #now green
  g=np.asarray(g).dot(INTENSITIES)
  #blue
  b=np.asarray(b).dot(INTENSITIES)
  #dot these together with weights. I found these weight
  #that apparently represent a common greyscale filter.
  t = 0.2989 * r + 0.5870 * g + 0.1140 * b
  #Finally take the average
  return t/(225*i.height * i.width)


@app.route('/cronny')
def do_cron_jobs():
  for session in get_all_active():
        s='Working on %s...'%session.url
        try:
          i=get_intensity(get_frame(session.url))
          s+='got intensity %f...'%i
          session.dates.append(time())
          session.vals.append(i)
          s+='done, have recorded %d obs...'%len(session.vals)
          if len(session.vals)==NUM_SAMPLES:
            s+='we are done'
            session.complete=True
        except Exception, e:
          session.err=str(e)
          s+="Error processing %s, %s"%(session.url,str(e))
          s+='...got an error %s'%str(e)
          session.complete = True
        logging.info(s)
        session.put()
  return ''


@app.route('/')
def main_page():
    """Return a friendly HTTP greeting."""
    url=request.args.get('url')
    if not url:
      return render_template('landing.html')
    return url_page(url)

@app.route('/all/<num>')
def all(num):
  num=int(num)
  def g():
    for session in Session.query().fetch(num):
      if session.vals:
        yield "<a href='/?url=%s'> %d obs</a></br>"%(quote(session.url.encode('utf8')),len(session.vals))
  return Response(g())


@app.route('/url/<url>')
def url_page(url):
    sesh=get_key_if_any(url)
    if sesh:
        return existing_session(sesh)
    else:
        return new_session(sesh,url)

def new_session(sesh,url):
  new_sesh = Session(url=url,dates=[],vals=[],complete=False,err='')
  new_sesh.put()
  return render_template("requestpending.html",session=new_sesh)

def existing_session(sesh):
  return render_template("webcamlocation.html",session=sesh)
