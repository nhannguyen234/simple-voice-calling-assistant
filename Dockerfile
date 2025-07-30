FROM python:3.11.11-bulleye

WORKDIR /code

RUN apt-get update \ 
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2 \
    && apt-get install -y libgl1-mesa-glx libglib2.0-0 \
    && apt-get clean

COPY ./requirements.txt /code/requirements.txt

RUN pip install --upgrade pip \
    && pip install -r ./requirements.txt

COPY . /code/
ENV PYTHONPATH "${PYTHONPATH}:/code/"

CMD ["python", "main.py"]