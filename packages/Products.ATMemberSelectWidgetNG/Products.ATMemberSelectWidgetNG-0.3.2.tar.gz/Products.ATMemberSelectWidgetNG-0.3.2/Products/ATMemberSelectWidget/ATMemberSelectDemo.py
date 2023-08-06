""" demonstrates the use of ATMemberSelectWidget """

from Products.Archetypes.public import *
from Products.ATMemberSelectWidget.ATMemberSelectWidget import *
from DateTime import DateTime


schema = BaseSchema +  Schema((
    StringField('singleMember', 
                 widget=MemberSelectWidget() ),
    StringField('singleMemberEmail',
                 widget=MemberSelectWidget(fieldType="email") ),
    LinesField('multiMember',
                multiValued=1,
                widget=MemberSelectWidget()) ,
   LinesField('multiMemberEmail',
             multiValued=1,
        widget=MemberSelectWidget(fieldType="email")) ,

                              ))

class ATMemberSelectDemo(BaseContent):
    """
    Demo from ATMemberSelectWidget
    """
    content_icon = "document_icon.gif"
    schema = schema

registerType(ATMemberSelectDemo)
