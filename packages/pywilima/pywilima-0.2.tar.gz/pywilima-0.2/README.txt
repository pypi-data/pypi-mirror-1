This is a library to use the bus schedule lookup site at:

 http://lprwilima.lappeenranta.fi:8080

The library uses ClientForm and BeautifulSoup; you'll need
to install those libraries first.

Besides a small library, there's a wsgi app for
serving the bus stops as xml - see the "scripts" dir.

The app gives browser access to getting five next
departures. Just navigate to "/stops", click
departure stop, then click on arrival stop
and you will be shown the next five departures.

Note that you can bookmark the result URL -
thus giving an easy access to often-used
departure info.

Known problems:

 - The library only handles direct routes;
   if you select departure and arrival so 
   that there's a bus change involved,
   the system will fail.
   
Some items on the list to be done later:

 - implement a mobile client for Series60
