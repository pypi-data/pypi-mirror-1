import urllib, urllib2
from d9t.json.parser import JsDomParser

class GoogleDirections(object):
    """
        This implements a nice api for a google maps call.

        Usage
        =====
        >>> api.GoogleDirections("your-key").query("ulm","hamburg").distance

        The whole result will be in
        >>> api.GoogleDirections("your-key").query("ulm","hamburg").result
    """

    url="http://maps.google.com/maps/nav?key=%s&output=js&doflg=ptj&q=from%%3A%s%%20to%%3A%s"

    def __init__(self, key):
        self.key = key
        self.result = None
        self.start = None
        self.destination = None

    def query(self, start, destination, headers=None):
        if self.result and self.start==start and self.destination==destination:
            return self
        if type(start) is unicode:
            start = start.encode("utf-8")
        if type(destination) is unicode:
            destination = destination.encode("utf-8")
        self.start = start
        self.destination = destination
        url = self.url % (
            self.key,
            urllib.quote(start),
            urllib.quote(destination),
        )
        if not headers:
            headers = {}
        req = urllib2.Request(url, None, headers)
        res = urllib2.urlopen(req).read()
        # google sends as iso-8859-1. Recode.
        res = res.decode("iso-8859-1")
        parser = JsDomParser(res)
        self.result = parser.parse()
        return self

    @property
    def status(self):
        """
            Returns the status of the query. You really should check
            if this is != 200, because you won't get any other results
            otherwise.
        """
        return self.result["Status"]["code"]

    @property
    def distance(self):
        """
            Returns the driving distance in meters.
        """
        return self.result["Directions"]["Distance"]["meters"]

    @property
    def startAddress(self):
        """
            Returns a address dict
        """
        ret = {}
        return self.result["Placemark"][0]

    @property
    def destinationAddress(self):
        return self.result["Placemark"][1]

