import datetime
from typing import Union

from pydantic import BaseModel

from const import MeasureTypes


class BaseOutputEntry(BaseModel):
    class Config:
        frozen = True


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


class ReviewMergeRatioOutputEntry(BaseOutputEntry):
    value: int
    type: MeasureTypes
    team: str


AnyOutputEntry = Union[DateByTypeOutputEntry, ReviewOverMergeOutputEntry, ReviewMergeRatioOutputEntry]
