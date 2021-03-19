import json
import requests
from requests.auth import HTTPBasicAuth


def pipeline2ldif():
    workspace = "1a84105f-5e80-468d-bc82-311338999016"

    ado_organization = 'leanixcnstest'    # The name of the Azure DevOps Organization
    # The name of the Azure DevOps Project (can be the name or the ID)
    add_project = 'Test'

    auth = HTTPBasicAuth(
        '', 'fkvbddslrmrqflmpui76l5huybhk5yu7nwoqgxh7tz23bobq7b3q')

    request_url = 'https://dev.azure.com/' + ado_organization + '/' + add_project + \
        '/_apis/pipelines?api-version=6.0-preview.1'  # Reques to get a full list of available pipelines
    # related to this Project

    res = requests.get(request_url, auth=auth)
    pipeline_list = res.json()

    ####
    # Artifact test
    ####
    # add_pipe_line_id = "2"
    # artifactURL = 'https://dev.azure.com/' + ado_organization + '/' + add_project + \
    #     '/_apis/pipelines/' + add_pipe_line_id + \
    #     '/runs/1/artifacts?artifactName=""&api-version=6.0-preview.1'
    # # https: // dev.azure.com/{organization}/{project}/
    # _apis/pipelines/{pipelineId}/runs/{runId}/artifacts?artifactName={artifactName}
    #  &api-version=6.0-preview.1
    # artifactResponse = requests.get(artifactURL, auth=auth)
    # artifactJSON = artifactResponse.json()
    # print(artifactJSON)

    ####
    # Build test
    ####
    # addBuildId = "2"
    # addArtifactName = "azure-pipelines"
    # buildURL = 'https://dev.azure.com/' + ado_organization + '/' + add_project + \
    #     '/_apis/build/builds/' + addBuildId + '/artifacts?artifactName=' + \
    #     addArtifactName + '&api-version=6'
    # # https://dev.azure.com/{organization}/{project}/_apis/build/builds/
    # {buildId}/artifacts?artifactName={artifactName}&api-version=6.
    # buildResponse = requests.get(buildURL, auth=auth)
    # buildJSON = buildResponse
    # print(buildJSON)

    pipeline_configs = []
    for pipeline_item in pipeline_list['value']:
        # print(json.dumps(pipeline_list, indent=2))
        response = requests.get(
            pipeline_item['_links']['self']['href'], auth=auth)

        # List of runs
        runs_list = []

        # Get last 1000 runs from each pipeline
        add_pipe_line_id = str(pipeline_item['id'])

        # Get individual run from pipeline
        runs_url = 'https://dev.azure.com/' + ado_organization + '/' + add_project + \
            '/_apis/pipelines/' + add_pipe_line_id + '/runs?api-version=6.0-preview.1'
        runs_response = requests.get(runs_url, auth=auth)
        runs_json = runs_response.json()

        # Add individual run to metrics
        for runs_item in runs_json['value']:
            runs_list.append({
                "type": "Run",
                "id": "run_" + runs_item['name'],
                "data": {
                    'state': runs_item['state'],
                    'result': runs_item['result'],
                    'date': runs_item['finishedDate'],
                    "deployment": runs_item['pipeline']['name']
                }
            })

        response_json = json.loads(response.content)
        # print(json.dumps(response_json, indent=2))
        # print(response_json['configuration']['path'])
        # pipelineLDIFObjects = {"content": response_json['configuration']['path']}
        pipeline_configs.append({
            "type": "Configuration",
            "id": response_json['name'],
            "data": {
                'url': response_json['_links']['web']['href'],
                'name': response_json['configuration']['repository']['fullName'],
                'runs': runs_list
            }
        })

    # print(json.dumps(pipeline_configs, indent=2))
    # ldif['content'] =
    ldif = {
        "connectorType": "azure-devops-pipelines-connector",
        "connectorId": "azure-devops-pipelines-connector",
        "connectorVersion": "1.0",
        "processingMode": "full",
        "lxVersion": "1.0.0",
        "lxWorkspace": workspace,
        "description": "Azure DevOps Connector",
        "content": pipeline_configs}
    print(json.dumps(ldif, indent=2))


# Initiate script    
pipeline2ldif()    
