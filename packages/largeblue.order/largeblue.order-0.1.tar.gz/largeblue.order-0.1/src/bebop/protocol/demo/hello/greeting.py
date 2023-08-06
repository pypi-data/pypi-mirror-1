from zope.publisher.browser import BrowserView 

class Greeting(BrowserView): 

    def __call__(self): 
        return "Hello %s" % self.context.name() 
