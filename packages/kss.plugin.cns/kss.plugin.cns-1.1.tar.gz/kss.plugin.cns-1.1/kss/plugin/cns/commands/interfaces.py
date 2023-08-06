from zope.interface import Interface

class ICNSCommands(Interface):
    """Commands for additional operations.
    
    Registered as command set 'cns'
    """
    
    def redirectRequest(url):
        """ Redirects request to specified url. """

    def valueSetter(target_element, source_element=None, value=None):
        """ Sets a value of the target_element by either source_element value or given value """
        
    def alertText(message):
        """ Show alert box with a given message ( not for debugging purposes as core alert plugin does) """
        
    def openWindow(url):
       """ Open a new window with a given url """
    
    def removeAttribute(selector, name):
        """ Remove attribute from node defined by selector """