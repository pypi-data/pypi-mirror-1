import os
import re
import StringIO
import pycurl

EMAIL_PATTERN = re.compile(r"([a-zA-Z0-9+_\-\.]+@[0-9a-zA-Z][.-0-9a-zA-Z]*.[a-zA-Z]+)",re.IGNORECASE)

def uniqify(seq, idfun=None):
    # order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result

class SimpleCurl(object):

    USER_AGENT = "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; EmbeddedWB 14.52 from: http://www.bsalsa.com/ EmbeddedWB 14.52; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.1; .NET CLR 1.0.3705; .NET CLR 3.0.04506.30)"

    def __init__(self):
        self.curl = pycurl.Curl()
        self.curl.setopt(pycurl.USERAGENT, SimpleCurl.USER_AGENT)
        self.cookie_filename = os.tempnam()
        self.curl.setopt(pycurl.COOKIEFILE, self.cookie_filename)
        self.curl.setopt(pycurl.FOLLOWLOCATION, True)
        self.curl.setopt(pycurl.COOKIEJAR, self.cookie_filename)

    def get_page(self, url):
        self.curl.setopt(pycurl.URL, str(url))
        contents = StringIO.StringIO()
        self.curl.setopt(pycurl.WRITEFUNCTION, contents.write)
        self.curl.perform()
        page = contents.getvalue()
        contents.close()
        return page

    def __del__(self):
        self.curl.close()
        os.remove(self.cookie_filename)

