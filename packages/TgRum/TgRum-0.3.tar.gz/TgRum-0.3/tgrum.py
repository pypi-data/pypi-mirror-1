import logging
from tg import config as tg_config, request, TGController, expose, flash,\
               get_flash, get_status, redirect, render, WSGIAppController
from pylons import app_globals
from paste.deploy.converters import asbool
from webob import Request
from rum.wsgiapp import RumApp
from rum.controller import process_output
from rum.util import merge_dicts

log = logging.getLogger(__name__)

__all__ = ['RumAlchemyController']

@process_output.before(
    "isinstance(output,dict) and self.get_format(routes) != 'json'",
    )
def _inject_tg_vars(self, output, routes):
    tg_vars = render._get_tg_vars()
    for k in 'c', 'tmpl_context', 'h', 'url', 'helpers', 'tg':
        if k in output:
            log.warn("Will not override var %r which rum provided", k)
        else:
            output[k] = tg_vars[k]
        output['app_globals'] = output['g'] = app_globals

class RumAlchemyController(WSGIAppController):
    def __init__(self, model, allow_only=None, template_path=None, config=None,
                 render_flash=True):
        search_path = []
        if template_path:
            search_path.append(template_path)
        base_config = {
            'rum.repositoryfactory': {
                'use': 'sqlalchemy',
                'scan_modules': [model],
                'session_factory': model.DBSession,
            },
            'rum.viewfactory': {
                'use': 'toscawidgets',
            },
            'templating': {
                'search_path': search_path,
            },
            'render_flash': render_flash
        }
        config = merge_dicts(base_config, config or {})
        log.info("initializing RumApp for RumAlchemyController")
        rum_app = RumApp(
            config,
            full_stack=False,
            debug=asbool(tg_config['debug'])
            )
        super(RumAlchemyController, self).__init__(rum_app, allow_only)
