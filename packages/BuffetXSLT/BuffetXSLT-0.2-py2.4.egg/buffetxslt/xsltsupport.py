import os

import Ft
from Ft.Xml.Xslt import Processor
from Ft.Lib.Uri import OsPathToUri
from Ft.Xml import InputSource


class BuffetXSLTPlugin(object):
    extension = "xsl"

    def __init__(self, extra_vars_func=None, config=None):
        self.get_extra_vars = extra_vars_func
        if config:
            self.config = config
        else:
            self.config = dict()
        self.processor = Processor.Processor()

    def load_template(self, template_path):
        parts = template_path.split('.')
        true_path = "%s.%s" % (os.path.join(*parts), self.extension)
        stylesheet_as_uri = OsPathToUri(true_path)
        transform = InputSource.DefaultFactory.fromUri(stylesheet_as_uri)
        return transform

    def render(self, info, format='html', fragment=False, template=None):
        transform = self.load_template(template)
        document = info.get('xml', '<root />')
        source = InputSource.DefaultFactory.fromString(document, 'http://none.xml')
        self.processor.appendStylesheet(transform)
        output = self.processor.run(source, topLevelParams=info)
        
        # create a new processor for the next call (as suggested at
        # http://uche.ogbuji.net/tech/akara/nodes/2003-01-01/basic-xslt)
        self.processor = Processor.Processor()
        
        return output

    def transform(self, info, template):
        pass

