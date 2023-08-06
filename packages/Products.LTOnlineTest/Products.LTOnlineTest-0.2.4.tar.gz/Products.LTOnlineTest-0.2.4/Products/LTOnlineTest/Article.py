from Products.Archetypes.public import BaseSchema, Schema
from Products.Archetypes.public import StringField, TextField
from Products.Archetypes.public import SelectionWidget, TextAreaWidget
from Products.Archetypes.public import RichWidget
from Products.Archetypes.public import BaseContent, registerType
from Products.Archetypes.Marshall import PrimaryFieldMarshaller

# BBB for CMF < 2.1
try:
    from Products.CMFCore import permissions as CMFCorePermissions
except ImportError:
    from Products.CMFCore import CMFCorePermissions

from config import PROJECTNAME

schema = BaseSchema +  Schema((
    StringField('question',
                widget=TextAreaWidget(),
                ),
    StringField('blurb',
                searchable=1,
                widget=TextAreaWidget(),
                ),
    TextField('body',
              searchable=1,
              required=1,
              primary=1,
              default_output_type='text/html',
              allowable_content_types=('text/plain',
                                       'text/structured',
                                       'text/restructured',
                                       'text/html',
                                       'application/msword'),
              widget=RichWidget(label='Body'),
              ),
    ),
                              marshall=PrimaryFieldMarshaller(),
                              )

class Article(BaseContent):
    """This is a sample article, it has an overridden view for show,
    but this is purely optional
    """

    schema = schema

    actions = ({
        'id': 'view',
        'name': 'View',
        'action': 'string:${object_url}/article_view',
        'permissions': (CMFCorePermissions.View,)
        },)

registerType(Article, PROJECTNAME)
