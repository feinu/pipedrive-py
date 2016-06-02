# encoding:utf-8
import datetime

from collections import Iterable
from schematics.types import DateType, BaseType
from schematics.exceptions import ConversionError
from base import dict_to_model


class PipedriveDate(DateType):
    def to_native(self, value, context=None):
        return datetime.datetime.strptime(value, "%Y-%m-%d")


class PipedriveTime(DateType):
    def to_native(self, value, context=None):
        if value.find(':') < 0:
            return 0

        minutes, seconds = [int(x) for x in value.split(':')]
        return minutes * 60 + seconds

    def to_primitive(self, value, context=None):
        minutes, seconds = divmod(value, 60)
        return "%s:%s" % (minutes, seconds)


class PipedriveDateTime(DateType):
    def to_native(self, value, context=None):
        return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


class PipedriveModelType(BaseType):
    """
    Sometimes, in the JSON responses sent by the Pipedrive api there's a dict
    where a numeric id should be - e.g. in the Deal response, the user_id field
    holds the actual user data instead of the user's numeric id.

    For the sake of consistency, those fields should be set to be a
    PipedriveModelType field. It works like ModelType, with a few differences:

    - Fields of this type can receive an int value - in this case, a new object
      of the model type is created and stored in the field, and the passed value
      becomes the object's id.

    - Fields of this type can receive a dict with the object's data, which will
      then be converted to the model type through dict_to_model.

    - When an object is converted to a dict, PipedriveModelType fields will hold
      only the object's numeric id.

    This way, our models can communicate seamlessly with the Pipedrive api.

    Last but not least: the natural solution would be having PipedriveModelType
    extend ModelType, but for an undisclosed reason (a bug, maybe?), the
    to_primitive method in the ModelType class never seems to be called. So,
    we extend BaseType directly. It's not as robust as ModelType, but it's
    strong enough for our needs.

    """
    MESSAGES = {
        'value_type': 'Value must be of type %s, dict or int'
    }

    def __init__(self, model_class, *args, **kwargs):
        super(PipedriveModelType, self).__init__(*args, **kwargs)
        self.model_class = model_class

    def to_native(self, value, context=None):
        if isinstance(value, self.model_class):
            return value

        if isinstance(value, int):
            return self.model_class({'id': value})

        if isinstance(value, dict):
            return dict_to_model(value, self.model_class)

        raise ConversionError(self.messages['value_type'] % self.model_class)

    def to_primitive(self, value, context=None):
        if isinstance(value, self.model_class):
            return value.id

        if isinstance(value, dict):
            return value['id']

        return value


class PipedriveListDictStringOrStringType(BaseType):
    """
    Can be used as a base class for fields that receive different formats (list with dicts with strings or just
    a string) from the Pipedrive API.

    Pipedrive inconsistently returns values for some fields, for example: "find" for a Person just returns a string
    for email even if there are multiple emails associated with that Person. "detail" for a Person returns a list
    containing a dict containing strings for emails. Because of this inconsistency we need to have a field that can
    return the correct values even if the way they are represented changes. We are opting for the list-dict-string
    because this allows us to better control these multiple values (email addresses, phone numbers etc.).
    """
    def to_native(self, value, context=None):
        if isinstance(value, list):
            return value
        elif is_string(value):
            return [{'value': value}]

    def to_primitive(self, value, context=None):
        # Pipedrive can't handle iterable objects (dicts, lists, sets, etc.) so we throw an error if we encounter
        # one during updating or creation. Fun fact: Pipedrive can return iterable objects, but can't receive them.
        # So when you, for example, get a person with multiple email addresses and try to update his name Pipedrive
        # will screw up his email addresses. In that case it's just better to update manually or specify None for
        # the email addresses (which means it won't update them at all).
        if not is_string(value) and isinstance(value, Iterable):
            raise ValueError("Pipedrive can't handle iterable objects. You can either specify one value of type base"
                             "string which will update the first record, or specify None which won't update anything")
        return value


class PipedriveEmailType(PipedriveListDictStringOrStringType):
    """
    Use this field type for models that can have multiple email addresses associated with them, such as Persons.
    We're just using these, because they're more clear than the parent's name.

    For more information see the parent's docstring.
    """
    pass


class PipedrivePhonenumberType(PipedriveListDictStringOrStringType):
    """
    Use this field type for models that can have multiple phone numbers associated with them, such as Persons.
    We're just using these, because they're more clear than the parent's name.

    For more information see the parent's docstring.
    """
    pass


def is_string(value):
    """
    Check if value is a string. Python 2 and 3 compatible.
    """
    try:
        return isinstance(value, basestring)
    except NameError:
        return isinstance(value, str)
