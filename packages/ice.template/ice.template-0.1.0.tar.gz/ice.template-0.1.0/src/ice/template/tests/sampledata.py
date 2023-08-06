from zope.interface import implements
from zope.app.component.hooks import setSite
from zope.component import queryUtility, provideUtility
from z3c.sampledata.interfaces import ISampleDataPlugin

from ice.template import ITemplates, Templates

class MailTemplatesPlugin(object):
    implements(ISampleDataPlugin)
    name = 'templates.mail'
    dependencies = []
    schema = None

    def generate(self, context, param={}, dataSource=None, seed=None):
        setSite(context)
        templates = queryUtility(ITemplates, 'templates.mail')
        if templates is None:
            templates = Templates()
            sm = context.getSiteManager()
            sm['mail-templates'] = templates
            sm.registerUtility(templates, ITemplates, 'templates.mail')
        return templates

class SkinTemplatesPlugin(object):
    implements(ISampleDataPlugin)
    name = 'templates.skin'
    dependencies = []
    schema = None

    def generate(self, context, param={}, dataSource=None, seed=None):
        setSite(context)
        templates = queryUtility(ITemplates, 'templates.skin')
        if templates is None:
            templates = Templates()
            sm = context.getSiteManager()
            sm['skin-templates'] = templates
            sm.registerUtility(templates, ITemplates, 'templates.skin')
        return templates
