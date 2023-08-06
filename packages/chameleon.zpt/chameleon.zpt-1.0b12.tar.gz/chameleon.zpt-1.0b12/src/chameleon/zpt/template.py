from chameleon.core import template

import language

class PageTemplate(template.Template):
    __doc__ = template.Template.__doc__ # for Sphinx autodoc

    default_parser = language.Parser()
    version = 2
    
    def __init__(self, body, parser=None, format=None,
                 doctype=None, encoding=None):
        if parser is None:
            parser = self.default_parser
        super(PageTemplate, self).__init__(body, parser, format,
                                           doctype, encoding)

class PageTemplateFile(template.TemplateFile):
    __doc__ = template.TemplateFile.__doc__ # for Sphinx autodoc

    default_parser = language.Parser()
    version = 2
    
    def __init__(self, filename, parser=None, format=None,
                 doctype=None, **kwargs):
        if parser is None:
            parser = self.default_parser
        super(PageTemplateFile, self).__init__(filename, parser, format,
                                               doctype, **kwargs)
