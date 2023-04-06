from dotenv import load_dotenv

load_dotenv()

import tempfile
import uuid
from typing import Any, Dict, List, Optional, get_args

from fastapi import Depends, FastAPI, Response, UploadFile, status
from fastapi.exceptions import HTTPException
from sqlalchemy import and_, or_, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import Token, get_user, get_user_or_none, login
from api.models import EntrySummary, VisTypeSchema, Visualization, VisualizationCreatePayload, VisualizationWithData
from api.services import InvalidFile, df_for_entry, parse_uploaded_file
from db.orm import EntryOrm, UserOrm, VisualizationOrm
from db.utils import get_db
from vis.vis_types import AnyVisType

app = FastAPI()


@app.get('/')
def root() -> Response:
    return Response()


app.post('/api/auth/token/', response_model=Token)(login)


@app.get('/api/users/me/')
def users_me(user: UserOrm = Depends(get_user)) -> Dict[str, Any]:
    return {
        'id': user.id,
        'is_authenticated': True,
    }


@app.post('/api/entries/', status_code=201)
async def entry_create(
    payload: UploadFile,
    db: AsyncSession = Depends(get_db),
    user: UserOrm = Depends(get_user),
) -> EntrySummary:
    # TODO: make a more efficient implementation of stream usage.
    # Probably would be better without a tempfile
    with tempfile.NamedTemporaryFile(mode='wb', suffix=payload.filename) as tmp:
        tmp.write(await payload.read())
        tmp.seek(0)

        try:
            entry = parse_uploaded_file(tmp.name, user.id)
        except InvalidFile:
            raise HTTPException(422)

    db.add(entry)
    await db.commit()

    return EntrySummary.from_orm(entry)


@app.get('/api/entries/')
async def entries_list(
    db: AsyncSession = Depends(get_db),
    user: UserOrm = Depends(get_user),
) -> List[EntrySummary]:
    res = await db.execute(select(EntryOrm).where(EntryOrm.user_id == user.id))
    out = []
    for (entry,) in res.all():
        out.append(EntrySummary.from_orm(entry))
    return out


@app.get('/api/entries/{entry_id}/')
async def entry_detail(
    entry_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: UserOrm = Depends(get_user),
) -> EntrySummary:
    res = await db.execute(select(EntryOrm).where(EntryOrm.user_id == user.id, EntryOrm.id == entry_id))
    row = res.one_or_none()
    if not row:
        raise HTTPException(404)
    return EntrySummary.from_orm(row[0])


@app.delete('/api/entries/{entry_id}/')
async def entry_remove(
    entry_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: UserOrm = Depends(get_user),
) -> Response:
    res = await db.execute(select(EntryOrm).where(EntryOrm.user_id == user.id, EntryOrm.id == entry_id))
    row = res.one_or_none()
    if not row:
        raise HTTPException(404)

    await db.delete(row[0])
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post('/api/vis/')
async def vis_create(
    payload: VisualizationCreatePayload,
    db: AsyncSession = Depends(get_db),
    user: UserOrm = Depends(get_user),
) -> Visualization:
    # checking access
    res = await db.execute(select(EntryOrm).where(EntryOrm.user_id == user.id, EntryOrm.id == payload.entry_id))
    if res.one_or_none() is None:
        raise HTTPException(404, detail='Entry not found')

    vis = VisualizationOrm(**payload.dict())
    db.add(vis)
    await db.commit()

    return Visualization.from_orm(vis)


@app.get('/api/vis/')
async def vis_list(
    db: AsyncSession = Depends(get_db),
    user: UserOrm = Depends(get_user),
    entry_id: Optional[uuid.UUID] = None,
) -> List[Visualization]:
    stmt = select(VisualizationOrm).join(EntryOrm).where(EntryOrm.user_id == user.id)
    if entry_id:
        stmt = stmt.where(VisualizationOrm.entry_id == entry_id)

    res = await db.execute(stmt)
    out = []
    for row in res.all():
        out.append(Visualization.from_orm(row[0]))
    return out


@app.get('/api/vis_types/')
async def vis_types() -> List[VisTypeSchema]:
    out = []
    for vis_type_class in get_args(AnyVisType):
        out.append(VisTypeSchema(
            vis_type=vis_type_class.__fields__['vis_type'].default,
            allowed_chart_types=vis_type_class.allowed_chart_types,
        ))
    return out


@app.get('/api/vis/{vis_id}/')
async def vis_detail(
    vis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: UserOrm = Depends(get_user_or_none),
) -> VisualizationWithData:
    # checking access
    if user is None:
        filter_stmt = VisualizationOrm.is_public == True
    else:
        filter_stmt = or_(
            and_(VisualizationOrm.id == vis_id, EntryOrm.user_id == user.id),
            VisualizationOrm.is_public == True,
        )

    res = await db.execute(select(VisualizationOrm).join(EntryOrm).filter(filter_stmt))
    try:
        vis = res.one()[0]
    except NoResultFound:
        raise HTTPException(404)

    vis_model = Visualization.from_orm(vis)
    df = await df_for_entry(vis.entry_id, db)
    output = vis_model.options.apply(df)
    return VisualizationWithData(data=output, **vis_model.dict())


@app.delete('/api/vis/{vis_id}/')
async def vis_remove(
    vis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: UserOrm = Depends(get_user),
) -> Response:
    res = await db.execute(
        select(VisualizationOrm).where(
            VisualizationOrm.entry_id == EntryOrm.id,
            EntryOrm.user_id == user.id,
            VisualizationOrm.id == vis_id,
        )
    )

    row = res.one_or_none()
    if not row:
        raise HTTPException(404)
    await db.delete(row[0])
    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put('/api/vis/{vis_id}/share/')
async def vis_share(
    vis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: UserOrm = Depends(get_user),
) -> Response:
    res = await db.execute(
        select(VisualizationOrm).join(EntryOrm).where(EntryOrm.user_id == user.id, VisualizationOrm.id == vis_id)
    )
    try:
        vis = res.one()[0]
    except NoResultFound:
        raise HTTPException(404)

    vis.is_public = True
    await db.commit()

    return Response()


@app.delete('/api/vis/{vis_id}/share/')
async def vis_unshare(
    vis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: UserOrm = Depends(get_user),
) -> Response:
    res = await db.execute(
        select(VisualizationOrm).join(EntryOrm).where(EntryOrm.user_id == user.id, VisualizationOrm.id == vis_id)
    )
    try:
        vis = res.one()[0]
    except NoResultFound:
        raise HTTPException(404)

    vis.is_public = False
    await db.commit()
    return Response()
