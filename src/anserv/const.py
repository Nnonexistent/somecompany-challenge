from __future__ import annotations

import enum
from typing import Callable, Dict, Union

import pandas as pd
import pyarrow as pa


class VisTypes(str, enum.Enum):
    DATE_BY_TYPE = 'daily-by-type'
    REVIEW_OVER_MERGE = 'review-over-merge'
    REVIEW_MERGE_RATIO = 'review-merge-ratio'


class ChartTypes(str, enum.Enum):
    LINE = 'line'
    BAR = 'bar'
    STACKED = 'stacked'
    SCATTER = 'scatter'
    PIE = 'pie'


class CSVColumns(str, enum.Enum):
    REVIEW_TIME = 'review_time'
    TEAM = 'team'
    DATE = 'date'
    MERGE_TIME = 'merge_time'


class MeasureTypes(str, enum.Enum):
    REVIEW = 'review'
    MERGE = 'merge'


PA_COLUMN_TYPES = {
    CSVColumns.REVIEW_TIME: pa.int32(),
    CSVColumns.TEAM: pa.string(),
    CSVColumns.DATE: pa.date32(),
    CSVColumns.MERGE_TIME: pa.int32(),
}
SUMMARY_FIELDS = [CSVColumns.MERGE_TIME, CSVColumns.REVIEW_TIME]
SUMMARY_FUNCTIONS: Dict[str, Callable[[pd.Series[int]], Union[int, float]]] = {
    'min': lambda s: int(s.min()),
    'max': lambda s: int(s.max()),
    'mean': lambda s: s.mean(),
    'median': lambda s: s.median(),
    'quantile_10': lambda s: s.quantile(0.1),
    'quantile_90': lambda s: s.quantile(0.9),
    'mode': lambda s: int(s.mode()[0]),
    'std': lambda s: s.std(),
}
