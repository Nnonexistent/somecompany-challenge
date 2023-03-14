import datetime
import uuid
from typing import List

from const import VisTypes
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .conf import Base


class UserOrm(Base):
    __tablename__ = 'user'

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, insert_default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String())

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
    type: Mapped[VisTypes] = mapped_column(Integer)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)

    path: Mapped[str] = mapped_column(String(255))
