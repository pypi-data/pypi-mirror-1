from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from interfaces import ISplashImage, IStrapline

class SplashImage(ViewletBase):
	implements(ISplashImage)
	
	render = ViewPageTemplateFile('splash-image.pt')
	
	def getSplashImage(self):
		portal = self.portal_state.portal()
		try:
			bannerimg = portal['banner.jpg']
		except:
			bannerimg = ''
		return bannerimg
	
	
class Strapline(ViewletBase):
	implements(IStrapline)
	
	render = ViewPageTemplateFile('strapline.pt')
	def getStrapline(self):
		portal = self.portal_state.portal()
		try:
			strp = portal['strapline']()
		except:
			try:
				strp = portal.Title()
			except:
				strp = ''
		return strp
	
	
		
		
			