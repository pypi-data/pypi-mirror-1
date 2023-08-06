import logging
from tg import config as tg_config, request, TGController, expose, flash,\
               get_flash, get_status, redirect, render, WSGIAppController
from pylons import app_globals
from paste.deploy.converters import asbool
from webob import Request
from rum.wsgiapp import RumApp
from rum.controller import process_output
from rum.genericfunctions import when, around
from rum.util import merge_dicts
from rum import app
from rum.policy import Denial, Policy, anyone, NotProvided
from repoze.what.predicates import NotAuthorizedError, Predicate
from rum import fields
from rum.i18n import _

log = logging.getLogger(__name__)

__all__ = ['RumAlchemyController']

@process_output.before(
    "isinstance(output,dict) and self.get_format(routes) != 'json'",
    )
def _inject_tg_vars(self, output, routes):
    tg_vars = render._get_tg_vars()
    for k in 'c', 'tmpl_context', 'url', 'helpers', 'tg':
        if k in output:
            log.warn("Will not override var %r which rum provided", k)
        else:
            output[k] = tg_vars[k]
    output['app_globals'] = output['g'] = app_globals

class TGDummyPolicy(Policy):
    def has_permission(self, obj, action, attr=None, user=NotProvided):
        if obj in app.resources:
            resource = obj
        else:
            resource = obj.__class__
        if attr is None:
            return True
        if not isinstance(app.field_for_resource_with_name(resource, attr), fields.Password):
            return True
        if action in ['create', 'new', 'edit', 'update']\
            and app.request.routes.get('format', 'html')=='html':
                return True
        else:
            return Denial(_("No access to password fields allowed"))

class RumAlchemyController(WSGIAppController):
    def __init__(self, model, allow_only=None, template_path=None, config=None,
                 render_flash=True, policy=TGDummyPolicy):
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
        if not policy is None:
            config["rum.policy"]={"use": policy}
        log.info("initializing RumApp for RumAlchemyController")
        rum_app = RumApp(
            config,
            full_stack=False,
            debug=asbool(tg_config['debug'])
            )
        super(RumAlchemyController, self).__init__(rum_app, allow_only)

    def delegate(self, environ, start_response):
        """
        Delegates the request to the WSGI app.

        Insert identity 
        """
        identity=environ.get("repoze.who.identity", None)
        if identity is not None:
            user=identity.get("user")
        else:
            user=None
        environ["rum.user"]=user
        log.debug("injecting user %s into rum", user)
        return super(RumAlchemyController, self).delegate(environ, start_response)


class TGPolicy(Policy): pass

@when(TGPolicy.register.im_func, "isinstance(predicate, Predicate)")
def __register_adapted_repoze_what_predicate(
    cls, predicate, obj=None, action=None, attr=None, rule=None
    ):
    predicate = adapt_rw_predicate(predicate)
    return cls.register(predicate, obj, action, attr, rule)

_opposite_actions=dict()
for (l,r) in [('edit', 'update'), ('delete', 'confirm_delete'), ('new', 'create')]:
    _opposite_actions[l]=r
    _opposite_actions[r]=l

@around(TGPolicy.register.im_func, "action in _opposite_actions")
def __pairing_actions(next_method,
    cls, predicate, obj=None, action=None, attr=None, rule=None
    ):
    other=_opposite_actions[action]
    new_rule="action in "+repr([action, other])
    if rule is not None:
        assert isinstance(rule, basestring)
        rule="("+rule+") and ("+ new_rule+")"
    else:
        rule=new_rule
    
    cls.register(predicate, obj, None, attr, rule)

def adapt_rw_predicate(predicate):
    def checker(policy, obj, action, attr, user):
        #WARNING: user parameter is always ignored when adapting repoze.what
        # since r.w unconditionally uses the currently logged in user
        try:
            predicate.check_authorization(request.environ)
            return True
        except NotAuthorizedError, e:
            return Denial(unicode(e))
    return checker
