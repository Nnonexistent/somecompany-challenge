import datetime
import uuid
from typing import Any, Dict, List

from const import SUMMARY_FIELDS, SUMMARY_FUNCTIONS, Columns
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Uuid
from sqlalchemy.dialects.sqlite import JSON  # TODO: switch to postgres
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .utils import Base


class UserOrm(Base):
    __tablename__ = 'user'

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, insert_default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String())
    hashed_password: Mapped[str] = mapped_column(String())

    entries: Mapped[List['EntryOrm']] = relationship(back_populates='user', cascade='all, delete-orphan')


class EntryOrm(Base):
    __tablename__ = 'entry'

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, insert_default=uuid.uuid4)
    dt: Mapped[datetime.datetime] = mapped_column(DateTime(), insert_default=datetime.datetime.now)

    user: Mapped['UserOrm'] = relationship(back_populates='entries')
    user_id = mapped_column(ForeignKey('user.id'))

    atoms: Mapped[List['AtomOrm']] = relationship(back_populates='entry', cascade='all, delete-orphan')
    visualizations: Mapped[List['VisualizationOrm']] = relationship(
        back_populates='entry', cascade='all, delete-orphan'
    )

    date_start: Mapped[datetime.date] = mapped_column(Date())
    date_end: Mapped[datetime.date] = mapped_column(Date())

    merge_time_min: Mapped[int] = mapped_column(Integer())
    merge_time_max: Mapped[int] = mapped_column(Integer())
    merge_time_mean: Mapped[float] = mapped_column(Float())
    merge_time_median: Mapped[float] = mapped_column(Float())
    merge_time_quantile_10: Mapped[float] = mapped_column(Float())
    merge_time_quantile_90: Mapped[float] = mapped_column(Float())
    merge_time_mode: Mapped[int] = mapped_column(Integer())
    merge_time_std: Mapped[float] = mapped_column(Float())

    review_time_min: Mapped[int] = mapped_column(Integer())
    review_time_max: Mapped[int] = mapped_column(Integer())
    review_time_mean: Mapped[float] = mapped_column(Float())
    review_time_median: Mapped[float] = mapped_column(Float())
    review_time_quantile_10: Mapped[float] = mapped_column(Float())
    review_time_quantile_90: Mapped[float] = mapped_column(Float())
    review_time_mode: Mapped[int] = mapped_column(Integer())
    review_time_std: Mapped[float] = mapped_column(Float())


class AtomOrm(Base):
    __tablename__ = 'atom'

    entry: Mapped['EntryOrm'] = relationship(back_populates='atoms')
    entry_id = mapped_column(ForeignKey('entry.id'), primary_key=True)

    date: Mapped[datetime.date] = mapped_column(Date(), primary_key=True)
    team: Mapped[str] = mapped_column(String(), primary_key=True)
    review_time: Mapped[int] = mapped_column(Integer())
    merge_time: Mapped[int] = mapped_column(Integer())


class VisualizationOrm(Base):
    __tablename__ = 'visualization'

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, insert_default=uuid.uuid4)

    entry: Mapped['EntryOrm'] = relationship(back_populates='visualizations')
    entry_id = mapped_column(ForeignKey('entry.id'), primary_key=True)
    dt: Mapped[datetime.datetime] = mapped_column(DateTime(), insert_default=datetime.datetime.now)
    is_public: Mapped[bool] = mapped_column(Boolean(), default=False)

    options: Mapped[Dict[str, Any]] = mapped_column(JSON())


for field_name in SUMMARY_FIELDS:
    for suffix in SUMMARY_FUNCTIONS.keys():
        assert hasattr(EntryOrm, f'{field_name}_{suffix}')

for col in Columns:
    assert hasattr(AtomOrm, col)
