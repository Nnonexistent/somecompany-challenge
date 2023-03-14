from __future__ import annotations

import datetime
import uuid
from typing import List

from const import VisTypes
from pydantic import BaseModel


class User(BaseModel, frozen=True):
    id: uuid.UUID
    name: str

    entries: List[EntrySummary]

    class Config:
        orm_mode = True


class EntrySummary(BaseModel, frozen=True):
    id: uuid.UUID

    user: User

    atoms: List[Atom]
    visualizations: List[Visualization]

    class Config:
        orm_mode = True


class Atom(BaseModel, frozen=True):
    entry: EntrySummary

    date: datetime.date
    team: str
    review_time: int
    merge_time: int

    class Config:
        orm_mode = True


class Visualization(BaseModel, frozen=True):
    id: uuid.UUID

    entry: EntrySummary
    dt: datetime.datetime
    type: VisTypes

    class Config:
        orm_mode = True


User.update_forward_refs()
EntrySummary.update_forward_refs()
