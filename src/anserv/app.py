from dotenv import load_dotenv

load_dotenv()


import uuid
from typing import List

from conf import orm_engine
from fastapi import FastAPI, UploadFile
from fastapi.exceptions import HTTPException
from models import EntrySummary
from orm import Base, EntryOrm, UserOrm
from services import InvalidFile, parse_uploaded_file
from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session

app = FastAPI()


# DEBUG:
USER_ID = uuid.UUID('0*32')
Base.metadata.create_all(orm_engine)
with orm_engine.connect() as conn:
    result = conn.execute(insert(UserOrm).values(id=USER_ID, name='Test User'))
    conn.commit()
# END DEBUG


@app.post('/entries/', status_code=201)
async def new_entry(uploaded: UploadFile) -> EntrySummary:
    try:
        return parse_uploaded_file(uploaded, user_id=USER_ID)
    except InvalidFile:
        raise HTTPException(422)


@app.get('/entries/')
async def entries_list() -> List[EntrySummary]:
    out = []
    with Session(orm_engine) as session:
        for (entry,) in session.execute(select(EntryOrm).where(EntryOrm.user_id == USER_ID)):
            out.append(entry)
    return out


@app.get('/entries/{entry_id}/')
async def entries_detail(entry_id: uuid.UUID) -> EntrySummary:
    with Session(orm_engine) as session:
        for (entry,) in session.execute(select(EntryOrm).where(EntryOrm.user_id == USER_ID, EntryOrm.id == entry_id)):
            return EntrySummary.from_orm(entry)
    raise HTTPException(404)


@app.delete('/entries/{entry_id}/')
async def entries_remove(entry_id: uuid.UUID) -> None:
    with Session(orm_engine) as session:
        session.execute(delete(EntryOrm).where(EntryOrm.user_id == USER_ID, EntryOrm.id == entry_id))
        session.commit()
    raise HTTPException(404)
