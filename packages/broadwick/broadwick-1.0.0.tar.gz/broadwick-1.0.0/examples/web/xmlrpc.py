import broadwick.utils
from broadwick.web import expose_xmlrpc, expose
from broadwick.web.xmlrpc import DocXMLRPC

class Control:
    """An example control interface that you would expose to the outside world"""
    @expose_xmlrpc
    def add(self, a, b):
        """returns a+b"""
        return a+b

    @expose_xmlrpc
    def error(self):
        """just throws an Exception"""
        raise Exception('Oh dear')

    def subtract(self, a, b):
        """This method is not exposed via xmlrpc"""

    def __init__(self):
        # expose functions on TVControl on this interface
        self.tv = expose_xmlrpc(TVControl())

class TVControl:
    @expose_xmlrpc
    def change_channel(self, to):
        """Change the TV channel. """
        pass

if __name__ == '__main__':
    control = Control()
    view = DocXMLRPC(control,
                     allow_none = True, 
                     server_title = "Broadwick XMLRPC Example",
                     server_name = "Broadwick XMLRPC Example Thingy",
                     server_documentation = "blah blah bink bonk bang nosh nosh monkey",
                     )
    broadwick.utils.quickstart(view)
