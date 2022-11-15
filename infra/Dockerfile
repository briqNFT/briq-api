FROM python:3.9-buster as initial

WORKDIR /usr/src/app

FROM initial

COPY poetry.lock ./
COPY pyproject.toml ./

# This is super unrecommended because poetry can uninstall its own dependencies later,
# but I don't think I care particularly.
RUN pip install --no-cache-dir poetry
RUN poetry export --output requirements.txt --without-hashes && pip install -r requirements.txt

COPY briq_api/ briq_api
COPY jobs/ jobs
COPY gunicorn.conf.py gunicorn.conf.py

RUN pip install --no-deps -e .

# For temporary testing, copy the temp folder for sets.
COPY temp/genesis_themes/ temp/genesis_themes

CMD [ "gunicorn", "briq_api.server:app" ]
