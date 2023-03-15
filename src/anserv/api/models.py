from __future__ import annotations

import datetime
import uuid
from typing import List

from const import SUMMARY_FIELDS, SUMMARY_FUNCTIONS
from pydantic import BaseModel, Field
from vis.output import AnyOutputEntry
from vis.vis_types import AnyVisType


class EntrySummary(BaseModel):
    id: uuid.UUID

    date_start: datetime.date
    date_end: datetime.date

    merge_time_min: int
    merge_time_max: int
    merge_time_mean: float
    merge_time_median: float
    merge_time_quantile_10: float
    merge_time_quantile_90: float
    merge_time_mode: int
    merge_time_std: float

    review_time_min: int
    review_time_max: int
    review_time_mean: float
    review_time_median: float
    review_time_quantile_10: float
    review_time_quantile_90: float
    review_time_mode: int
    review_time_std: float

    class Config:
        frozen = True
        orm_mode = True


class Visualization(BaseModel):
    id: uuid.UUID

    entry: EntrySummary
    dt: datetime.datetime
    is_public: bool
    options: AnyVisType = Field(discriminator='vis_type')

    class Config:
        frozen = True
        orm_mode = True


class VisualizationWithData(Visualization):
    data = List[AnyOutputEntry]

    class Config:
        frozen = True
        orm_mode = False


for field_name in SUMMARY_FIELDS:
    for suffix in SUMMARY_FUNCTIONS.keys():
        assert f'{field_name}_{suffix}' in EntrySummary.__fields__
