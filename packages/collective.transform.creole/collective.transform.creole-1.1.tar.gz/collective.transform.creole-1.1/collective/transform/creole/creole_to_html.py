from Products.PortalTransforms.interfaces import itransform
from creoleparser.dialects import Creole10
from creoleparser.core import Parser

def _safe_unicode(text):
    if not isinstance(text, unicode):
        text = unicode(text, 'utf-8', 'ignore')
    return text


class CreoleToHtml:
    """Transform to take creole wiki text and turn it into HTML"""

    __implements__ = itransform

    __name__ = "creole_to_html"
    output = "text/html"

    def __init__(self, name=None, inputs=('text/wiki+creole',), base_url='',
                 interwiki=[]):
        self.config = {
            'inputs': inputs,
            'base_url': base_url,
            'interwiki': interwiki
        }
        self.config_metadata = {
            'inputs' : ('list', 
                        'Inputs', 
                        'Input(s) MIME type. Change with care.'),
            'base_url' : ('string', 
                          'Wiki Link Base URL',
                          'Base URL to use when creating wiki links'),
            'interwiki' : ('list',
                           'Interwiki Base URLs',
                           'Interwiki names and base URLs on per line '
                           'separated by pipes (e.g. '
                           'wikipedia|http://en.wikipedia.org/wiki/).'),
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
        interwiki_links = {}
        interwiki = self.config['interwiki']
        if interwiki:
            interwiki_links = dict(
                map(lambda x: x.replace(' ', '').split('|'), interwiki)
            )
        custom_dialect = Creole10(
            wiki_links_base_url=self.config['base_url'],
            interwiki_links_base_urls=interwiki_links,
            use_additions=True,
            no_wiki_monospace=False,
        )
        plone_creole_parser = Parser(dialect=custom_dialect)
        text = plone_creole_parser(_safe_unicode(orig))
        data.setData(text)
        return data


def register():
    return CreoleToHtml()
