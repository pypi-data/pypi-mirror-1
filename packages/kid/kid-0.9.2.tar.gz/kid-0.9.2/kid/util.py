class QuickTextReader(object):
    def __init__(self, text):
        self.text = text
        
    def read(self, amount):
        t = self.text
        self.text = ''
        return t
    
def xml_sniff(text):
    """Sniff text to see if it looks like XML.
    Return 1 if text looks like XML, otherwise return 0.
    """
    for x in text:
        if x in '\t\r\n ':
            continue
        elif x == '<':
            return 1
        else:
            return 0

from urllib import splittype
def open_resource(uri, mode='rb'):
    """Generic resource opener."""
    (scheme, rest) = splittype(uri)
    if not scheme or (len(scheme) == 1 and rest.startswith('\\')):
        return open(uri, mode)
    else:
        import urllib2
        return urllib2.urlopen(uri)

