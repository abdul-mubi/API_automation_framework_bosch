# Auto-Check Quality Gates


## Preconditions
1. Python v3.x
2. Internet Access to the JIRA URLs (Proxy/Whitelisting)
3. User has to configure his PAT under
## Dependencies

Dependencies are defined in:
- `requirements.txt` 

## First steps

Install the necessary dependencies execute
```
pip install -r requirements.txt --proxy=https://rb-proxy-in.bosch.com:8080
```

## Usage

To start the Script, first navigate to qg-automation root directory via terminal and type following command:
```
python .\automated_qgs.py -d <TEST_EXECUTION_ID> --d <ACTION_NAME>  
```
or 
```
python .\automated_qgs.py --TE <TEST_EXECUTION_ID> --action <ACTION_NAME>  
```

```
Eg:
```
python .\automated_qgs.py --TE QGM-90 --action DO_QG_CHECK  
```
Once the required operation is completed, it will automatically display the results