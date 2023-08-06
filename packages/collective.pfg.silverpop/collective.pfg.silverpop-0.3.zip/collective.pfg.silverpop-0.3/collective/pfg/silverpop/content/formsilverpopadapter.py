"""Definition of the FormSilverpopAdapter content type
"""

import logging

from types import StringTypes

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata

from Products.PloneFormGen.content.actionAdapter import \
    FormActionAdapter, FormAdapterSchema

from collective.pfg.silverpop import silverpopMessageFactory as _
from collective.pfg.silverpop.interfaces import IFormSilverpopAdapter
from collective.pfg.silverpop.config import PROJECTNAME
from collective.pfg.silverpop.utilities import make_request

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

        make_request(self.apiurl, self.listid, data)


atapi.registerType(FormSilverpopAdapter, PROJECTNAME)
