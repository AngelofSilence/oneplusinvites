#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import logging
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext import db
from google.appengine.api import taskqueue
from google.appengine.api import taskqueue
from google.appengine.api import background_thread
import threading
import urllib2
import re
class MailReceiver(InboundMailHandler):
    def receive(self, mail_message): # When email gets received
        url = re.findall("https://invites.oneplus.net/confirm/[\w]{0,34}", mail_message.original.as_string()) # Parse the verification link
        if url != None: # If the link is found
          urllib2.urlopen(url[0]) # Open the link (HTTP Get) and verify the account
          m = Mule(mail=mail_message.to, verificationlink = url[0]) # Save it in the database
          m.put()
        
class Mule(db.Model):
    mail = db.StringProperty(required=True)
    verificationlink = db.StringProperty(required=True)
        
class MainHandler(webapp2.RequestHandler):
    def get(self):
         self.response.write("<h3>Your mules:</h3>")
         mules = Mule.all()
         mules.order('mail')
         for m in mules:
             self.response.write(m.mail + "<br>")
             self.response.write(m.verificationlink + "<br><br>")    
        
             
class ReVerify(webapp2.RequestHandler):    
    def get(self):
        global count
       # global debug
        count = 0
        v = Verify()
        mules = Mule.all()
        mc = mules.count()
        mules.order('mail')
        if(mules.count() > 0):
            for m in mules[0:500]:
                v.doit(m)
                count = count + 1       
            if(mc != mules.count()):
                text = str(count) + ' Mules Verified. ' #+ str(debug)
                self.response.out.write(text)
            else:
                self.response.out.write('hrm..')
        else:
            self.response.out.write('All Mules Verified.')
        
class Verify():        
    def doit(self, m):
        try:
            a = urllib2.urlopen(m.verificationlink)
            if a.getcode() == 200:
                m.delete()
                
        except Exception as e:
           # self.response.write(e)
            pass        

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/verify', ReVerify),
    MailReceiver.mapping()
], debug=True)
