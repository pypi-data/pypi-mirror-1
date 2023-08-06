import logging
from Acquisition import Explicit, aq_base, aq_parent, aq_chain
from collective.multitemplate import IMultiTemplate
from collective.multitemplate import MultiTemplateMessageFactory as _
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider as IPortletDataProviderBase
from plone.portlets.interfaces import IPortletManager, IPortletRenderer
from plone.portlets.interfaces import IPortletAssignmentMapping
from zope import schema
from zope.component import queryAdapter, getMultiAdapter, getAdapters, getUtility
from zope.interface import implements
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.publisher.interfaces.browser import IBrowserView
from Products.Five.browser import BrowserView


log = logging.getLogger('collective.multitemplate')


class IPortletDataProvider(IPortletDataProviderBase):
    template = schema.Choice(
        title=_(u"heading_template", u"Template for rendering"),
        description=_(u"description_template", u"The template "
                      u"which should be used for rendering of this portlet."),
        required=False,
        vocabulary="collective.multitemplate.PortletTemplates",
    )


class TemplateVocabulary(object):
    """ """
    implements(IVocabularyFactory)

    def __call__(self, assignment):
        # use aq_chain and interface lookup
        request = assignment.REQUEST
        column_name = assignment.__parent__.__manager__
        column = getUtility(IPortletManager, name=column_name)
        view = None
        for obj in aq_chain(assignment):
            if IBrowserView.providedBy(obj):
                view = obj
                break
        assignment_mapping = None
        for obj in aq_chain(assignment):
            if IPortletAssignmentMapping.providedBy(obj):
                assignment_mapping = obj
                break
        if assignment_mapping is None:
            raise ValueError("No object implementing IPortletAssignmentMapping found in aq_chain")
        context = aq_parent(assignment_mapping)
        if context is None:
            raise ValueError("No context found in aq_chain")
        if view is None:
            view = BrowserView(context, request)
        renderer = getMultiAdapter((context, request, view, column,
                                    assignment),
                                   IPortletRenderer)
        templates = getAdapters((renderer,), IMultiTemplate)
        return SimpleVocabulary([SimpleTerm(x[0]) for x in templates])

TemplateVocabularyFactory = TemplateVocabulary()


class Assignment(base.Assignment):
    implements(IPortletDataProvider)

    template = None


class ViewMultiTemplate(Explicit):
    def __init__(self, default):
        self.default = default

    def __call__(self, *args, **kwargs):
        instance = aq_parent(self)
        name = getattr(aq_base(instance.data), 'template', None)
        render = None
        if name:
            render = queryAdapter(instance, IMultiTemplate, name=name)
            if render is None:
                log.error("Template '%s' for '%s' not found!" % (name, instance))
        if render is None:
            render = self.default
        return render.__of__(instance)(instance, *args, **kwargs)


class MultiTemplate(object):
    def __init__(self, template):
        self.template = template

    def __call__(self, klass):
        return self.template
