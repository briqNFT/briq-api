FROM python:3.9-buster

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# somehow necessary
RUN pip uninstall -y lark-parser && pip install lark-parser

COPY briq_api/ briq_api
COPY gunicorn.conf.py gunicorn.conf.py

CMD [ "gunicorn", "briq_api.server:app" ]
