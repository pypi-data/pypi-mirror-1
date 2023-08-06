import os

from paste import urlparser
from webob import Request, Response
from mako.template import Template
from mako.lookup import TemplateLookup


class CallsController:

    def index(self, environ, start_response):
        req = Request(environ)
        positional, named = environ.get('wsgiorg.routing_args')
        named.update(req.params)
        stats_dict = req.environ.get('wsgiprofile.stats')
        pid = int(named.pop('pid'))
        if not pid in stats_dict:
            raise KeyError("%s not found. Server may have been restarted" % pid)
        stats_info = stats_dict.get(pid)
        if 'sort' in named:
            stats_info.sort(named.pop('sort'))
        named['stats_info'] = stats_info
        format = named.pop('format', None)
        if format == 'html':
            body = self.html(req, **named)
        elif format == 'json':
            body = self.json(req, **named)
        else:
            body = self.chrome(req, **named)
        response = Response(body=body, content_type='text/html')
        return response(environ, start_response)

    def chrome(self, req, stats_info, search=None, rowcount=10):
        """Render the StatsInfo object into an html page, with chrome."""
        dirname = os.path.dirname(__file__)
        lookup = TemplateLookup(directories=[dirname])
        template = Template(filename=os.path.join(dirname, 'base.html'),
                            lookup=lookup)
        url_for = req.environ['wsgiprofile.mapper'].generate
        filters = [rowcount]
        if search:
            filters.insert(0, search)
        stats = stats_info.items(filters=filters)
        context = dict(info=stats_info, stats=stats, pid=stats_info.id,
                       url_for=url_for, search=search)
        return template.render(**context)

    def html(self, req, stats_info, search=None, rowcount=10):
        """Render the StatsInfo object into html, returning only the table."""
        dirname = os.path.dirname(__file__)
        lookup = TemplateLookup(directories=[dirname])
        template = Template(filename=os.path.join(dirname, 'rows.html'),
                            lookup=lookup)
        url_for = req.environ['wsgiprofile.mapper'].generate
        filters = [rowcount]
        if search:
            filters.insert(0, search)
        stats = stats_info.items(filters=filters)
        context = dict(stats=stats,
                       pid=stats_info.id,
                       url_for=url_for,
                       search=search)
        return template.render(**context)

    def json(self, req, stats):
        return repr(stats.items())


class StaticController:
    """Static path where images, javascript, and other files live."""

    def index(self, environ, start_response):
        app = urlparser.StaticURLParser(os.path.join(os.path.dirname(__file__),
                                             'public'))
        return app(environ, start_response)


# def callees(self, req):
#     pass

# def callers(self, req):
#     pass

