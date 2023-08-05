import sys, logging, time

from urllib2 import urlopen, HTTPError, HTTPCookieProcessor, install_opener, build_opener
from cookielib import CookieJar
from ClientForm import ParseResponse
from BeautifulSoup import BeautifulSoup

wilimaurl = "http://lprwilima.lappeenranta.fi:8080/traveller/matkainfo"

busns = "http://lprwilima.lappeenranta.fi/busstops/2006/04"


def install_cookieopener():
   # Install opener that handles cookies
   cj = CookieJar()
   processor = HTTPCookieProcessor(cj)
   install_opener(build_opener(processor))


def getServiceForm(url=wilimaurl):
   try:
      response = urlopen(url)
   except HTTPError, response:
      raise Exception("Could not retrieve bus service URL", response)
   forms = ParseResponse(response, backwards_compat=False)
   return forms[0]


def parseDepartureResultsView(response):
   "return [(lineno, linename), (leaves_from, travelday, leaves_at), (arrives_to, arrival_day, arrives_at)]"
            
   departurespage = response.read()
   del response
   soup = BeautifulSoup(departurespage)
   table = soup("table",{"width":"630", "cellspacing":"1"})[0]
   departures = []
   for trow in table(lambda(x):x.name=="tr" and len(x)>3)[1:]:
      lineno = trow.td.font.a.string.strip()
      linename, departure, arrival, comment = trow("td",{"height":"21"})
      linename = linename.font.string.strip()
      departure = departure.font.strong.string.strip()
      travelday, leaves_at = departure.split()[:2]
      leaves_from = " ".join(departure.split()[2:])
      
      arrival = arrival.font.strong.string.strip()
      arrival_day, arrives_at = arrival.split()[:2]
      arrives_to = " ".join(arrival.split()[1:])
      
      departure = (
         (lineno, linename),
         (leaves_from, travelday, leaves_at),
         (arrives_to, arrival_day, arrives_at)
      )
      departures.append(departure)
      
   return departures


def getBusStops(url=wilimaurl):
   "return all bus stops as a (name:value) dict"
   form = getServiceForm()
   try:
      # we assume all stops are used for both departure and arrival
      stops_source = form.find_control("lahtopaikka")
   except:
      raise Exception("no stop source element found")
   stops = [(stop.name, stop.attrs["label"].strip()) for stop in stops_source.items]
   return stops


def getDepartures(stop_from, stop_to, departure_time=None, departures=3):
   "get next departures"
   
   if not departure_time:
      departure_time = time.localtime()[:5]
         
   year, month, day, hour, minute = [str(t) for t in departure_time]
   
   form = getServiceForm()
   form.find_control("lahtopaikka").get(stop_from).selected=True
   form.find_control("maarapaikka").get(stop_to).selected=True
   form["vuosi"] = year
   form["kuukausi"] = month
   form["paiva"] = day
   form["tunnit"] = hour
   form["minuutit"] = minute
   
   # not being used right now - how can I set a hidden form field?
   #form["maxtuloksia"] = str(departures)
   
   submit = form.find_control("submit")
   form.method = "GET"
   request = form.click()

   try:
       response = urlopen(request)
       del request
   except HTTPError, response2:
      raise Exception("Could not get timetables", response)
   
   return parseDepartureResultsView(response)
   
   
if __name__=="__main__":
   
   stop_from = ("PA1023","Kivisalmi ( Kivistonkatu )")
   stop_to = ("PA25","Keskuspuisto ( Valtakatu )")
   
   departures = getDepartures(stop_from=stop_from[0], stop_to=stop_to[0])
   
   for  iline, ifrom, ito in departures:
      print "-------------------------"
      print "line: %s - %s" % iline
      #print "from: %s" % ifrom[0]
      print "leaves at: %s %s" % ifrom[1:] 
      #print "to: %s" % ito[0]
      print "arrives at: %s %s" % ito[1:]
