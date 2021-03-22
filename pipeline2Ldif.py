import json
import requests
import os
from requests.auth import HTTPBasicAuth

# ENV VARS
ADO_AUTH = os.getenv('ADO_AUTH')
ADO_ORGANIZATION = os.getenv('ADO_ORGANIZATION')
ADO_PROJECT = os.getenv('ADO_PROJECT')
WORKSPACE_ID = os.getenv('WORKSPACE_ID')


def pipeline2ldif():
    workspace = WORKSPACE_ID

    # The name of the Azure DevOps Organization
    ado_organization = ADO_ORGANIZATION
    # The name of the Azure DevOps Project (can be the name or the ID)
    add_project = ADO_PROJECT

    auth = HTTPBasicAuth(
        '', ADO_AUTH)

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
            if runs_item['state'] == 'completed':
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

        # Add Config fact sheet with history of runs
        pipeline_configs.append({
            "type": "Configuration",
            "id": response_json['name'],
            "data": {
                'url': response_json['_links']['web']['href'],
                'name': response_json['configuration']['repository']['fullName'],
                'runs': runs_list
            }
        })
        # To add further fact sheets in the future
        # pipeline_configs.append({
        #     "type": "Fact Sheet Type - mandatory field",
        #     "id": <<Delineate your required ID here - mandatory field>>,
        #     "data": {
        #         'exampleList': [
        #           {<<Add list item 1 here>>},
        #           {<<Add list item 2 here>>},
        #         ],
        #         'name': <<This shows that you can have any item in data section>>
        #     }
        # })

    # Add up findings from each API to create LDIF

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
