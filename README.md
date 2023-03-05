# backend

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