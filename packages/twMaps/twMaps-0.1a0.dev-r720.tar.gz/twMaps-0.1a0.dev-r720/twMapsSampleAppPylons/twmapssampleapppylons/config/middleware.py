from paste import httpexceptions
from paste.cascade import Cascade
from paste.urlparser import StaticURLParser
from paste.registry import RegistryManager
from paste.deploy.config import ConfigMiddleware, CONFIG
from paste.deploy.converters import asbool

from pylons.error import error_template
from pylons.middleware import ErrorHandler, ErrorDocuments, StaticJavascripts, error_mapper
import pylons.wsgiapp

from twmapssampleapppylons.config.environment import load_environment
import twmapssampleapppylons.lib.helpers
import twmapssampleapppylons.lib.app_globals as app_globals

def make_app(global_conf, full_stack=True, **app_conf):
    """Create a WSGI application and return it

    global_conf is a dict representing the Paste configuration options, the
    paste.deploy.converters should be used when parsing Paste config options
    to ensure they're treated properly.

    """
    # Setup the Paste CONFIG object, adding app_conf/global_conf for legacy code
    conf = global_conf.copy()
    conf.update(app_conf)
    conf.update(dict(app_conf=app_conf, global_conf=global_conf))
    CONFIG.push_process_config(conf)

    # Load our Pylons configuration defaults
    config = load_environment(global_conf, app_conf)
    config.init_app(global_conf, app_conf, package='twmapssampleapppylons',
                    template_engine='mako')

    # Load our default Pylons WSGI app and make g available
    app = pylons.wsgiapp.PylonsApp(config,
                                   helpers=twmapssampleapppylons.lib.helpers,
                                   g=app_globals.Globals)
    g = app.globals
    app = ConfigMiddleware(app, conf)

    # YOUR MIDDLEWARE Put your own middleware here, so that any problems are
    # caught by the error handling middleware underneath


    from toscawidgets.view import EngineManager
    from toscawidgets.middleware import TGWidgetsMiddleware
    from toscawidgets.mods.pylonshf import PylonsHostFramework
    from pylons.templating import render

    def _update_names(ns):
        """Return a dict of Pylons vars and their respective objects updated
        with the ``ns`` dict."""
        g = pylons.g._current_obj()
        d = dict(
            context=pylons.c._current_obj(),
            g=g,
            h=getattr(g.pylons_config, 'helpers', pylons.h._current_obj()),
            render=render,
            request=pylons.request._current_obj(),
            session=pylons.session._current_obj(),
            translator=pylons.translator,
            ungettext=pylons.i18n.ungettext,
            _=pylons.i18n._,
            N_=pylons.i18n.N_
            )
        d.update(ns)
        return d

    class CustomEngineManager(EngineManager):
        def _initialize_engine(self, name, factory, engine_options=None,
                               stdvars=None):
            if engine_options is None:
                engine_options = {}
            if stdvars is None:
                stdvars = {}
            try:
                def extra_vars():
                    return _update_names(stdvars)
                self[name] = factory(extra_vars, engine_options)
            except:
                raise

    class CustomHostFramework(PylonsHostFramework):
        engines = CustomEngineManager()
        # propigate the "templates" config to the "directories" 
        # that will be used by Mako's TemplateLookup
        engines.load_all({'mako.directories': config.paths['templates']})

    app = TGWidgetsMiddleware(app, CustomHostFramework)



    # If errror handling and exception catching will be handled by middleware
    # for multiple apps, you will want to set full_stack = False in your
    # config file so that it can catch the problems.
    if asbool(full_stack):
        # Change HTTPExceptions to HTTP responses
        app = httpexceptions.make_middleware(app, global_conf)

        # Error Handling
        app = ErrorHandler(app, global_conf, error_template=error_template,
                           **config.errorware)

        # Display error documents for 401, 403, 404 status codes (if debug is
        # disabled also intercepts 500)
        app = ErrorDocuments(app, global_conf, mapper=error_mapper, **app_conf)

    # Establish the Registry for this application
    app = RegistryManager(app)

    static_app = StaticURLParser(config.paths['static_files'])
    javascripts_app = StaticJavascripts()
    app = Cascade([static_app, javascripts_app, app])
    return app
