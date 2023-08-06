from urllib import urlencode
from urllib2 import urlopen, Request
import settings

baseurl = settings.text_baseurl

class Text:
    def places(self,doc,params=None):
        values = {}
        if params is not None:
            values = params
        if 'gazetteer' not in values:
            values['gazetteer'] = 'geonames'
        if 'type' not in values:
            values['type'] = 'plain'
        values['document'] = doc
        data = urlencode(values)
        req = Request(baseurl,data)
        res = urlopen(req)
        return res.read()


