import datetime
import enum
import typing
from typing import List, Literal, Optional, Union

import pandas as pd
from pydantic import BaseModel, Field

from const import Columns


class DataFilterTypes(str, enum.Enum):
    TEAMS = 'teams'
    DATE_RANGE = 'date-range'


class BaseDataFilter(BaseModel):
    filter_type: DataFilterTypes

    class Config:
        frozen = True

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError


class TeamsDataFilter(BaseDataFilter):
    filter_type: Literal[DataFilterTypes.TEAMS] = DataFilterTypes.TEAMS

    teams: List[str] = Field(default_factory=list)

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.teams:
            return df
        return df[df[Columns.TEAM].isin(self.teams)]


class DateRangeDataFilter(BaseDataFilter):
    filter_type: Literal[DataFilterTypes.DATE_RANGE] = DataFilterTypes.DATE_RANGE

    start_date: Optional[datetime.date]
    end_date: Optional[datetime.date]

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.start_date:
            d = datetime.datetime.combine(self.start_date, datetime.time())
            df = df[df[Columns.DATE] >= d]
        if self.end_date:
            d = datetime.datetime.combine(self.end_date, datetime.time())
            df = df[df[Columns.DATE] <= d]
        return df


AnyDataFilter = Union[TeamsDataFilter, DateRangeDataFilter]


# check that all data filter types has relevant model
assert all(c.__fields__['filter_type'].default in DataFilterTypes for c in typing.get_args(AnyDataFilter))
assert len(DataFilterTypes) == len(typing.get_args(AnyDataFilter))
