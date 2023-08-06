""".. _GenshiComponent:

``genshi`` -- Genshi Templating
===============================

Render templates using Genshi_. Assumes that
the name of the template is the same as the name
of your handler.

.. _Genshi: http://genshi.edgewall.org/

"""

from genshi.template import TemplateLoader, MarkupTemplate, NewTextTemplate

from haus.components.abstract import Component, wraps


class GenshiTemplatingComponent(Component):

    provides = ['render_view']

    def __init__(self, wrk):
        config = wrk.config.get('genshi', {})
        package_text_templates = wrk.pdfilename(
            config.get('text.templates', 'text')
        )
        package_markup_templates = wrk.pdfilename(
            config.get('markup.templates', config.get('templates.dir', 'html'))
        )
        template_search_path = list(config.get('path', []))
        template_search_path.insert(0, package_text_templates)
        template_search_path.insert(0, package_markup_templates)
        self.loader = TemplateLoader(
            template_search_path,
            auto_reload=config.get('reload', False)
        )
        wrk.functions['render_view'] = self.render_view

    def render_view(self, template_name, stuff, 
                    mode='html', doctype='html', text=False):
        if text:
            klass = NewTextTemplate
        else:
            klass = MarkupTemplate
        template = self.loader.load(template_name, cls=klass)
        genned = template.generate(**stuff)
        if text:
            return genned.render()
        else:
            return genned.render(mode, doctype=doctype)

    def __call__(self, wrk, *args, **kwargs):
        render = wrk.functions['render_view']
        if kwargs.get('text'):
            text = True
        else:
            text = False
        def middleware(app):
            if 'template' in kwargs:
                template_name = kwargs['template']
            elif len(args) == 1:
                template_name = args[0]
            else:
                if text:
                    template_name = "%s.txt" % app.__name__
                else:
                    template_name = "%s.html" % app.__name__
            @wraps(app)
            def proxy(environ, start_response):
                stuff = app(environ, start_response)
                stuff.setdefault('config', wrk.functions['get_config'](environ))
                if isinstance(stuff, dict):
                    return render(template_name, stuff, text=text)
                else:
                    return stuff
            return proxy
        return middleware

