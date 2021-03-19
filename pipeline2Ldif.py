import json
import requests
from requests.auth import HTTPBasicAuth

workspace = "1a84105f-5e80-468d-bc82-311338999016"

adoOrganization = 'leanixcnstest'    # The name of the Azure DevOps Organization
# The name of the Azure DevOps Project (can be the name or the ID)
addProject = 'Test'

auth = HTTPBasicAuth(
    '', 'fkvbddslrmrqflmpui76l5huybhk5yu7nwoqgxh7tz23bobq7b3q')


requestURL = 'https://dev.azure.com/' + adoOrganization + '/' + addProject + \
    '/_apis/pipelines?api-version=6.0-preview.1'  # Reques to get a full list of available pipelines related to this Project

res = requests.get(requestURL, auth=auth)
pipelineList = res.json()

####
# Artifact test
####
# addPipelineId = "2"
# artifactURL = 'https://dev.azure.com/' + adoOrganization + '/' + addProject + \
#     '/_apis/pipelines/' + addPipelineId + \
#     '/runs/1/artifacts?artifactName=""&api-version=6.0-preview.1'
# # https: // dev.azure.com/{organization}/{project}/_apis/pipelines/{pipelineId}/runs/{runId}/artifacts?artifactName = {artifactName} & api-version = 6.0-preview.1
# artifactResponse = requests.get(artifactURL, auth=auth)
# artifactJSON = artifactResponse.json()
# print(artifactJSON)

####
# Build test
####
addBuildId = "2"
addArtifactName = "azure-pipelines"
buildURL = 'https://dev.azure.com/' + adoOrganization + '/' + addProject + \
    '/_apis/build/builds/' + addBuildId + '/artifacts?artifactName=' + \
    addArtifactName + '&api-version=6'
# https://dev.azure.com/{organization}/{project}/_apis/build/builds/{buildId}/artifacts?artifactName={artifactName}&api-version=6.
buildResponse = requests.get(buildURL, auth=auth)
buildJSON = buildResponse
print(buildJSON)


pipelineConfigs = []
for pipelineItem in pipelineList['value']:
    # print(json.dumps(pipelineList, indent=2))
    response = requests.get(pipelineItem['_links']['self']['href'], auth=auth)

    # List of runs
    runsList = []

    # Get last 1000 runs from each pipeline
    addPipeLineId = str(pipelineItem['id'])

    # Get individual run from pipeline
    runsURL = 'https://dev.azure.com/' + adoOrganization + '/' + addProject + \
        '/_apis/pipelines/' + addPipeLineId + '/runs?api-version=6.0-preview.1'
    runsResponse = requests.get(runsURL, auth=auth)
    runsJSON = runsResponse.json()

    # Add individual run to metrics
    for runsItem in runsJSON['value']:
        runsList.append({
            "type": "Run",
            "id": "run_" + runsItem['name'],
            "data": {
                'state': runsItem['state'],
                'result': runsItem['result'],
                'date': runsItem['finishedDate'],
                "deployment": runsItem['pipeline']['name']
            }
        })

    responseJSON = json.loads(response.content)
    # print(json.dumps(responseJSON, indent=2))
    # print(responseJSON['configuration']['path'])
    # pipelineLDIFObjects = {"content": responseJSON['configuration']['path']}
    pipelineConfigs.append({
        "type": "Configuration",
        "id": responseJSON['name'],
        "data": {
            'url': responseJSON['_links']['web']['href'],
            'name': responseJSON['configuration']['repository']['fullName'],
            'runs': runsList
        }
    })

# print(json.dumps(pipelineConfigs, indent=2))
# ldif['content'] =
ldif = {
    "connectorType": "azure-devops-pipelines-connector",
    "connectorId": "azure-devops-pipelines-connector",
    "connectorVersion": "1.0",
    "processingMode": "full",
    "lxVersion": "1.0.0",
    "lxWorkspace": workspace,
    "description": "Azure DevOps Connector",
    "content": pipelineConfigs}
print(json.dumps(ldif, indent=2))
