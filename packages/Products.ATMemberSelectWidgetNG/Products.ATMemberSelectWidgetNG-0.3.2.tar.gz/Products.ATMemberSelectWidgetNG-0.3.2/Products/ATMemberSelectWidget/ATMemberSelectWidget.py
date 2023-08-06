import types

from Globals import InitializeClass
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget,registerPropertyType
from AccessControl import ClassSecurityInfo
from Products.Archetypes.utils import shasattr

class MemberSelectWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro' : "memberselect",
        'helper_js': ('memberselect.js',),
        'size': 8,
        'fieldType':'id', # ['nameemail'|'email'|'id']
        'groupName':'',
        'showGroups': True, # show "Search in Group" in popup
        'enableSearch':1,
        'close_window':-1,
        'show_fullname': 0, # show fullname instead of member id in the widget view macro
        'link_to_home': 0, # if set, member id/fullname in view macro will be hyperlink to 
                           # member's home folder
        })

    security = ClassSecurityInfo()    

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker=None, emptyReturnsMarker=None,):

        result = TypesWidget.process_form (self, instance, field, 
                form, empty_marker, emptyReturnsMarker, )

        if result is empty_marker:
            return result

        value, kwargs = result

        # The widget always returns a empty item (strange) when we use the multival option.
        # Remove the empty items manually
        if type(value) is types.ListType:
            value = [item for item in value if item]

        return value, kwargs

registerWidget(MemberSelectWidget,
               title='Member Select',
               description=('You can select portal members searched from a popup window.'),
               used_for=('Products.Archetypes.Field.LinesField',
	                 'Products.Archetypes.Field.StringField', )
               )
