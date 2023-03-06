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
4. Run the service:
````
python ./app/
````

# Test
To run all the tests:
````
pytest
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
