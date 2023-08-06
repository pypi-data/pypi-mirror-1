from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Field import Field
from Products.Archetypes.Field import ObjectField
from Products.Archetypes.Registry import registerField
from archetypes.recurringdate.widget import RecurringDateWidget
from archetypes.recurringdate.recurrence import RecurringData


class RecurringDateField(ObjectField):
    """A field that stores recurring dates."""
    __implements__ = ObjectField.__implements__

    _properties = Field._properties.copy()
    _properties.update({
        'type': 'object',
        'widget': RecurringDateWidget,
        })

    security = ClassSecurityInfo()

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        """Check if value is an actual RecurringData object. If not,
        attempt to convert it to one; otherwise set to None. Assign
        all properties passed as kwargs to the object.
        """
        if not value:
            value = None
        elif not isinstance(value, RecurringData):
            value = RecurringData(**kwargs)

        ObjectField.set(self, instance, value)


InitializeClass(RecurringDateField)

registerField(RecurringDateField,
              title='Recurring Date',
              description='Used to store recuring dates data.')
