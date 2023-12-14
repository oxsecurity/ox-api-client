# Imports
import requests
import json
import jsonpickle
import sys
import os.path

# USE pip install python-dotenv to enable .env file
from dotenv import load_dotenv

# FUNCTIONS ------------------
# Deserialize Function using JSONPICKLE
def show_issues (response):
    #frozen = jsonpickle.encode(response)
    jsonObject = jsonpickle.decode(response)

    for check in jsonObject['data']['getIssues']['issues']:
        id = check['id']
        desc = check['mainTitle']
        owners = check['owners']
        print("Issue ID:", id)
        print("Issue Description:", desc)
        print("Issue Owners:", owners)

def writeJSON (fileN,response):
    fileN = sys.argv[1]+'_response' 
    if os.path.exists(fileN+'.temp') is True:
        os.remove(fileN+'.temp')
    writefile = open(fileN + '.temp', 'w')
    writefile.write(passresult)
    writefile.close()
    # WRITES AS TEMP FILE FIRST, THEN RENAMES WHEN COMPLETE (this enables easier integration from other processes 'waiting' for a file)
    if os.path.exists(fileN+'.json') is True:
        os.remove(fileN+'.json')
    os.rename(fileN+'.temp',fileN+'.json')

# BEGIN EXECUTION FLOW --------------------
load_dotenv()
apiurl = os.environ.get('oxUrl')
key = os.environ.get('oxKey')
# apiurl = 'https://api.cloud.ox.security/api/apollo-gateway'
# key = 'api_key'
if (len(sys.argv) < 2):
    print('You must enter the name of the query to submit. Query filenames should contain .query.json and .variables.json suffixes.')
    exit()

usrAction = sys.argv[1].lower()

if usrAction == 'help':
    print('Use any of the following queries as an argument: python_examp.py queryname')
    print('getissues')
    print('getsingleissue')
    print('getapps')
    print('getappinventory')
    print('getappinfo')
    exit()    

# Reading Query and Variables files for GraphQL API
qFilename = './request/' + usrAction + '.query.json'
vFilename = './request/' + usrAction + '.variables.json'

if os.path.exists(qFilename) is False:
    print('Query filename '+qFilename+' does not exist. This file should contain the GraphQL query. The Variables should be located at '+vFilename+'.')
    exit()

with open(qFilename, 'r') as query_file: 
    query = query_file.read()

with open(vFilename, 'r') as variables_file:
    variables = json.load(variables_file)

# Setting Post Params

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'{key}',
}

body = {
    'query': query,
    'variables': variables,
}

# Post Request

try:
    response = requests.post(apiurl, headers=headers, json=body, timeout=1.5)
    if response.status_code == 200:
        result = response.json()
        passresult = json.dumps(result, indent=2)
        # show_issues(passresult)    
        fileN = usrAction+'_response' 
        writeJSON(fileN,passresult)
        if usrAction == 'getissues':
           show_issues(passresult)
    else:
        print(f'GraphQL request failed with status code: {response.status_code}')

except requests.exceptions.RequestException as error:
    print(f'Error: {error}')
