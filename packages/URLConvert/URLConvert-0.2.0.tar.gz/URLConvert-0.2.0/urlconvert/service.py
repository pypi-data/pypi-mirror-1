import warnings

from urlconvert import extract_url_parts
from bn import AttributeDict, absimport

class URLService(object):
    """
    To use this service effectievely outside a web environment you currently 
    have to specify the ``SERVER_NAME`` and ``SERVER_PORT`` explicitly in the
    ``environ`` dictionary.
    """
    def __init__(self, make_ruleset):
        self.ruleset = None
        self.make_ruleset = make_ruleset

    @staticmethod
    def create(flow, name, config=None):
        if config is None: 
            config = URLService.config(flow, name)
        if not config:
            # Assume we are using it in a framework and that the config
            # options already have all we need to know.
            url_module = absimport(
                '.'.join([flow.config.app.package, 'dynamic', 'url'])
            )
            return URLService(make_ruleset=url_module.make_ruleset)
        else:
            return URLService(make_ruleset=config.make_ruleset)

    @staticmethod
    def config(flow, name):
        if not flow.config.option.has_key(name):
            return ''

        from flows.config import handle_option_error
        options = flow.config.option[name]
        from conversionkit import Conversion
        from configconvert import stringToObject
        from recordconvert import toRecord
        converter = toRecord(
            missing_errors = \
               "The required option '%s.%%(key)s' is missing"%name,
            empty_errors = "The option '%s.%%(key)s' cannot be empty"%name,
            converters=dict(
                make_ruleset = stringToObject()
            )
        )
        conversion = Conversion(flow.config.option[name]).perform(converter)
        if not conversion.successful:
            handle_option_error(conversion)
        else:
            flow.config[name] = conversion.result
        return flow.config[name]

    def start(self, flow, name):
        if self.ruleset is None:
            self.ruleset = self.make_ruleset(flow)
        flow[name] = AttributeDict()
        #flow[name]['ruleset'] = self.ruleset

        def url_for(*k, **p):
            warnings.warn("service.url.url_for() has been replaced by service.url.generate()", DeprecationWarning)
            if k:
                raise Exception(
                    'You cannot have keyword arguments when using URLConvert'
                )
            url_parts = extract_url_parts(flow)
            result = self.ruleset.generate_url(p, url_parts)
            return result

        def match(url=None):
             if isinstance(url, unicode):
                 # It is a URL as a string
                 raise NotImplementedError
             elif isinstance(url, dict):
                 # Assume it is a url_parts dict
                 url_parts = url
             elif url is None:
                 try:
                     url_parts = extract_url_parts(flow)
                 except Exception, e:
                     log.error('%s', e)
                     return None
             else:
                 raise TypeError('The argument to match() should be a Unicode string or a dictionary of URL parts, not %r'%url)
             conversion = self.ruleset.match(url_parts)
             if not conversion.successful:
                 return None
             return conversion.result

        def generate(vars, default_url_parts=None):
             if default_url_parts is None:
                 default_url_parts = extract_url_parts(flow)
             return self.ruleset.generate_url(vars, default_url_parts)

        def abort(status_code, detail="", headers=None, comment=None):
            """Aborts the request immediately by returning an HTTP exception
            
            In the event that the status_code is a 300 series error, the detail
            attribute will be used as the Location header should one not be
            specified in the headers attribute.
            
            """
            flow.wsgi.start_response('%s %s'%(status_code, comment or 'Abort'), headers or [])
            return ''

        def redirect_to(*args, **kargs):
            """Raises a redirect exception to the URL resolved by Routes'
            url_for function
            
            Optionally, a _code variable may be passed with the status code of
            the redirect, ie::
        
                redirect_to('home_page', _code=303)
            
            """
            raise Exception('Deprecated')
            # We have to do the redirect explicitly to get the cookie set.
            status = 302
            location = flow.url.generate(kargs)
            log.debug("Generating 302 redirect to %r" % location)
            return flow.url.abort(status, headers=[('Location', location)])

        flow[name]['url_for'] = url_for
        flow[name]['generate'] = generate
        flow[name]['match'] = match
        flow[name]['abort'] = abort
        flow[name]['redirect_to'] = redirect_to
        flow[name]['vars'] = match()

