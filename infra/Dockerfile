FROM python:3.9-buster

WORKDIR /usr/src/app

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

CMD [ "gunicorn", "briq_api.server:app" ]
