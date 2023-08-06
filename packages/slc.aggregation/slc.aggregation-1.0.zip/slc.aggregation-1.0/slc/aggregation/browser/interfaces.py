from zope import schema
from zope.interface import Interface
from zope.i18nmessageid import MessageFactory

from plone.app.vocabularies.catalog import SearchableTextSourceBinder

_ = MessageFactory('slc.aggregation')

class IAggregatorView(Interface):
    """ """

class IAggregatorConfiguration(Interface):
    """ This interface defines the configuration form """
    aggregation_sources = schema.List(
            title=_(u"Aggregation sources"),
            description=_(u"Specify the source folder(s) from where items will be "
                            "retrieved and displayed in the current context"),
            value_type=schema.Choice(source=SearchableTextSourceBinder(
                                                        {'is_folderish' : True},
                                                        default_query = 'path:'
                                                        )
                                                    ),
            default=[],
            )

    content_types = schema.List(
            title=_(u"Content types to aggregate"),
            description=_(u"Choose from the list of item types displayed in "
                            "the box on the left by copying them to the right"
                            ),
            value_type=schema.Choice(vocabulary="plone.app.vocabularies.UserFriendlyTypes"),
            ) 

    review_state = schema.List(
            title=_(u"The workflow state of the items to be aggregated"),
            description=_(u"Choose from the list of item types displayed in "
                            "the box on the left by copying them to the right"
                            ),
            value_type=schema.Choice(vocabulary="plone.app.vocabularies.WorkflowStates"),
            required=True,
            ) 

    keyword_list = schema.TextLine(
            title=_(u"Filtering keywords"),
            description=_(u'Add your keywords here, separated by spaces.'),
            required=False,
            )

