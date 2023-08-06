from zope.interface import Interface, Attribute

class IBrowserDetector(Interface):
    """ A browser agent detector view """
    
    agent = Attribute("User Agent")
    protocol = Attribute("Protocol type")
    platform = Attribute("Browser Platform")
    browser = Attribute("Browser type/version")
    true_icon = Attribute("True icon")
    false_icon = Attribute("False icon")
    
    isSecure = Attribute("True if secure protocol is in use")
    isWebKit = Attribute("True if a WebKit based browser has been detected")
    
    isOpera = Attribute("True if an Opera browser has been detected")
    isChrome = Attribute("True if a Chrome browser has been detected")

    isSafari = Attribute("True if a Safari browser has been detected")
    isSafari3 = Attribute("True if a Safari browser of version 3.x has been detected")
    isSafari4 = Attribute("True if a Safari browser of version 4.x has been detected")
    
    isIE = Attribute("True if a Internet Explorer browser has been detected")
    isIE7 = Attribute("True if a Internet Explorer browser of version 7.x has been detected")
    isIE8 = Attribute("True if a Internet Explorer browser of version 8.x has been detected")
    isIE6 = Attribute("True if a Internet Explorer browser of version 6.x has been detected")

    isGecko = Attribute("True if a Mozilla/Firefox browser has been detected")
    isGecko3 = Attribute("True if a Mozilla/Firefox browser of version 3.x has been detected")
    isGecko2 = Attribute("True if a Mozilla/Firefox browser of version 2.x has been detected")
    
    isWindows = Attribute("True if a Windows platform has been detected")
    isMac = Attribute("True if a Mac platform has been detected")
    isLinux = Attribute("True if a Linux platform has been detected")
    
    isSafariOnMac = Attribute("True if a Safari browser on Mac has been detected")
    isSafariOnWin = Attribute("True if a Safari browser on Windows has been detected")
    
    isGeckoOnMac = Attribute("True if a Gecko browser on Mac has been detected")
    isGeckoOnLinux = Attribute("True if a Gecko browser on Linux has been detected")
    isGeckoOnWin = Attribute("True if a Gecko on Windows browser has been detected")
    
    isOperaOnMac = Attribute("True if a Opera browser on Mac has been detected")
    isOperaOnLinux = Attribute("True if a Opera browser on Linux has been detected")
    isOperaOnWin = Attribute("True if a Opera browser on Windows has been detected")
    
    isChromeOnMac = Attribute("True if a Chrome browser on Mac has been detected")
    isChromeOnLinux = Attribute("True if a Chrome browser on Linux has been detected")
    isChromeOnWin = Attribute("True if a Chrome browser on Windows has been detected")
