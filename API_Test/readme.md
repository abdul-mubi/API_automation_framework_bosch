# VMS 

Tags: vms, plcs

This is the new restructured PLCS/VMS repository.

## Frameworks and Libraries used
* [Behave](https://behave.readthedocs.io/en/latest/)
* [Requests](http://docs.python-requests.org/en/latest/user/quickstart/)

## System Installations

The following should be installed globally using its default installer (this
must only be done once on a system):

1. Python v3.x
2. Jenkins (will be installed in Test PC)

### Python 3.x

1. Download Python V3.x from the website [Python](https://www.python.org/downloads)	
2. Make sure the environment variable is added to PATH in system configuration
3. Ensure pip is installed (Python versions higher than 3.4 have it included by default).


## Prerequisites

The project requires the following packages to be installed using the ide or command line:

### Syntax

```
python -m pip install <package> --proxy=https://rb-proxy-in.bosch.com:8080
```

1. requests
```
python -m pip install requests --proxy=https://rb-proxy-in.bosch.com:8080
```
2. behave
```
python -m pip install behave --proxy=https://rb-proxy-in.bosch.com:8080
```
3. urllib3 
```
python -m pip install urllib3 --proxy=https://rb-proxy-in.bosch.com:8080
```
	NOTE: Since we are in Bosch (proxy), it is necessary to give proxy details for python pip package. 


## Folder structure in BDD (Behavior Driven Development) environment

The folder structure is very important in BDD environment.

1. Ensure prerequisites are installed
2. In the repo, create a 'features' (can be renamed, "API_Test" in our repo) directory that will contain the .feature file. There can be any number of feature directories depending upon the number of features for which the test cases are developed.
3. The step definition files (.py scripts) are placed under the directory 'API_Test/steps/'.

## Offline testing

The BDD lines contained in the feature file can be run offline. To run offline, a batch (.bat) file must be setup containing   
* **BUILD_NUMBER**
* **usernameUI**
* **passwordUI**

These are the environment variables which are setup in the server when the script is run on Jenkins. This batch file is added to the features (\API_Test\offline_tests) directory. Offline testing can be carried out in either of the two ways:
	
	NOTE: Make sure the tag "@offline" is added to the .feature file. 
* The .feature file can be dragged and dropped into the batch file.
* Else, navigate to the path containing the batch file in cmd window and provide the command
```
run_behave.bat <.feature filename>
```
	NOTE: Adding --no capture --no-capture-stderr to the 'behave' line in batch file provides debug logs.  

The logs are stored as output_log_DDMMYYmmss.txt file in API_Test\offline_tests\logs.
	
## Upload files

The dbc files and RDA container which require to be uploaded for Remote measurement and Remote diagnostics respectively are uploaded in the location \API_Test\steps\upload_files.

----------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------

# PLCS API tests

The content shall be used for PLCs API based tests.

## Getting Started

Clone the repository.

### Prerequisites

You have Python properly installed.

### Installing

Create virtual environment. Therefore navigate into the *API_Test* folder and execute
```
python -m venv .venv
```

To activate the virtual environment execute
```
.venv\Scripts\activate.bat
```

To install the necessary dependencies execute
```
pip install -r requirements.txt --proxy=https://rb-proxy-in.bosch.com:8080
```

To deactivate the virtual environment execute
```
.venv\Scripts\deactivate.bat
```

Depending on your system setup, you may need to 
```
set PYTHONPATH=.
```

to make the custom PrettyCucumberJSONFormater usable.

Update the Python37-32\Lib\site-packages\behave folder with below information

in File formatter\_builtins.py, Add line
		("json.cucumber", "behave.formatter.cucumber:CucumberJSONFormatter"),

Copy cucumber_json.py to folder \formatter

Update the PYTHONPATH and give path of folder \behave and \behave\formatter

### Troubleshooting with installations

1. Remove all residues of previous installation and the respective environment variables to fix the problem of empty scripts folder after installation

2. Downgrade urllib3 version to 1.25.8 to fix the issue of "requests.exceptions.SSLError: HTTPSConnectionPool"

3. In PC1 by default packages are requested from rb-artifactory server and some packages are not available there, so use -i 
https://pypi.org/simple default python server to install the packages

4. Restart the test PC after making all the changes and before running from jenkins

## Running the tests

Explain how to run the automated tests for this system

```
behave -i .feature --format=cucumber_json:PrettyCucumberJSONFormatter -o cucumber_formated_result.json
```

## Note

## Built With

* [Python](https://www.python.org/)
* [Behave](https://behave.readthedocs.io/en/latest/)