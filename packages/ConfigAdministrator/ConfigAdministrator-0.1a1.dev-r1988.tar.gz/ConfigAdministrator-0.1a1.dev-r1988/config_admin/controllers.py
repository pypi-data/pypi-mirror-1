import cherrypy
import logging

from turbogears import controllers, expose, redirect, flash, identity

log = logging.getLogger("config_admin.controllers")

from model import *

configuration_panels = dict()

require_predicate = True

global_predicate = None

class ConfigServer(controllers.Controller):
    @expose(format='json')
    def index(self, panel, **kw):
        panel = configuration_panels[panel]
        if require_predicate and not panel.predicate and not global_predicate:
            raise 'A predicate or global predicate is needed'
        if global_predicate:
            if not global_predicate.eval_with_object(identity.current):
                raise identity.IdentityFailure([])
        if panel.predicate:
            if not panel.predicate.eval_with_object(identity.current):
                raise identity.IdentityFailure([])
        log.info('saving config for %s, data (%s)' % (panel, kw))
        for k,v in kw.iteritems():
            v = unicode(v)
            try:
                cp = ConfigOption.selectBy(name=k, panel=panel.name)[0]
                cp.value = v
            except IndexError:
                cp = ConfigOption(name=k, panel=panel.name, value=v)
        flash('%s configuration updated!' % panel.name)
        raise redirect('/modulos/configuration/')

