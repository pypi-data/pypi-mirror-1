from unlock import Places, Text
import sys
sys.path.append('/home/jwalsh/unlock/py/src')
import unittest
import simplejson

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.name = 'Dunfermline'
        self.formats = ['json','kml','georss']  
    
    def testNameSearch(self):
        # simple name search
        p = Places() 
        xml = p.nameSearch(self.name)

    def testSpatialNameSearch(self):
        # bounding box name search
        bbox = {'minx' : -8, 'maxx': 1.5, 'miny' :54, 'maxy':62}
        places = Places()
        for f in self.formats:
            res = places.spatialNameSearch(minx=bbox['minx'],miny=bbox['miny'],maxx=bbox['maxx'],maxy=bbox['maxy'],name=self.name,format=f)
            if f == 'json':
                json = simplejson.loads(res)
                print json['totalResults']
        
    def testFootPrintSearch(self):
        # footprint search
        p = Places()
        res = p.nameSearch(name=self.name,format='json')        
        json = simplejson.loads(res)
        place = json['features'][0]
        foot = p.footprintLookup(id=place['id'])
   
    def testNameAndFeatureSearch(self):
        p = Places()
        res = p.nameAndFeatureSearch(name=self.name,featureType='populated place')
         
    def testText(self):
        t = Text()
        text = open('test.txt').read()
        res = t.places(text) 

    def testTextJSON(self):
        t = Text()
        text = open('test.txt').read()
        res = t.places(text,{'format':'json'})
if __name__ == '__main__':
    unittest.main()

