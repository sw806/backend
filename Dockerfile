FROM continuumio/miniconda3
WORKDIR /

RUN conda create -n wattsdown python=3.10
RUN /bin/bash -c conda activate wattsdown

COPY requirements.txt .
RUN pip install -r requirements.txt

ARG COMMIT_HASH
ENV COMMIT_HASH=$COMMIT_HASH
RUN echo "$COMMIT_HASH"

COPY /app/ /app/

EXPOSE 8000

CMD ["python", "./app/"]
