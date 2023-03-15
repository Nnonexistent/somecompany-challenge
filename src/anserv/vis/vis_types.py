import enum
import typing
from typing import ClassVar, List, Literal, Union

import pandas as pd
from const import ChartTypes, VisTypes
from pydantic import BaseModel, Field
from typing_extensions import Annotated, Type

from .filters import AnyDataFilter
from .output import AnyOutputEntry


class BaseVis(BaseModel, frozen=True):
    allowed_chart_types: ClassVar[List[ChartTypes]]
    output_format: ClassVar[Type[AnyOutputEntry]]

    vis_type: VisTypes
    chart_type: ChartTypes
    filters: List[Annotated[AnyDataFilter, Field(discriminator='filter_type')]]

    # TODO: validate chart type by allowed_chart_types

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


class DateByTypeVis(BaseVis):
    allowed_chart_types = [ChartTypes.LINE, ChartTypes.BAR, ChartTypes.STACKED]

    vis_type: Literal[VisTypes.DATE_BY_TYPE] = VisTypes.DATE_BY_TYPE
    date_resolution: DateResolution


class ReviewOverMergeVis(BaseVis):
    allowed_chart_types = [ChartTypes.SCATTER]

    vis_type: Literal[VisTypes.REVIEW_OVER_MERGE] = VisTypes.REVIEW_OVER_MERGE


class ReviewMergeRationVis(BaseVis):
    allowed_chart_types = [ChartTypes.SCATTER]

    vis_type: Literal[VisTypes.REVIEW_MERGE_RATIO] = VisTypes.REVIEW_MERGE_RATIO


AnyVisType = Union[DateByTypeVis, ReviewOverMergeVis, ReviewMergeRationVis]


# check that all vis types has relevant model
assert all(c.__fields__['vis_type'].default in VisTypes for c in typing.get_args(AnyVisType))
assert len(VisTypes) == len(typing.get_args(AnyVisType))
