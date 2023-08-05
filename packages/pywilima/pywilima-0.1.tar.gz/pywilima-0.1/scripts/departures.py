#!python

import sys, os
from wsgiref.handlers import CGIHandler
from StringIO import StringIO

from pywilima import *


def addStops(response):
   response.write("<stops>")
   stops = getBusStops()
   for stop in stops:
      response.write("""<stop code="%s">%s</stop>""" % stop)
   response.write("</stops>")


tripxml = """
   <route>
      <line>
         <number>%s</number>
         <name>%s</name>>
      </line>

      <departure>
         <stop>%s</stop>
         <at>
            <date>%s</date>
            <time>%s</time>
         </at>
     </departure>
     
     <arrival>
         <stop>%s</stop>
         <at>
            <date>%s</date>
            <time>%s</time>
         </at>
      </arrival>
      
   </route>
"""

def scheduleapp(environ, start_response):
   ""
   query = environ["QUERY_STRING"]
   path = environ["PATH_INFO"]

   status = "200 OK"
   response_headers = [("Content-Type", "text/xml"),]
   start_response(status, response_headers)
   response = StringIO("""<?xml version="1.0" encoding="UTF-8"?>\n""")
   
   if path[1:6] == "stops":
      addStops(response)

   response.seek(0)
   return  response.read()


CGIHandler().run(scheduleapp)
