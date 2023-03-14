import uuid

import pandas as pd
from conf import orm_engine
from models import EntrySummary
from orm import AtomOrm, EntryOrm
from pandas.core.dtypes.common import is_numeric_dtype, is_string_or_object_np_dtype
from pyarrow import csv
from sqlalchemy import insert


class InvalidFile(Exception):
    pass


def parse_uploaded_file(fp, user_id: uuid.UUID) -> EntrySummary:  # TODO: protocol for fp?
    try:
        df = csv.read_csv(fp).to_pandas()
    except ValueError as e:
        raise InvalidFile(e)

    _validate_data_frame(df)

    with orm_engine.connect() as conn:
        (entry_id,) = conn.execute(insert(EntryOrm).values(user_id=user_id))
        for row in df.iterrows():
            AtomOrm(
                entry_id=entry_id,
                review_time=row[0],
                team=row[1],
                date=row[2],
                merge_time=row[3],
            )
        conn.commit()

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
