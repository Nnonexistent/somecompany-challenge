import pytest
from db.orm import UserOrm
from httpx import AsyncClient


@pytest.mark.anyio
async def test_root(api_client: AsyncClient) -> None:
    async with api_client as client:
        response = await client.get('/')

    assert response.status_code == 200


@pytest.mark.anyio
async def test_auth(api_client: AsyncClient, test_user: UserOrm) -> None:
    async with api_client as client:
        response = await client.post('/auth/token/', data={'username': test_user.name, 'password': 'qwe123'})

    assert response.status_code == 200
    assert 'access_token' in response.json()
    assert response.json()['token_type'] == 'bearer'


from httpx._auth import Auth
class TokenAuth(Auth):
    def __init__(self, token):
        self.token = token

    def auth_flow(self, request):
        request.headers["Authorization"] = f'Bearer {self.token}'
        yield request


@pytest.mark.anyio
async def test_entries_listing(api_client: AsyncClient, get_auth_token: str, test_user) -> None:

    async with api_client as client:
        response = await client.get('/entries/', auth=TokenAuth(get_auth_token(test_user.name, 'qwe123')))

    assert response.status_code == 200
