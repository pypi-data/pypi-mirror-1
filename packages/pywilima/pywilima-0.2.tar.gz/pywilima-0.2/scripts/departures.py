#!python
# -*- encoding:utf-8 -*-
import sys, os, time
from wsgiref.handlers import CGIHandler
from StringIO import StringIO
import pywilima

queryparts = ("prefix", "from_stop", "to_stop", "year", "month", "day", "hour", "minute")


def showForm(response, stops):
   "a simple search form"
   response.write("<form action=''>")
   options = "\n".join(['<option value="%s">%s</option>' % s for s in stops])
   response.write('<select name="stops">%s</select' % options)
   response.write("</form")

   
def addStops(response, stops, path):
   "add the HTML with bus stop info"
   response.write("<ul>\n")
   for code, label in stops:
      link = """<a href="%s/%s">%s</a>""" % (path, code, label)
      response.write("""  <li w:code="%s" w:label="%s">%s</li>\n""" % (code, label, link))
   response.write("</ul>\n")

   
def parsePath(path):
   "get a dict out of restful URI, with request attribute names"
   items = path.split("/")
   
   data = {}
   for i, p in enumerate(queryparts):
      try:
         data[p] = items[i+1]
      except:
         break
   
   return data
   

def addNextDepartures(response, stop_from, stop_to):
   ""
   fcode, flabel = stop_from
   tcode, tlabel = stop_to
   departures = pywilima.getDepartures(stop_from=fcode, stop_to=tcode)
   out = response.write
   
   out("<h2>%s - %s</h2>" % (flabel, tlabel))
   out("<p><b>kello %02d:%02d</b></p>" % time.localtime()[3:5])
   out("<ol>\n")
   
   for  iline, ifrom, ito in departures:
      out("<li>linja %s - <b>%s</b> (arrives at %s)</li>" % (str(iline[0]), str(ifrom[2]),str(ito[1])))
   out("</ol>")

   
def getStops():
   "get stops from disk or the wilima service"
   try:
      f = open("stops.txt")
      for l in f:
         stops.append(l.split('|'))
      f.close()
   except:
      stops = pywilima.getBusStops()
      f = open("stops.txt", "w")
      for stop in stops:
         f.write("%s|%s\n" % stop)
      f.close()
   return stops
   

def getLabelForCode(stops, code):
   return [s[1] for s in stops if s[0]==code][0]

   
def scheduleapp(environ, start_response):
   "the WSGI app"
   query = environ["QUERY_STRING"]
   path = environ["SCRIPT_NAME"] + environ["PATH_INFO"]
   path = path.rstrip("/")

   status = "200 OK"
   response_headers = [("Content-Type", "text/html"),]
   start_response(status, response_headers)
   
   response = StringIO()
   response.write("""<html xmlns:w="%s">\n<head>\n""" % pywilima.wilimans)

   stops = getStops()
   
   pathdata = parsePath(environ["PATH_INFO"])
   if "prefix" in pathdata and pathdata["prefix"] == "stops":
      steps = len(pathdata)
      
      if steps ==1:
         response.write("<title>%s</title\n</head>\n<body>\n" % "Lähtöpysäkit")
         try:
            path = "/".join((path,pathdata["from_stop"]))
         except:
            pass
         addStops(response, stops, path)

      elif steps == 2:
         response.write("<title>%s</title\n</head>\n<body>\n" % "Kohdepysäkit")
         addStops(response, stops, path)
         
      elif steps == 3:
         fromcode = pathdata["from_stop"]
         tocode = pathdata["to_stop"]
         fromlabel = getLabelForCode(stops, fromcode)
         tolabel = getLabelForCode(stops, tocode)
         response.write("<title>%s - %s</title\n</head>\n<body>\n" % (fromlabel, tolabel))
         addNextDepartures(response, (fromcode, fromlabel), (tocode, tolabel))
         
   response.write("</body>\n</html>")

   response.seek(0)
   return  response.read()


if __name__=="__main__":
   CGIHandler().run(scheduleapp)
