from dotenv import load_dotenv

load_dotenv()

import tempfile
import uuid
from typing import List

from api.models import EntrySummary, Visualization, VisualizationCreatePayload, VisualizationWithData
from api.services import InvalidFile, df_for_entry, parse_uploaded_file
from auth import Token, get_user, get_user_or_none, login
from db.orm import EntryOrm, UserOrm, VisualizationOrm
from db.utils import get_db
from fastapi import Depends, FastAPI, Response, UploadFile, status
from fastapi.exceptions import HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

app = FastAPI()


from auth import get_password_hash

# DEBUG:
from db.utils import Base, SessionLocal, engine

USER_ID = uuid.UUID('0' * 32)
Base.metadata.create_all(engine)
with SessionLocal() as db:
    db.add(UserOrm(id=USER_ID, name='Test User', hashed_password=get_password_hash('123')))
    db.commit()
# END DEBUG


app.post('/auth/token', response_model=Token)(login)  # FIXME: registration


@app.post('/entries/', status_code=201)
async def entry_create(
    payload: UploadFile,
    db: Session = Depends(get_db),
    user: UserOrm = Depends(get_user),
) -> EntrySummary:
    # TODO: make a more efficient implementation of stream usage.
    # Probably would be better without a tempfile
    with tempfile.NamedTemporaryFile(mode='wb', suffix=payload.filename) as tmp:
        tmp.write(await payload.read())
        tmp.seek(0)

        try:
            return parse_uploaded_file(tmp.name, user.id, db)
        except InvalidFile:
            raise HTTPException(422)


@app.get('/entries/')
async def entries_list(
    db: Session = Depends(get_db),
    user: UserOrm = Depends(get_user),
) -> List[EntrySummary]:
    out = []
    for entry in db.query(EntryOrm).filter(EntryOrm.user_id == user.id).all():
        out.append(EntrySummary.from_orm(entry))
    return out


@app.get('/entries/{entry_id}/')
async def entry_detail(
    entry_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: UserOrm = Depends(get_user),
) -> EntrySummary:
    try:
        entry = db.query(EntryOrm).filter(EntryOrm.user_id == user.id, EntryOrm.id == entry_id).one()
    except NoResultFound:
        raise HTTPException(404)
    else:
        return EntrySummary.from_orm(entry)


@app.delete('/entries/{entry_id}/')
async def entry_remove(
    entry_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: UserOrm = Depends(get_user),
) -> Response:
    n = db.query(EntryOrm).filter(EntryOrm.user_id == user.id, EntryOrm.id == entry_id).delete()
    if n == 0:
        raise HTTPException(404)
    assert n == 1
    return Response(status.HTTP_204_NO_CONTENT)


@app.post('/vis/')
async def vis_create(
    payload: VisualizationCreatePayload,
    db: Session = Depends(get_db),
    user: UserOrm = Depends(get_user),
) -> Visualization:
    # checking access
    try:
        db.query(EntryOrm).filter(EntryOrm.user_id == user.id, EntryOrm.id == payload.entry_id).one()
    except NoResultFound:
        raise HTTPException(404, detail='Entry not found')

    vis = VisualizationOrm(**payload.dict())
    db.add(vis)
    db.commit()
    db.refresh(vis)
    return Visualization.from_orm(vis)


@app.get('/vis/')
async def vis_list(
    db: Session = Depends(get_db),
    user: UserOrm = Depends(get_user),
) -> List[Visualization]:
    out = []
    for vis in db.query(VisualizationOrm).join(EntryOrm).filter(EntryOrm.user_id == user.id).all():
        out.append(Visualization.from_orm(vis))
    return out


@app.get('/vis/{vis_id}/')
async def vis_detail(
    vis_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: UserOrm = Depends(get_user_or_none),
) -> VisualizationWithData:
    # checking access
    try:
        vis = (
            db.query(VisualizationOrm)
            .join(EntryOrm)
            .filter(
                or_(
                    and_(VisualizationOrm.id == vis_id, EntryOrm.user_id == user.id),
                    VisualizationOrm.is_public == True,
                )
            )
            .one()
        )
    except NoResultFound:
        raise HTTPException(404)

    vis_model = Visualization.from_orm(vis)
    df = df_for_entry(vis.entry_id, db)
    output = vis_model.options.apply(df)
    return VisualizationWithData(data=output, **vis_model.dict())


@app.delete('/vis/{vis_id}/')
async def vis_remove(
    vis_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: UserOrm = Depends(get_user),
) -> Response:

    n = (
        db.query(VisualizationOrm)
        .join(EntryOrm)
        .filter(EntryOrm.user_id == user.id, VisualizationOrm.id == vis_id)
        .delete()
    )
    if n == 0:
        raise HTTPException(404)
    assert n == 1
    return Response(status.HTTP_204_NO_CONTENT)


@app.put('/vis/{vis_id}/share/')
async def vis_share(
    vis_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: UserOrm = Depends(get_user),
) -> Response:
    try:
        vis = (
            db.query(VisualizationOrm)
            .join(EntryOrm)
            .filter(EntryOrm.user_id == user.id, VisualizationOrm.id == vis_id)
            .one()
        )
    except NoResultFound:
        raise HTTPException(404)

    vis.is_public = True
    db.commit()
    return Response()


@app.delete('/vis/{vis_id}/share/')
async def vis_unshare(
    vis_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: UserOrm = Depends(get_user),
) -> Response:
    try:
        vis = (
            db.query(VisualizationOrm)
            .join(EntryOrm)
            .filter(EntryOrm.user_id == user.id, VisualizationOrm.id == vis_id)
            .one()
        )
    except NoResultFound:
        raise HTTPException(404)

    vis.is_public = False
    db.commit()
    return Response()
