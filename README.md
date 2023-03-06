# backend

# Getting started
1. Create Conda environment:
````
conda create -n wattsdown python=3.10
````
2. Activate the Conda environment:
````
conda activate wattsdown
````
3. Install the requirements with Pip:
````
pip install -r requirements.txt
````
or with Make:
````
make req
````
4. Run the service:
````
python ./app/
````
or with Make:
````
make run
````

# Format
To run all formatting:
````
python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
python -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
````
Alternatively you can use Make:
````
make fmt
````

# Test
To run all the tests:
````
pytest
````
Alternatively you can use Make:
````
make test
````

# Docker
To build the image:
````
docker build . --tag wattsdown:dev
````
To run the newly built image:
````
docker run --publish 8000:8000 wattsdown:dev
````

# Docker Compose
To start docker-compose:
````
docker-compose up
````
This will build with the current directory of the compose file as its context.
Alternatively you can use Make:
````
make
````