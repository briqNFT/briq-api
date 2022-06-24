FROM python:3.9-buster as initial

WORKDIR /usr/src/app

# Install some libs that are less likely to change
# TODO: keep synched with requirements.txt
RUN pip install --no-cache-dir gunicorn>=20.1 google-cloud-storage>=2.3 flake8>=4.0 Pillow>=9.0 pygltflib>=1.15 ecdsa fastecdsa sympy

FROM initial

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
# somehow necessary
RUN pip uninstall -y lark-parser && pip install lark-parser

COPY briq_api/ briq_api
COPY jobs/ jobs
COPY gunicorn.conf.py gunicorn.conf.py

# Install briq_api as a module for jobs.
COPY setup.py ./
RUN pip install -e .

# For temporary testing, copy the temp folder for sets.
COPY temp/genesis_themes/ temp/genesis_themes

CMD [ "gunicorn", "briq_api.server:app" ]
