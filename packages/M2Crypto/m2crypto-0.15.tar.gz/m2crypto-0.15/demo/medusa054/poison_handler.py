
import string
import whrandom

RESP_HEAD="""\
<HTML><BODY BGCOLOR=\"#ffffff\">
"""

RESP_MIDDLE="""
<h2>M2Crypto https server demonstration</h2>

This web page is generated by the "poison" http request handler. 
<br>
The links just go on and on and on...
<br><br>
"""

RESP_TAIL="""
</BODY></HTML>
"""

charset='012345678/90ABCDEFGHIJKLM/NOPQRSTUVWXYZabcd/efghijklmnopqrs/tuvwxyz'
numchar=len(charset)

def makepage(numlinks):

    title='<title>'
    for u in range(whrandom.randint(3, 15)):
        pick=whrandom.randint(0, numchar-1)
        title=title+charset[pick]
    title=title+'</title>'

    url='\r\n'
    numlinks=whrandom.randint(2, numlinks)
    for i in range(numlinks): 
        url=url+'<a href="/poison/'
        for u in range(whrandom.randint(3, 15)):
            pick=whrandom.randint(0, numchar-1)
            ch=charset[pick]
            if ch=='/' and url[-1]=='/':
                ch=charset[pick+1]
            url=url+ch
        url=url+'/">'
        for u in range(whrandom.randint(3, 15)):
            pick=whrandom.randint(0, numchar-1)
            url=url+charset[pick]
        url=url+'</a><br>\r\n'

    url=RESP_HEAD+title+RESP_MIDDLE+url+RESP_TAIL
    return url


class poison_handler:
    """This is a clone of webpoison - every URL returns a page of URLs, each of which 
    returns a page of URLs, each of _which_ returns a page of URLs, ad infinitum.
    The objective is to sucker address-harvesting bots run by spammers."""

    def __init__(self, numlinks=10):
        self.numlinks = numlinks
        self.poison_level = 0

    def match(self, request):
        return  (request.uri[:7] == '/poison')

    def handle_request(self, request):
        if request.command == 'get':
            request.push(makepage(self.numlinks))
        request.done()

