from elementtree.ElementTree import parse
from deliverance.utils import set_rule_uri
from deliverance.utils import set_theme_uri
from repoze.urispace.middleware import getAssertions

class DeliveranceSelect(object):
    """ Pure ingress filter:  tweaks environment to get Deliverance to use
        desired rule / theme, based on URISpace.
    """
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        assertions = getAssertions(environ)

        rules = assertions.get('rules')
        if rules is not None:
            set_rule_uri(environ, rules)

        theme = assertions.get('theme')
        if theme is not None:
            set_theme_uri(environ, theme)

        return self.application(environ, start_response)

def make_middleware(application, global_conf):
    return DeliveranceSelect(application)
