# encoding:utf-8
from copy import deepcopy

from schematics.models import Model
from schematics.types import (
    StringType, IntType, DecimalType, DateTimeType, EmailType, BooleanType
)
from schematics.types.compound import ListType, ModelType
from .types import (
    PipedriveDateTime, PipedriveModelType, PipedriveDate, PipedriveTime
)


class BaseModel(Model):
    _original_data = None

    def __init__(self, raw_data=None, deserialize_mapping=None, strict=True, original_data=None):
        self._original_data = original_data
        super().__init__(raw_data, deserialize_mapping, strict)

    def get_original_data(self):
        return deepcopy(self._original_data)


class User(BaseModel):
    """
    A person in the Pipedrive ecosystem. Can be used to represent the owner of
    an activity or deal, among other things.
    """
    id = IntType(required=True)
    name = StringType()
    email = EmailType()
    active_flag = IntType(choices=(0,1), default=0)
    has_pic = BooleanType()

    def __unicode__(self):
        return self.name or str(self.id)


class Pipeline(BaseModel):
    """
    Represents one of the pipelines in the Pipedrive ecosystem.
    """
    id = IntType(required=False)
    name = StringType(required=False)
    order_nr = IntType(required=False, min_value=0)
    active = IntType(required=False, choices=(0,1))


class Stage(BaseModel):
    """
    Represents a stage in a pipeline. E.g.: open deals, lost deals, etc.
    """
    id = IntType(required=False)
    name = StringType(required=True)
    pipeline_id = PipedriveModelType(Pipeline, required=True)
    deal_probability = DecimalType(required=False)
    rotten_flag = IntType(required=False, choices=(0,1))
    rotten_days = IntType(required=False)
    order_nr = IntType(required=False, min_value=0)


class SearchResult(BaseModel):
    """
    Model for the results from search queries. Goes for both broad search and
    specific fields search, even though the response schema for those API
    methods are completely different.
    """
    id = IntType(required=False)
    type = StringType(required=False, choices=(
        'deal', 'person', 'organization', 'product', 'file'
    ))
    result = StringType(required=False)


class Organization(BaseModel):
    """
    Represents an organization (or Company, as it's called in the Loggi system).
    """
    id = IntType(required=False)
    name = StringType(required=False)
    owner_id = PipedriveModelType(User, required=False)
    visible_to = IntType(required=False, choices=(0,1,2,3))
    address = StringType(required=False)


class Deal(BaseModel):
    """
    The model for the Pipedrive deals.
    """
    title = StringType(required=True)
    id = IntType(required=False)
    value = DecimalType(required=False)
    currency = StringType(required=False)
    user_id = PipedriveModelType(User, required=False)
    # person_id = PipedriveModelType(Person, required=False)
    org_id = PipedriveModelType(Organization, required=False)
    stage_id = PipedriveModelType(Stage, required=False)
    status = StringType(required=False, choices=('open','won','lost','deleted'))
    lost_reson = StringType(required=False)
    add_time = PipedriveDateTime(required=False)
    visible_to = ListType(IntType)


class Activity(BaseModel):
    """
    Model for the activities associated to each deal.
    """
    subject = StringType(required=True)
    done = IntType(required=False)
    type = StringType(required=True)
    id = IntType(required=False)
    duration = PipedriveTime(required=False)
    user_id = PipedriveModelType(User, required=False)
    deal_id = PipedriveModelType(Deal, required=False)
    # person_id = PipedriveModelType(Person, required=False)
    org_id = PipedriveModelType(Organization, required=False)
    note = StringType(required=False)
    due_date = PipedriveDate(required=False)



class ActivityType(BaseModel):
    """
    Represents the possible types of activities.
    """
    id = IntType(required=False)
    name = StringType(required=False)
    key_string = StringType(required=False)
    icon_key = StringType(required=False)
    is_custom_flag = BooleanType(required=False)
