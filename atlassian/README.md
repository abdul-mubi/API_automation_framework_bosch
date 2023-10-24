# Jira API
Library for JIRA and Xray related actions.

## Installation
```
    pip install jira_api 
```

Note: DIrect installation is not available yet as the package is still not migrated to artifactory

## Get started

The Jira API currently supports two Type of APIs

Precondition: User has a valid JIRA URL and the user credentials for CRUD operation
### Jira API
With Jira APIs user can create update or view the issues. Also perform some actions based on filters

### XRay API
With XRay related APIs user can update the tests / Test Executions / Test Plans / Test Runs
The APIs also support Cucumber test import and Export part.


## Package creation

Package creation can be done by updating the setup.py file as per the required version after installing the pre requisites as mentioned in requirements.txt

```
python setup.py sdist bdist_wheel
```
once the above step is executed, a new package will be created in whl format and tar.gz format in dist directory. Which can be installed by the user

Eg:
```
pip install dist/jira_api-0.0.1.tar.gz
```

Once the above step is executed library will be available in the local for usage.


## Unit testing

Currently only basic use cases are covered as part of unit testing and will be improved later point in time.