import enum
import typing
from typing import ClassVar, List, Literal, Union

import pandas as pd
from const import MT2COL, ChartTypes, Columns, MeasureTypes, VisTypes
from pydantic import BaseModel, Field, validator
from typing_extensions import Annotated, Type

from .filters import AnyDataFilter
from .output import AnyOutputEntry, DateByTypeOutputEntry, ReviewMergeRatioOutputEntry, ReviewOverMergeOutputEntry


class BaseVis(BaseModel):
    allowed_chart_types: ClassVar[List[ChartTypes]]
    output_format: ClassVar[Type[AnyOutputEntry]]

    vis_type: VisTypes
    chart_type: ChartTypes
    filters: List[Annotated[AnyDataFilter, Field(discriminator='filter_type')]] = Field(default_factory=list)

    class Config:
        frozen = True

    @validator('chart_type')
    def chart_type_is_allowed(cls, v: str) -> str:
        if v not in cls.allowed_chart_types:
            raise ValueError('Specified chart type is not allowed')
        return v

    def apply(self, df: pd.DataFrame) -> List[AnyOutputEntry]:
        for filter in self.filters:
            df = filter.apply(df)

        out = self.make_output(df)
        assert not out or isinstance(out[0], self.output_format)
        return out

    def make_output(self, df: pd.DataFrame) -> List[AnyOutputEntry]:
        raise NotImplementedError


class DateResolution(str, enum.Enum):
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'


RES_TO_FREQ = {
    DateResolution.DAY: 'D',
    DateResolution.WEEK: 'W-MON',
    DateResolution.MONTH: 'M',
}


class DateByTypeVis(BaseVis):
    allowed_chart_types = [ChartTypes.LINE, ChartTypes.BAR, ChartTypes.STACKED]
    output_format = DateByTypeOutputEntry

    vis_type: Literal[VisTypes.DATE_BY_TYPE] = VisTypes.DATE_BY_TYPE
    date_resolution: DateResolution

    def make_output(self, df: pd.DataFrame) -> List[DateByTypeOutputEntry]:  # FIXME: typing
        out = []

        freq = RES_TO_FREQ[self.date_resolution]
        grouped = df.groupby([pd.Grouper(key=Columns.DATE, freq=freq), Columns.TEAM]).sum()

        for mt in MeasureTypes:
            for indexes, value in grouped[MT2COL[mt]].items():
                assert isinstance(indexes, tuple)  # typing
                idate, team = indexes
                out.append(
                    DateByTypeOutputEntry(
                        date=idate.date(),
                        value=value,
                        type=mt,
                        team=team,
                    )
                )

        return out


class ReviewOverMergeVis(BaseVis):
    allowed_chart_types = [ChartTypes.SCATTER]
    output_format = ReviewOverMergeOutputEntry

    vis_type: Literal[VisTypes.REVIEW_OVER_MERGE] = VisTypes.REVIEW_OVER_MERGE

    def make_output(self, df: pd.DataFrame) -> List[ReviewOverMergeOutputEntry]:  # FIXME: typing
        out = []
        for _, row in df.iterrows():
            out.append(
                ReviewOverMergeOutputEntry(
                    merge_value=row[Columns.MERGE_TIME],
                    review_value=row[Columns.REVIEW_TIME],
                    team=row[Columns.TEAM],
                    date=row[Columns.DATE],
                )
            )
        return out


class ReviewMergeRatioVis(BaseVis):
    allowed_chart_types = [ChartTypes.SCATTER]
    output_format = ReviewMergeRatioOutputEntry

    vis_type: Literal[VisTypes.REVIEW_MERGE_RATIO] = VisTypes.REVIEW_MERGE_RATIO

    def make_output(self, df: pd.DataFrame) -> List[ReviewMergeRatioOutputEntry]:  # FIXME: typing
        out = []

        grouped = df.groupby(Columns.TEAM).sum()  # FIXME: pandas deprecation

        for mt in MeasureTypes:
            for team, value in grouped[MT2COL[mt]].items():
                assert isinstance(team, str)  # typing
                out.append(
                    ReviewMergeRatioOutputEntry(
                        team=team,
                        type=mt,
                        value=value,
                    )
                )
        return out


AnyVisType = Union[DateByTypeVis, ReviewOverMergeVis, ReviewMergeRatioVis]


# check that all vis types has relevant model
assert all(c.__fields__['vis_type'].default in VisTypes for c in typing.get_args(AnyVisType))
assert len(VisTypes) == len(typing.get_args(AnyVisType))
