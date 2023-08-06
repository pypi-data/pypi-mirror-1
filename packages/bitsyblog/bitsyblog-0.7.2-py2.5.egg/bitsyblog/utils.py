"""utlity functions for bitsyblog"""

import datetime
import os
import urllib
import urllib2

timeformat = ( 'YYYY', 'MM', 'DD', 'HH', 'MM', 'SS' )

def validate_css(css):
    """use a webservice to determine if the argument is valid css"""    
    url = 'http://jigsaw.w3.org/css-validator/validator?text=%s'
    url = url % urllib.quote_plus(css)
    foo = urllib2.urlopen(url)
    text = foo.read()
    return not 'We found the following errors' in text

def date(datestamp):
    datestamp = os.path.split(datestamp)[-1]
    retval = []
    for i in timeformat:
        retval.append(int(datestamp[:len(i)]))
        datestamp = datestamp[len(i):]
    return datetime.datetime(*retval)

