# Ormuco Test

## Objectives
This repository is intendend to provide access to Ormuco in order to evaluate
tests given

## Organization
The repo is organized in the following way:
1. A util directory with a simple python package where Question A and B of the test are implemented inside a util.py file and can be tested using test_util.py file
 ```bash
 ~/virgilio_santos_test $ cd util/
 ~/virgilio_santos_test/util $ nosetests test_util.py
 ```
 For implementation details, please read the functions doc strings.

2. A geod_lrucache directory which contains a full structured python lib to be installed with a package manager like pip. It's based on cookiecutter `audreyr/cookiecutter-pypackage` template and ready to grow as a robust piece of code. Checkout [geod_lrucache/README.rst](https://github.com/virgilio/virgilio_santos_test/blob/master/geod_lrucache/README.rst) for more information about the library itself and implementation design details.
**For the test specific purposes** please look into: `virgilio_santos_test/geod_lrucache/geod_lrucache/geod_lrucache.py` file

3. A geod_demo directory with 2 demos that should show how to integrate the library to your code easily. for `geod_demo/demo_distributed_cache.py`, you need to:
 ```bash
 ~/virgilio_santos_test $ # initialize a python3 environment of your preference
 ~/virgilio_santos_test $ cd geod_demo && virtualenv env
 ~/virgilio_santos_test $ . env/bin/activate
 ~/virgilio_santos_test $ pip install -r requirements.txt
 ~/virgilio_santos_test $ pip install ../geod_lrucache/
 ~/virgilio_santos_test $ python demo_distributed_cache.py
 ```
