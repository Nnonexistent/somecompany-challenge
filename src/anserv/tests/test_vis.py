from typing import Any, Callable

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.orm import EntryOrm, UserOrm, VisualizationOrm

from .conftest import TokenAuth


def test_vis_listing(
    api_client: TestClient,
    get_auth: Callable[[str, str], TokenAuth],
    vis_factory: Callable[..., VisualizationOrm],
    entry_factory: Callable[..., EntryOrm],
    user_factory: Callable[..., UserOrm],
) -> None:
    user = user_factory('user', 'qwe123')
    entry_1 = entry_factory(user=user)
    entry_2 = entry_factory(user=user)
    vis_factory(entry=entry_1)
    vis_factory(entry=entry_2)

    with api_client as client:
        response = client.get('/api/vis/', auth=get_auth('user', 'qwe123'))

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_vis_listing_filter(
    api_client: TestClient,
    get_auth: Callable[[str, str], TokenAuth],
    vis_factory: Callable[..., VisualizationOrm],
    entry_factory: Callable[..., EntryOrm],
    user_factory: Callable[..., UserOrm],
) -> None:
    user = user_factory('user', 'qwe123')
    entry = entry_factory(user=user)
    other_entry = entry_factory(user=user)
    vis = vis_factory(entry=entry)
    vis_factory(entry=other_entry)

    with api_client as client:
        response = client.get(f'/api/vis/?entry_id={entry.id}', auth=get_auth('user', 'qwe123'))

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['id'] == str(vis.id)


def test_vis_listing_other(
    api_client: TestClient,
    get_auth: Callable[[str, str], TokenAuth],
    vis_factory: Callable[..., VisualizationOrm],
    user_factory: Callable[..., UserOrm],
) -> None:
    user_factory('other')
    vis_factory()

    with api_client as client:
        response = client.get('/api/vis/', auth=get_auth('other', 'qwe123'))

    assert response.status_code == 200
    assert len(response.json()) == 0


def test_vis_detail(
    api_client: TestClient,
    get_auth: Callable[[str, str], TokenAuth],
    vis_factory: Callable[..., VisualizationOrm],
) -> None:
    vis = vis_factory()
    with api_client as client:
        response = client.get(f'/api/vis/{vis.id}/', auth=get_auth('user', 'qwe123'))

    assert response.status_code == 200
    assert response.json()['id'] == str(vis.id)
    assert 'data' in response.json()


def test_vis_remove(
    api_client: TestClient,
    get_auth: Callable[[str, str], TokenAuth],
    vis_factory: Callable[..., VisualizationOrm],
    db_session: Session,
) -> None:
    vis = vis_factory()
    with api_client as client:
        response = client.delete(f'/api/vis/{vis.id}/', auth=get_auth('user', 'qwe123'))

    assert response.status_code // 100 == 2

    assert not db_session.query(select(VisualizationOrm).exists()).scalar()


def test_vis_share(
    api_client: TestClient,
    get_auth: Callable[[str, str], TokenAuth],
    vis_factory: Callable[..., VisualizationOrm],
    db_session: Session,
) -> None:
    vis = vis_factory()
    with api_client as client:
        response = client.put(f'/api/vis/{vis.id}/share/', auth=get_auth('user', 'qwe123'))

    assert response.status_code // 100 == 2

    assert db_session.query(VisualizationOrm.is_public).scalar()


def test_vis_share_other(
    api_client: TestClient,
    get_auth: Callable[[str, str], TokenAuth],
    vis_factory: Callable[..., VisualizationOrm],
    user_factory: Callable[..., UserOrm],
    db_session: Session,
) -> None:
    vis = vis_factory()
    user = user_factory('other', 'qwe123')
    with api_client as client:
        response = client.put(f'/api/vis/{vis.id}/share/', auth=get_auth(user.name, 'qwe123'))

    assert response.status_code // 100 == 4

    assert not db_session.query(VisualizationOrm.is_public).scalar()


def test_vis_unshare(
    api_client: TestClient,
    get_auth: Callable[[str, str], TokenAuth],
    vis_factory: Callable[..., VisualizationOrm],
    db_session: Session,
) -> None:
    vis = vis_factory()
    with api_client as client:
        response = client.delete(f'/api/vis/{vis.id}/share/', auth=get_auth('user', 'qwe123'))

    assert response.status_code // 100 == 2

    assert db_session.query(select(VisualizationOrm).exists()).scalar()
    assert not db_session.query(VisualizationOrm.is_public).scalar()


@pytest.mark.parametrize(
    'auth_factory',
    [
        lambda get_auth: get_auth('user', 'qwe123'),
        lambda get_auth: get_auth('other', 'qwe123'),
        lambda get_auth: None,
        lambda get_auth: TokenAuth('qwe'),
    ],
)
def test_shared_access(
    api_client: TestClient,
    vis_factory: Callable[..., VisualizationOrm],
    get_auth: Callable[[str, str], TokenAuth],
    auth_factory: Callable[..., TokenAuth],
    user_factory: Callable[..., UserOrm],
) -> None:
    user_factory('other', 'qwe123')  # other user
    vis = vis_factory(is_public=True)

    with api_client as client:
        response = client.get(f'/api/vis/{vis.id}/', auth=auth_factory(get_auth))

    assert response.status_code == 200
    assert response.json()['id'] == str(vis.id)
    assert 'data' in response.json()
