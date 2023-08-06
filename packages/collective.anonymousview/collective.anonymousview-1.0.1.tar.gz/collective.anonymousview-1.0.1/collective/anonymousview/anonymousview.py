from zope.interface import implements
from Products.Five.browser import BrowserView
from interfaces import IAnonymousView
from zope.app import zapi
import urllib2

class AnonymousView(BrowserView):
	implements(IAnonymousView)
	
	def __call__(self):
		url = zapi.absoluteURL(self.context, self.request)
		response = urllib2.urlopen(url)
		return response.read()