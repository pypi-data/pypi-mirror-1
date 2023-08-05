import cherrypy
from buffet import TemplateFilter, using_template

class XSLTTest(object):
    _cpFilterList = [TemplateFilter('xslt', 'templates')]

    @cherrypy.expose
    @using_template('index')
    def index(self):
        return dict(title="XSLT and Buffet!", message="Thanks to Sylvain and Uche!")

    @cherrypy.expose
    @using_template('another')
    def another(self):
        return dict(title="Another test", message="Just making sure this works")

cherrypy.root = XSLTTest()

cherrypy.server.start()

