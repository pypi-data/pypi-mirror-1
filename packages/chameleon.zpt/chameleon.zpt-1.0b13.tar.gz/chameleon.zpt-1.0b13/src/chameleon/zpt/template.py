from chameleon.core import template

import language

class PageTemplate(template.Template):
    __doc__ = template.Template.__doc__ # for Sphinx autodoc

    default_parser = language.Parser()
    version = 3
    
    def __init__(self, body, parser=None, format=None,
                 doctype=None, encoding=None):
        if parser is None:
            parser = self.default_parser
        super(PageTemplate, self).__init__(body, parser, format,
                                           doctype, encoding)

    def __call__(self, **kwargs):
        kwargs["template"] = self
        return self.render(**kwargs)

    def render_macro(self, macro, global_scope=False, parameters={}):
        parameters["template"] = self
        return super(PageTemplate, self).render_macro(
            macro, global_scope=global_scope, parameters=parameters)

class PageTemplateFile(template.TemplateFile, PageTemplate):
    __doc__ = template.TemplateFile.__doc__ # for Sphinx autodoc

    default_parser = language.Parser()

    def __init__(self, filename, parser=None, format=None,
                 doctype=None, **kwargs):
        if parser is None:
            parser = self.default_parser
        super(PageTemplateFile, self).__init__(filename, parser, format,
                                               doctype, **kwargs)
