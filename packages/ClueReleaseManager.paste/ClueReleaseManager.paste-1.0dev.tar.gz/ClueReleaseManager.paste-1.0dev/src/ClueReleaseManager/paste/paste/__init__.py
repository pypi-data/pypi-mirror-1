from webob import Request, exc
from clue.relmgr import utils, wsgiapp

def crmgr_factory(global_config, **local_config):
    """
    A paste.httpfactory to wrap a crmgr WSGI based application.
    """
    debug = False
    if global_config.get('debug', 'False').lower() == 'true':
        debug = True
    aconf = local_config.copy()
    for key in aconf.keys():
        if not key in ('sqluri', 'basefiledir', 'baseurl',
                       'security_config', 'self_register',
                       'backup_pypis'):
            del aconf[key]
    aconf['logger'] = utils.logger
    if aconf.get('self_register', 'false') == 'true':
        aconf['self_register'] = True
    if 'backup_pypis' in aconf:
        aconf['backup_pypis'] = aconf['backup_pypis'].split()
    app = wsgiapp.make_app({}, **aconf)
    def crmgr_app(environ, start_response):
        req = Request(environ)
        try:
            resp = req.get_response(app)
            return resp(environ, start_response)
        except Exception, e:
            if not debug:
                return exc.HTTPServerError(str(e))(environ, start_response)
            else:
                raise
    return crmgr_app

