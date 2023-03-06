FROM continuumio/miniconda3
WORKDIR /

RUN conda create -n wattsdown python=3.10
RUN /bin/bash -c conda activate wattsdown

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY /app/ /app/

EXPOSE 8000

CMD ["python", "./app/"]
