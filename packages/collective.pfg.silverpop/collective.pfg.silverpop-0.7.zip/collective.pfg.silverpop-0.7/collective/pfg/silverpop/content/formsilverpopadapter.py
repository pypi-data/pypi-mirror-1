"""Definition of the FormSilverpopAdapter content type
"""

import logging

from types import StringTypes

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata

from Products.PloneFormGen.content.actionAdapter import \
    FormActionAdapter, FormAdapterSchema

from Products.DataGridField import DataGridField, DataGridWidget
from Products.DataGridField.FixedColumn import FixedColumn

from collective.pfg.silverpop import silverpopMessageFactory as _
from collective.pfg.silverpop.interfaces import IFormSilverpopAdapter
from collective.pfg.silverpop.config import PROJECTNAME
from collective.pfg.silverpop.config import SILVERPOP_API_KEY_IDENTIFIER
from collective.pfg.silverpop.utilities import make_request
from collective.pfg.silverpop.utilities import get_mapping, set_mapping

LOGGER="collective.pfg.silverpop"


def info(msg):
    logging.getLogger(LOGGER).info(msg)


FormSilverpopAdapterSchema = FormAdapterSchema.copy() + atapi.Schema((
    atapi.StringField('apiurl',
        searchable=0,
        required=1,
        default='http://api4.silverpop.com/XMLAPI',
        validators=('isURL', ),
        widget=atapi.StringWidget(
            label = _('Silverpop API URL'),
            description = _('URL to take the Silverpop Marketer API requests'),
            ),
        ),

    atapi.StringField('listid',
        searchable=0,
        required=1,
        validators=('isInt', ),
        widget=atapi.StringWidget(
            label = _('Silverpop List Id'),
            description = _('The id of the Silverpop list'),
            ),
        ),

    DataGridField(
        'mapping',
        storage=atapi.AnnotationStorage(),
        accessor = 'get_mapping',
        edit_accessor = 'get_mapping',
        mutator = 'set_mapping',
        columns=('id', 'title', SILVERPOP_API_KEY_IDENTIFIER),
        allow_empty_rows = False,
        allow_insert=False,
        allow_reorder=False,
        allow_delete=False,
        widget = DataGridWidget(
            label=_(u"Mapping"),
            auto_insert=False,
            description=_(u"Define a mapping from PFG fields to\
                    Silverpop API Keys, like silverpop_state -> State"),
            columns= {
                "id": FixedColumn("id"),
                "title": FixedColumn("title"),
            },
         ),
     ),
))


FormSilverpopAdapterSchema['title'].storage = atapi.AnnotationStorage()
FormSilverpopAdapterSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(FormSilverpopAdapterSchema, moveDiscussion=False)


class FormSilverpopAdapter(FormActionAdapter):
    """A Form action adapter that will add a recipient to a
    Silverpop mailing list
    """
    implements(IFormSilverpopAdapter)

    meta_type = "FormSilverpopAdapter"
    schema = FormSilverpopAdapterSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    mapping = atapi.ATFieldProperty('mapping')

    get_mapping = get_mapping
    set_mapping = set_mapping

    def onSuccess(self, fields, REQUEST=None):
        """
        extract data from form,
        get settings made to the adapter itself
        construct a request to sivlerpop adding a
        recipient
        """
        data=dict()
        for f in fields:
            if f.isFileField():
                pass
            elif not f.isLabel():
                val = REQUEST.form.get(f.fgField.getName(), '')
                if not type(val) in StringTypes:
                    # Zope has marshalled the field into
                    # something other than a string
                    val = str(val)
                data[f.id] = val

        return make_request(self.apiurl, self.listid, data, fields)


atapi.registerType(FormSilverpopAdapter, PROJECTNAME)
