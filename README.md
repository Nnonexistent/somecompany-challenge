## How to start project

1. Docker and docker-compose should be installed.

2. Run in terminal:
```bash
./run-compose.sh
```

3. Open browser at http://localhost:8000/docs to see swagger


4. Click **Authorize** and use `user`/`qwe123` to gain access to API.


## How to run tests

1. Install/switch to python 3.8+

2. Install **postgresql** and create user and database

3. Navigate to `src/anserv`

```bash
cd src/anserv/
```

4. Create `.env` file and fill it with:
```
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=anserv
```

5. Install requirements

```bash
pip install -r requirements.txt
pip install -r dev-requirements.txt
```

6. Run pytest

```bash
pytest
```


## How to run tests in docker

1. Docker and docker-compose should be installed.

2. Run in terminal:
```bash
./run-compose-tests.sh
```
