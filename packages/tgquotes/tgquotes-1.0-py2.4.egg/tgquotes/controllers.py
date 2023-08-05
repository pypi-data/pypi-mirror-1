import turbogears
from turbogears import controllers, expose, redirect
import urllib, simplejson

from tgquotes import json

class QuoteController(controllers.Controller):
    @expose('json')
    def index(self):
        import model
        return dict(quotes=model.Quote.random())

    @expose('json')
    def default(self, *args, **kw):
        import model
        try:
            num = int(args[0])
            return dict(quotes=model.Quote.random(num))
        except ValueError, TypeError:
            return dict(quotes=[])

class QuoteProxyController(controllers.Controller):
    def __init__(self, host, *args, **kw):
        self.host = host
        super(controllers.Controller, self).__init__(*args, **kw)

    @expose('json')
    def index(self):
        quotes = urllib.urlopen(self.host)
        return dict(quotes=simplejson.load(quotes)['quotes'])

    @expose('json')
    def default(self, *args, **kw):
        try:
            quotes = urllib.urlopen('%s/%s' % (self.host, args[0]))
            quotes = simplejson.load(quotes)['quotes']
        except ValueError:
            quotes = []
        return dict(quotes=quotes)
                                

class Root(controllers.RootController):
    @expose(template="tgquotes.templates.welcome")
    def index(self):
        import time
        return dict(now=time.ctime())

    quote = QuoteController()
