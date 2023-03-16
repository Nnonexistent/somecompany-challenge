import uuid
from typing import TYPE_CHECKING, Any, BinaryIO, Dict, List, Union

import pandas as pd
import pyarrow as pa
from const import PA_COLUMN_TYPES, SUMMARY_FIELDS, SUMMARY_FUNCTIONS, Columns
from db.orm import AtomOrm, EntryOrm
from pyarrow import csv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from sqlalchemy.orm.attributes import InstrumentedAttribute


class InvalidFile(Exception):
    pass


def parse_uploaded_file(fp: Union[str, BinaryIO], user_id: uuid.UUID) -> EntryOrm:
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
                team=row[Columns.TEAM],
                date=row[Columns.DATE],
                merge_time=row[Columns.MERGE_TIME],
                review_time=row[Columns.REVIEW_TIME],
            )
        )
    return entry


def _validate_data_frame(df: pd.DataFrame) -> None:
    if df.size == 0:
        raise InvalidFile('No data')

    if df.duplicated([Columns.DATE, Columns.TEAM]).any():
        raise InvalidFile('Duplicated values')

    if not set(df.keys()).issuperset(Columns):
        raise InvalidFile('Invalid columns')

    if df[Columns.REVIEW_TIME].min() < 0:
        raise InvalidFile(f'Negative values in column "{Columns.REVIEW_TIME}"')

    if df[Columns.MERGE_TIME].min() < 0:
        raise InvalidFile(f'Negative values in column "{Columns.MERGE_TIME}"')


def calc_summary(df: pd.DataFrame) -> Dict[str, Union[int, float]]:
    out = {
        'date_start': df[Columns.DATE].min(),
        'date_end': df[Columns.DATE].max(),
    }
    for field_name in SUMMARY_FIELDS:
        series = df[field_name]
        assert series.size > 0

        for suffix, func in SUMMARY_FUNCTIONS.items():
            out[f'{field_name}_{suffix}'] = func(series)

    return out


def _read_sql(session: Session, sql: str, **kwargs: Any) -> pd.DataFrame:
    df = pd.read_sql_query(sql, session.connection(), **kwargs)
    assert isinstance(df, pd.DataFrame)
    return df


async def df_for_entry(entry_id: uuid.UUID, db: AsyncSession) -> pd.DataFrame:
    cols: List[InstrumentedAttribute[Any]] = [getattr(AtomOrm, col_name) for col_name in Columns]
    df = await db.run_sync(
        _read_sql,
        sql=select(*cols).where(AtomOrm.entry_id == entry_id),
        parse_dates=[Columns.DATE],
    )
    assert isinstance(df, pd.DataFrame)
    return df
