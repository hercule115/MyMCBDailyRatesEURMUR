#### Class Headers

class HttpHeaders():
    def __init__(self):

        # Request header prototype. Updated with specific request
        self._protoHeaders = {
            'Accept': 		'*/*',
            'Accept-Encoding': 	'gzip, deflate, br',
            'Accept-Language': 	'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 	'no-cache',
            'Connection': 	'keep-alive',
            'Pragma': 		'no-cache',
            'User-Agent': 	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36'
        }

        self._h = self._protoHeaders

    @property
    def headers(self):
        return self._h

    def setHeader(self, hdr, val):
        self._h[hdr] = val

    # Return header value if found
    def getHeader(self, hdr):
        try:
            val = self._h[hdr]
        except:
            return None
        return val
    
    def getCookie(self, cookie):
        for k,v in self._h.items():
            if k == 'Set-Cookie':
                cookies = v.split(';')
                for c in cookies:
                    try:
                        cc = c.split('=')
                    except:
                        myprint(1,'Skipping %s' % cc)
                        continue
                    if cc[0] == cookie:
                        return cc[1]
        return None
