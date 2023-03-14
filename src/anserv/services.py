import uuid

import pandas as pd
from models import EntrySummary
from pandas.core.dtypes.common import is_numeric_dtype, is_string_or_object_np_dtype
from pyarrow import csv
from sqlalchemy.orm import Session

from db.orm import AtomOrm, EntryOrm


class InvalidFile(Exception):
    pass


def parse_uploaded_file(fp, user_id: uuid.UUID, db: Session) -> EntrySummary:  # TODO: protocol for fp?
    try:
        df = csv.read_csv(fp).to_pandas()
    except ValueError as e:
        raise InvalidFile(e)

    _validate_data_frame(df)

    entry = EntryOrm(user_id=user_id)
    db.add(entry)

    for row in df.iterrows():
        db.add(
            AtomOrm(
                entry_id=entry.id,
                review_time=row[0],
                team=row[1],
                date=row[2],
                merge_time=row[3],
            )
        )
    db.commit()

    orm_obj = EntryOrm()
    return EntrySummary.from_orm(orm_obj)


def _validate_data_frame(df: pd.DataFrame) -> None:
    if len(df.dtypes) < 4:
        raise InvalidFile

    if not is_numeric_dtype(df.dtype[0]):
        raise InvalidFile

    if not is_string_or_object_np_dtype(df.dtype[1]):
        raise InvalidFile

    if not is_string_or_object_np_dtype(df.dtype[2]):
        raise InvalidFile

    if not is_numeric_dtype(df.dtype[3]):
        raise InvalidFile

    if df[0].min() < 0:
        raise InvalidFile

    if df[3].min() < 0:
        raise InvalidFile
