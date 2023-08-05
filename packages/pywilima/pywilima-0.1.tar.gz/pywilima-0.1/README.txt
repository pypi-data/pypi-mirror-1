This is a library to use the bus schedule lookup site at:

 http://lprwilima.lappeenranta.fi:8080

The library uses ClientForm and BeautifulSoup; you'll need
to install those libraries first.

Besides a small library, there's a wsgi app for
serving the bus stops as xml.

Some items on the list to be done later:

 - cache the lookup results

 - serve the full schedule info via a RESTful "api"

 - implement a mobile client for Series60
