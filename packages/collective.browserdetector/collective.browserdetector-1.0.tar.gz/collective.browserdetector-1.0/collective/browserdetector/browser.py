from zope.interface import implements
from Products.Five import BrowserView

from collective.browserdetector.interfaces import IBrowserDetector
from collective.browserdetector.i18n import cbdMessageFactory as _

class BrowserDetector(BrowserView):
    """ A helper browser view to get user agent detection results"""

    implements(IBrowserDetector)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._prtc = self.request.get('SERVER_PROTOCOL', u'')
        self._ua_id = self.request.get('HTTP_USER_AGENT',
                                        u'Detection not supported')
        self._ua = self._ua_id.lower()

    @property
    def agent(self):
        return self._ua_id

    def protocol(self):
        if self.isSecure:
            return _(u"Secure (${protocol})", mapping={'protocol': self._prtc})
        return _(u"Unsecure (${protocol})", mapping={'protocol': self._prtc})
    
    def platform(self):
        if self.isMac:
            return u'Mac (OS X)'
        elif self.isLinux:
            return u'Linux'
        elif self.isWindows:
            return u'Microsoft Windows'
        else:
            return _(u'Unknown')
    
    def browser(self):
        if self.isSafari:
            if self.isSafari3:
                return u'Safari 3.x'
            elif self.isSafari4:
                return u'Safari 4.x'
            else:
                return u'Safari'
        elif self.isGecko:
            if self.isGecko2:
                return u'Mozilla/Firefox 2.x'
            elif self.isGecko3:
                return u'Mozilla/Firefox 3.x'
            else:
                return u'Mozilla/Firefox'
        elif self.isIE:
            if self.isIE6:
                return u'Internet Explorer 6.x'
            elif self.isIE7:
                return u'Internet Explorer 7.x'
            elif self.isIE8:
                return u'Internet Explorer 8.x'
            else:
                return u'Internet Explorer'
        elif self.isChrome:
            return u'Chrome'
        elif self.isOpera:
            return u'Opera'
        else:
            return _(u'Unknown')

    @property
    def true_icon(self):
        return self.context.unrestrictedTraverse('confirm_icon.gif').tag(title=_(u"Yes"))
    
    @property
    def false_icon(self):
        return self.context.unrestrictedTraverse('delete_icon.gif').tag(title=_(u"No"))
    
    @property
    def isSecure(self):
        return (self._prtc.find('https/') == 0)

    @property
    def isWebKit(self):
        return (self._ua.find('webkit') >= 0)

    @property
    def isOpera(self):
        return (self._ua.find('opera') >= 0)
    
    @property
    def isChrome(self):
        return (self._ua.find('chrome') >= 0)

    @property
    def isSafari(self):
        return (not self.isChrome) and (self._ua.find('safari') >= 0)
    
    @property
    def isSafari3(self):
        return self.isSafari and (self._ua.find('version/3') > 0)
    
    @property
    def isSafari4(self):
        return self.isSafari and (self._ua.find('version/4') > 0)
    
    @property
    def isIE(self):
        return (not self.isOpera) and (self._ua.find('msie') >= 0)
    
    @property
    def isIE7(self):
        return self.isIE and (self._ua.find('msie 7') >= 0)
    
    @property
    def isIE8(self):
        return self.isIE and (self._ua.find('msie 8') >= 0)
    
    @property
    def isIE6(self):
        return self.isIE and (not (self.isIE7 or self.isIE8))

    @property
    def isGecko(self):
        return (not self.isWebKit) and (self._ua.find('gecko') >= 0)
    
    @property
    def isGecko3(self):
        return self.isGecko and (self._ua.find('rv:1.9') > 0)
    
    @property
    def isGecko2(self):
        return self.isGecko and (not self.isGecko3)
    
    @property
    def isWindows(self):
        return (self._ua.find('windows') > 0) or (self._ua.find('win32') > 0)
    
    @property
    def isMac(self):
        return (self._ua.find('macintosh') > 0) or (self._ua.find('mac os x') > 0)
    
    @property
    def isLinux(self):
        return (self._ua.find('linux') > 0)

    @property
    def isSafariOnMac(self):
        return (self.isMac and self.isSafari)
    
    @property
    def isSafariOnWin(self):
        return (self.isWindows and self.isSafari)
    
    @property
    def isGeckoOnMac(self):
        return (self.isMac and self.isGecko)
    
    @property
    def isGeckoOnLinux(self):
        return (self.isLinux and self.isGecko)
    
    @property
    def isGeckoOnWin(self):
        return (self.isWindows and self.isGecko)
    
    @property
    def isOperaOnMac(self):
        return (self.isMac and self.isOpera)
    
    @property
    def isOperaOnLinux(self):
        return (self.isLinux and self.isOpera)
    
    @property
    def isOperaOnWin(self):
        return (self.isWindows and self.isOpera)
    
    @property
    def isChromeOnMac(self):
        return (self.isMac and self.isChrome)
    
    @property
    def isChromeOnLinux(self):
        return (self.isLinux and self.isChrome)
    
    @property
    def isChromeOnWin(self):
        return (self.isWin and self.isChrome)
