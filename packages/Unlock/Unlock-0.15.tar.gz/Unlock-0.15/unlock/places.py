import urllib2
from urllib import urlencode
from warnings import warn
import settings

baseurl = settings.places_baseurl 

class Unlock:
    def __init__(self,key=None,gazetteer=None):
        self.apikey = key
        self.gazetteer = gazetteer

class Places(Unlock):
    
    def ask_service(self,request,params):
        if self.apikey is not None:
            params['key'] = self.apikey
        url = baseurl+request+'?'+urlencode(params)
        try:
            r = urllib2.urlopen(url)
            return r.read()
        except urllib2.HTTPError, e:
            warn(e)
            return None

    def nameSearch(self,name=None,format=None):
        """Look up a name, get back short description in format
        one of ['json','kml',?]"""

        params = {'name':name,'format':format, 'gazetteer':self.pick_gazetteer()}   
        results = self.ask_service('nameSearch',params)
        return results

    def spatialNameSearch(self,name=None,format=None,minx=None,miny=None,maxx=None,maxy=None,operator=None):
        """Look up a name, get back short description in format
        one of ['json','kml',?]"""

        if operator is None: operator = 'within'

        params = {'name':name,'format':format, 'gazetteer':self.pick_gazetteer(),'minx':minx,'maxx':maxx,'miny':miny,'maxy':maxy,'operator':operator}

        return self.ask_service('spatialNameSearch',params)        


    def nameAndFeatureSearch(self,name=None,featureType=None,format=None):
        """Look up a name but limit results by specified feature type(s)?"""

        params = {'name':name,'format':format,'featureType':featureType,'gazetteer':self.pick_gazetteer()}
        return self.ask_service('nameAndFeatureSearch',params)

    def featureTypes(self,superclass=None):
        """Is this written yet."""
        return self.ask_service('featureTypes')
        
    def footprintLookup(self,id=None,format=None):
        """Given an identifier get back a shape (if one is available)"""
        params = {'gazetteer':self.pick_gazetteer(),'identifier':id,'format':format}

        return self.ask_service('footprintLookup',params)
         
        #return r.read()
                                                                 

    def pick_gazetteer(self,gazetteer=None):
        """Choose geonames by default, if a gazetteer was not specified.
        Optionally pass in a gazetteer to use here.
        """
        if gazetteer is not None:
            self.gazetteer = gazetteer
        if self.gazetteer is None:
            if self.apikey is not None:
                self.gazetteer = 'os'    
            else:
                self.gazetteer = 'geonames'
        return self.gazetteer

    


if __name__ == '__main__':

    p = Places(key=None)
    output = p.nameSearch(name='Dunfermline',format='json')
    print output         
    
