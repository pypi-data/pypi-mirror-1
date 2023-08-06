import pkg_resources

import os
from tempfile import mkstemp

from Products.PortalTransforms.interfaces import itransform

def _safe_unicode(text):
    if not isinstance(text, unicode):
        text = unicode(text, 'utf-8', 'ignore')
    return text


class MultiMarkdownToHtml:
    """Transform turn MultiMarkdown text into HTML"""

    __implements__ = itransform

    __name__ = "multimarkdown_to_html"
    output = "text/html"

    def __init__(self, name=None, inputs=('text/x-multimarkdown',)):
        self.config = {
            'inputs': inputs,
        }
        self.config_metadata = {
            'inputs' : ('list', 
                        'Inputs', 
                        'Input(s) MIME type. Change with care.'),
             }
        if name:
            self.__name__ = name
        
    def name(self):
        return self.__name__

    def __getattr__(self, attr):
        if attr in self.config:
            return self.config[attr]
        raise AttributeError(attr)

    def convert(self, orig, data, **kwargs):
        # Get path env variable
        if os.environ.has_key('PATH'):
            path = os.environ['PATH']
            path = path.split(os.pathsep)
        else:
            path = self.DEFAULT_PATH

        # Check existance of perl binary
        found = False
        for dir in path:
            if not found:
                fullname = os.path.join(dir, 'perl')
                if os.path.exists(fullname):
                    perl_path = fullname
                    found = True
        
        # Raise an error if no perl binary is found
        if not found:
            raise LookupError('No perl binary found')
    
        # Check existance of MultiMarkdown.pl in path
        found = False
        for dir in path:
            if not found:
                fullname = os.path.join(dir, 'MultiMarkdown.pl')
                if os.path.exists(fullname):
                    script_path = fullname
                    found = True
                
        # If none is found, use the script included in the package
        if not found:
            pkg_name = 'collective.transform.multimarkdown'
            local_script = 'scripts/MultiMarkdown.pl'
            script_path = pkg_resources.resource_filename(pkg_name, local_script)
            
        # Create a temp file with the original text for the script to read
        text_path = mkstemp()[1]
        text_file = open(text_path, 'w')
        text_file.write(orig)
        text_file.close()

        # Do the conversion
        conversion = os.popen('%s %s %s' % (perl_path, script_path, text_path))
        text = conversion.read()

        data.setData(text)
        return data


def register():
    return MultiMarkdownToHtml()
