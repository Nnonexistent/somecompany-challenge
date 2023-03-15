from dotenv import load_dotenv

load_dotenv()


import tempfile
import uuid
from typing import List

from api.models import EntrySummary, Visualization, VisualizationCreatePayload, VisualizationWithData
from api.services import InvalidFile, df_for_entry, parse_uploaded_file
from db.conf import get_db
from db.orm import EntryOrm, UserOrm, VisualizationOrm
from fastapi import Depends, FastAPI, Response, UploadFile, status
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

app = FastAPI()


# DEBUG:
from db.conf import Base, engine

USER_ID = uuid.UUID('0' * 32)
Base.metadata.create_all(engine)
db = next(iter(get_db()))
db.add(UserOrm(id=USER_ID, name='Test User'))
db.commit()
# END DEBUG


@app.post('/entries/', status_code=201)
async def entry_create(payload: UploadFile, db: Session = Depends(get_db)) -> EntrySummary:
    # TODO: auth
    with tempfile.NamedTemporaryFile(mode='wb', suffix=payload.filename) as tmp:
        # TODO: optimizations
        tmp.write(await payload.read())
        tmp.seek(0)

        try:
            return parse_uploaded_file(tmp.name, USER_ID, db)
        except InvalidFile:
            raise HTTPException(422)


@app.get('/entries/')
async def entries_list(db: Session = Depends(get_db)) -> List[EntrySummary]:
    # TODO: auth
    out = []
    for entry in db.query(EntryOrm).filter(EntryOrm.user_id == USER_ID).all():
        out.append(EntrySummary.from_orm(entry))
    return out


@app.get('/entries/{entry_id}/')
async def entry_detail(entry_id: uuid.UUID, db: Session = Depends(get_db)) -> EntrySummary:
    # TODO: auth
    try:
        entry = db.query(EntryOrm).filter(EntryOrm.user_id == USER_ID, EntryOrm.id == entry_id).one()
    except NoResultFound:
        raise HTTPException(404)
    else:
        return EntrySummary.from_orm(entry)


@app.delete('/entries/{entry_id}/')
async def entry_remove(entry_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    # TODO: auth
    n = db.query(EntryOrm).filter(EntryOrm.user_id == USER_ID, EntryOrm.id == entry_id).delete()
    if n == 0:
        raise HTTPException(404)
    assert n == 1
    return Response(status.HTTP_204_NO_CONTENT)


@app.post('/vis/')
async def vis_create(payload: VisualizationCreatePayload, db: Session = Depends(get_db)) -> Visualization:
    # TODO: auth

    vis = VisualizationOrm(**payload.dict())
    db.add(vis)
    db.commit()
    db.refresh(vis)
    return Visualization.from_orm(vis)


@app.get('/vis/')
async def vis_list(db: Session = Depends(get_db)) -> List[Visualization]:
    # TODO: auth
    out = []
    for vis in db.query(VisualizationOrm).filter().all():
        out.append(Visualization.from_orm(vis))
    return out


@app.get('/vis/{vis_id}/')
async def vis_detail(vis_id: uuid.UUID, db: Session = Depends(get_db)) -> VisualizationWithData:
    # TODO: auth
    try:
        vis = db.query(VisualizationOrm).filter(VisualizationOrm.id == vis_id).one()
    except NoResultFound:
        raise HTTPException(404)

    vis_model = Visualization.from_orm(vis)
    df = df_for_entry(vis.entry_id, db)
    output = vis_model.options.apply(df)
    return VisualizationWithData(data=output, **vis_model.dict())


@app.delete('/vis/{vis_id}/')
async def vis_remove(vis_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    # TODO: auth
    n = db.query(VisualizationOrm).filter(VisualizationOrm.id == vis_id).delete()
    if n == 0:
        raise HTTPException(404)
    assert n == 1
    return Response(status.HTTP_204_NO_CONTENT)
