"""
Extract client information from http user agent
The module does not try to detect all capabilities of browser in current form (it can easily be extended though).
Aim is 
    * fast 
    * very easy to extend
    * reliable enough for practical purposes
    * and assist python web apps to detect clients.
"""
import sys

class DetectorsHub(dict):
    _known_types = ['os', 'dist', 'flavor', 'browser']
    def __init__(self, *args, **kw):
        dict.__init__(self, *args, **kw)
        for typ in self._known_types:
            self.setdefault(typ, [])
        self.registerDetectors()
    def register(self, detector):
        if detector.info_type not in self._known_types:
            self[detector.info_type] = [detector]
            self._known_types.insert(detector.order, detector.info_type)
        else:
            self[detector.info_type].append(detector)
    def reorderByPrefs(self, detectors, prefs):
        if prefs == None:
            return []
        elif prefs == []:
            return detectors
        else:
            prefs.insert(0, '')
            return sorted(detectors, key=lambda d: d.name in prefs and prefs.index(d.name) or sys.maxint)
    def __iter__(self):
        return iter(self._known_types)
    def registerDetectors(self):
        detectors = [v() for v in globals().values() if DetectorBase in getattr(v, '__mro__', [])]
        for d in detectors:
            if d.can_register:
                self.register(d)

class DetectorBase(object):
    name = "" # "to perform match in DetectorsHub object"
    info_type = "override me"
    result_key = "override me"
    order = 10 # 0 is highest
    look_for = "string to look for"
    can_register = False
    prefs = dict() # dict(info_type = [name1, name2], ..)
    version_splitters = ["/", " "]
    _suggested_detectors = None
    def __init__(self):
        if not self.name:
            self.name = self.__class__.__name__
        self.can_register = (self.__class__.__dict__.get('can_register', True))
    def detect(self, agent, result):
        # -> True/None
        if self.checkWords(agent):
            result[self.info_type] = {self.name : dict()}
            version = self.getVersion(agent)
            if version:
                result[self.info_type][self.name]['version'] = version
            return True
    def checkWords(self, agent):
        # -> True/None
        if self.look_for in agent:
            return True
    def getVersion(self, agent):
        # -> version string /None
        return agent.split(self.look_for + self.version_splitters[0])[-1].split(self.version_splitters[1])[0].strip()

class OS(DetectorBase):
    info_type = "os"
    can_register = False
    version_splitters = [";", " "]

class Dist(DetectorBase):
    info_type = "dist"
    can_register = False

class Flavor(DetectorBase):
    info_type = "flavor"
    can_register = False

class Browser(DetectorBase):
    info_type = "browser"
    can_register = False

class Macintosh(OS):
    look_for = 'Macintosh'
    prefs = dict(dist = None)
    def getVersion(self, agent): pass

class Firefox(Browser):
    look_for = "Firefox"

class Konqueror(Browser):
    look_for = "Konqueror"

class Opera(Browser):
    look_for = "Opera"

class MSIE(Browser):
    look_for = "MSIE"
    name = "Microsoft Internet Explorer"
    version_splitters = [" ", ";"]

class Galeon(Browser):
    look_for = "Galeon"

class Linux(OS):
    look_for = 'Linux'
    prefs = dict(browser = ["Firefox"], dist=["Ubuntu"], flavor=None)
    def getVersion(self, agent): pass

class Macintosh(OS):
    look_for = 'Macintosh'
    prefs = dict (dist = None, flavor = ['MacOS'])
    def getVersion(self, agent): pass

class MacOS(Flavor):
    look_for = 'Mac OS'
    prefs = dict (browser = ['Firefox', 'Opera', "Microsoft Internet Explorer"])
    def getVersion(self, agent):
        return agent.split('Mac OS')[-1].split(';')[0].strip()

class Windows(OS):
    look_for = 'Windows'
    prefs = dict (browser = ["Microsoft Internet Explorer", 'Firefox'], dict = None, flavor = None)
    def getVersion(self, agent):
        return agent.split('Windows')[-1].split(';')[0].strip()

class Ubuntu(Dist):
    look_for = 'Ubuntu'
    version_splitters = ["/", " "]
    prefs = dict (browser = ['Firefox'])

detectorshub = DetectorsHub()

def detect(agent):
    result = dict()
    prefs = dict ()
    _suggested_detectors = []
    for info_type in detectorshub:
        if not _suggested_detectors:
            detectors = detectorshub[info_type]
            _d_prefs = prefs.get(info_type, [])
            detectors = detectorshub.reorderByPrefs(detectors, _d_prefs)
            if "detector" in locals():
                detector._suggested_detectors = detectors
        else:
            detectors = _suggested_detectors
        for detector in detectors:
            #print "detector name: ", detector.name
            if detector.detect(agent, result):
                prefs = detector.prefs
                _suggested_detectors = detector._suggested_detectors
                break
    return result

def test():
    import datetime
    execfile("testdata", globals())
    then = datetime.datetime.now()
    for agent in agents * 10:
        print agent
        print detect(agent)
    #s = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-GB; rv:1.9.0.10) Gecko/2009042315 Firefox/3.0.10"
    #print s
    #print detect(s)
    now = datetime.datetime.now()
    print len(agents), "analysed in ", now - then

if __name__ == '__main__':
    test()
    print
    #import cProfile
    #cProfile.run('test()')
