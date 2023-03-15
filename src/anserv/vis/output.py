import datetime
from typing import Union

from const import MeasureTypes
from pydantic import BaseModel


class BaseOutputEntry(BaseModel, frozen=True):
    pass


class DateByTypeOutputEntry(BaseOutputEntry):
    date: datetime.date
    value: int
    type: MeasureTypes
    team: str


class ReviewOverMergeOutputEntry(BaseOutputEntry):
    merge_value: int
    review_value: int
    team: str
    date: datetime.date


class ReviewMergeRatioEntry(BaseOutputEntry):
    value: int
    type: MeasureTypes
    team: str


AnyOutputEntry = Union[DateByTypeOutputEntry, ReviewOverMergeOutputEntry, ReviewMergeRatioEntry]