from zope import component
from zope.annotation.interfaces import IAnnotations
from zope.interface import implements
from zope.formlib import form
from zope.i18nmessageid import MessageFactory

from Acquisition import aq_inner
from Acquisition import aq_parent

from plone.app.form.widgets.uberselectionwidget import UberMultiSelectionWidget

from Products.ATContentTypes.interface.document import IATDocument
from Products.AdvancedQuery import Or, Eq, And, In
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBatch import Batch
from Products.Five import BrowserView
from Products.Five.formlib import formbase

from p4a.subtyper.interfaces import ISubtyper

from slc.aggregation.browser.interfaces import IAggregatorView
from slc.aggregation.browser.interfaces import IAggregatorConfiguration

_ = MessageFactory('slc.aggregation')

class Aggregator(BrowserView):
    implements(IAggregatorView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_context(self):
        context = aq_inner(self.context)
        # if on a Document, get the parent-folder
        if IATDocument.providedBy(context):
            context = aq_parent(context)
        if hasattr(context, 'isCanonical') and not context.isCanonical():
            context = context.getCanonical()
        return context

    def is_subtyped_as_aggregator(self):
        context = aq_inner(self.context)
        subtyper = component.getUtility(ISubtyper)
        type = subtyper.existing_type(context)
        if type:
            return type.name == 'slc.aggregation.aggregator'
        else:
            return False

    def query_items(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        if hasattr(catalog, 'getZCatalog'):
            catalog = catalog.getZCatalog()

        portal_state = component.getMultiAdapter(
                                (self.context, self.request), 
                                name=u'plone_portal_state'
                                )

        canonical = context.getCanonical()
        annotations = IAnnotations(canonical)
        types = annotations.get('content_types', [])

        queries = []
        if 'News Item' in types and 'isNews' in catalog.indexes():
            queries.append(Or(In('portal_type', types), Eq('isNews', True)))

        elif types:
            queries.append(In('portal_type', types))

        state = annotations.get('review_state')
        if state:
            queries.append(In('review_state', state))

        current_language = context.getLanguage()

        paths = annotations.get('aggregation_sources', [])
        if paths:
            portal_url = getToolByName(context, 'portal_url')
            portal_obj = portal_url.getPortalObject()
            portal_path = '/'.join(portal_obj.getPhysicalPath())
            full_paths = []
            for path in paths:
                full_path = '%s%s' % (portal_path, path)
                obj = context.unrestrictedTraverse(full_path.lstrip('/'))
                # Get the correct language version of the source folder
                if obj.getLanguage() != current_language:
                    translation = obj.getTranslation(language=current_language)
                    if translation:
                        full_path = '/'.join(translation.getPhysicalPath())

                full_paths.append(full_path)

            queries.append(In('path', full_paths))

        keywords = annotations.get('keyword_list', [])
        if keywords:
            queries.append(In('Subject', keywords))

        if queries:
            advanced_query = And(queries[0])
            if annotations.get('restrict_language'):
                advanced_query.addSubquery(Eq('Language', current_language))

            for q in queries[1:]:
                advanced_query.addSubquery(q)

            results = catalog.evalAdvancedQuery(advanced_query, (('Date', 'desc'),) ) 
            return results

        return []


    def get_items(self, b_size=10):
        results = self.query_items()
        b_start = self.request.get('b_start', 0)
        batch = Batch(results, b_size, int(b_start), orphan=0)
        return batch
        

class AggregatorConfigurationForm(formbase.PageForm):
    """  """
    form_fields = form.FormFields(IAggregatorConfiguration)
    form_fields['aggregation_sources'].custom_widget = UberMultiSelectionWidget
    label = _(u"Configure the aggregation settings for this folder")

    def setUpWidgets(self, ignore_request=False):
        request = self.request
        if not request.has_key('form.actions.save'):
            # Add annotated values to the request so that we see the saved 
            # values on a freshly opened form.
            context = aq_inner(self.context).getCanonical()
            annotations = IAnnotations(context)
            for field in self.form_fields:
                key = field.__name__
                if annotations.get(key):
                    if key == 'keyword_list':
                        if type(annotations[key]) in  [str, unicode]:
                            request.form['form.%s' % key] = annotations[key]
                        else:
                            request.form['form.%s' % key] =  ' '.join(annotations[key])
                    elif annotations[key] == True:
                        request.form['form.%s' % key] =  "on"
                    else:
                        request.form['form.%s' % key] =  annotations[key]

        self.adapters = {}
        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            form=self, adapters=self.adapters, ignore_request=ignore_request)

    @form.action("save")
    def action_save(self, action, data):
        request = self.context.request
        canonical = aq_inner(self.context).getCanonical()
        annotations = IAnnotations(canonical)
        for field in self.form_fields:
            key = field.__name__
            value = data.get(key)
            if key == 'keyword_list' and value and type(value) == str:
                annotations[key] = [value]
            else:
                annotations[key] = value
        return request.RESPONSE.redirect(
                        '%s' % '/'.join(self.context.getPhysicalPath()))

    @form.action("cancel")
    def action_cancel(self, action, data):
        return self.context.request.RESPONSE.redirect(
                        '%s' % '/'.join(self.context.getPhysicalPath()))


