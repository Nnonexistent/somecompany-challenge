import datetime
import enum
import typing
from typing import List, Literal, Optional, Union

import pandas as pd
from pydantic import BaseModel, Field


class DataFilterTypes(str, enum.Enum):
    TEAMS = 'teams'
    DATE_RANGE = 'date-range'


class BaseDataFilter(BaseModel, frozen=True):
    filter_type: DataFilterTypes

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError


class TeamsDataFilter(BaseDataFilter):
    filter_type: Literal[DataFilterTypes.TEAMS] = DataFilterTypes.TEAMS
    teams: List[str] = Field(default_factory=list)


class DateRangeDataFilter(BaseDataFilter):
    filter_type: Literal[DataFilterTypes.DATE_RANGE] = DataFilterTypes.DATE_RANGE
    start_date: Optional[datetime.date]
    end_date: Optional[datetime.date]


AnyDataFilter = Union[TeamsDataFilter, DateRangeDataFilter]


# check that all data filter types has relevant model
assert all(c.__fields__['type'].default in DataFilterTypes for c in typing.get_args(AnyDataFilter))
assert len(DataFilterTypes) == len(typing.get_args(AnyDataFilter))
