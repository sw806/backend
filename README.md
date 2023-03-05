# backend

# Getting started
To run the service you must first activate the environment with _conda_:
````
conda activate
````
Then you can run the main python application:
````
python ./app/
````
You can check that everything is running by opening your browser and vist: http://0.0.0.0:8000/api/v1/status.
This page should display an healthy status of this service.

# Anaconda

To create an _actual_ conda environment:  
````
conda create --prefix ./environment
````

To add a dependecy/package to that environment do:  
```
conda install --prefix ./environment PACKAGE_NAME
```  
As an example:  
````
conda install --prefix ./environment.yml --channel conda-forge fastapi
````  

To create a local copy of the anaconda environment, run the following command:  
````
conda env create -f environment.yml
````