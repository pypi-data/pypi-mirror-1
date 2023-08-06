from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import StringWidget
from Products.Archetypes.Registry import registerWidget

class RecordWidget(StringWidget):
    _properties = StringWidget._properties.copy()
    _properties.update({
        'macro' : "record_widget",
        })
    security = ClassSecurityInfo()

InitializeClass(RecordWidget)

registerWidget(RecordWidget,
               title='Record',
               description="Renders a group of subfields.",
               used_for=('Products.ATExtensions.fields.RecordField',)
               )
