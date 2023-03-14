import uuid
from typing import Dict, Union

import pandas as pd
import pyarrow as pa
from const import PA_COLUMN_TYPES, SUMMARY_FIELDS, SUMMARY_FUNCTIONS, CSVColumns
from db.orm import AtomOrm, EntryOrm
from models import EntrySummary
from pyarrow import csv
from sqlalchemy.orm import Session


class InvalidFile(Exception):
    pass


def parse_uploaded_file(fp: str, user_id: uuid.UUID, db: Session) -> EntrySummary:
    opts = pa.csv.ConvertOptions(column_types=PA_COLUMN_TYPES)
    try:
        df = csv.read_csv(fp, convert_options=opts).to_pandas(date_as_object=False)
    except ValueError as e:
        raise InvalidFile(e)

    _validate_data_frame(df)

    summary_stats = calc_summary(df)
    entry = EntryOrm(user_id=user_id, **summary_stats)

    for _, row in df.iterrows():
        entry.atoms.append(
            AtomOrm(
                entry_id=entry.id,
                team=row[CSVColumns.TEAM],
                date=row[CSVColumns.DATE],
                merge_time=row[CSVColumns.MERGE_TIME],
                review_time=row[CSVColumns.REVIEW_TIME],
            )
        )
    db.add(entry)
    db.commit()

    return EntrySummary.from_orm(entry)


def _validate_data_frame(df: pd.DataFrame) -> None:
    if df.size == 0:
        raise InvalidFile('No data')

    if not set(df.keys()).issuperset(CSVColumns):
        raise InvalidFile('Invalid columns')

    if df[CSVColumns.REVIEW_TIME].min() < 0:
        raise InvalidFile(f'Negative values in column "{CSVColumns.REVIEW_TIME}"')

    if df[CSVColumns.MERGE_TIME].min() < 0:
        raise InvalidFile(f'Negative values in column "{CSVColumns.MERGE_TIME}"')


def calc_summary(df: pd.DataFrame) -> Dict[str, Union[int, float]]:
    out = {
        'date_start': df[CSVColumns.DATE].min(),
        'date_end': df[CSVColumns.DATE].max(),
    }
    for field_name in SUMMARY_FIELDS:
        series = df[field_name]
        assert series.size > 0

        for suffix, func in SUMMARY_FUNCTIONS.items():
            out[f'{field_name}_{suffix}'] = func(series)

    return out
