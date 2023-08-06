from Products.Archetypes.Widget import StringWidget
from Products.Archetypes.Registry import registerWidget


class ReadonlyStringWidget(StringWidget):
    _properties = StringWidget._properties.copy()
    _properties.update({
        'macro' : "readonlystring",
        })

registerWidget(ReadonlyStringWidget,
               title='ReadonlyString',
               description=('Renders a HTML readonly text input box which '
                            'accepts a single line of text'),
               used_for=('Products.Archetypes.Field.StringField',)
               )
