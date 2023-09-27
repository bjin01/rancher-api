
from __future__ import absolute_import, print_function, unicode_literals
import requests, sys, yaml, json, urllib3, time
import logging
import six
import salt.client

urllib3.disable_warnings()

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    __salt__: Any = None
    __opts__: Any = None
    __pillar__: Any = None

log = logging.getLogger(__name__)

def __virtual__():
    return True

def _load_yaml_file(yaml_file_path):
    with open(yaml_file_path, 'r') as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)
    return yaml_data

def _get_rancher_configuration():
    '''
    Return the configuration read from the salt master configuration
    file or directory
    '''
    rancher_info = __opts__['rancher'] if 'rancher' in __opts__ else None

    if rancher_info:
        try:
            username = rancher_info.get('username')
            password = rancher_info.get('password')
            server = rancher_info.get('server')
            port = rancher_info.get('port', "443")
            if not username or not password or not server:
                log.error(
                    'Username or Password or Server or import_cluster_name has not been specified in the rancher configuration section'
                    'configuration for %s', rancher_info
                )
                return False

            ret = {
                'port': port,
                'username': username,
                'password': password,
                'server': server
            }
            return ret
        except Exception as exc:  # pylint: disable=broad-except
            log.error('Exception encountered: %s', exc)
            return False

    return False


def _make_request(method, url, headers, data=None, params=None):
    response = requests.request(method, url, headers=headers, data=data, params=params, verify=False)
    return response

def _get_cluster_id(name, cluster_link, headers=None):
    url = cluster_link
    response = _make_request("GET", url, headers=headers)
    response_dict = json.loads(response.text)
    #print(response_dict)
    cluster_id = ""
    try:
        cluster_id = response_dict.get('status').get('clusterName')
        return cluster_id
    except:
        for r in response_dict["metadata"]['relationships']:
            if isinstance(r, dict):
                if r['toType'] == "management.cattle.io.cluster":
                    cluster_id = r["toId"]
                    return cluster_id
    return cluster_id

def _create_cluster_token(cluster_id, rancher_config, headers=None):
       #POST - Create Registration Token
    
    output = _lookup_cluster_registrationtoken(rancher_config, cluster_id, headers=headers)
    return output

    # below code is not needed because import cluster will automatically create a registration token
    """ if output != "Not Found":
        #print("Cluster registration token already exists!")
        #print("do we get here?")
        return output

    url = "https://{}/v3/clusterregistrationtokens".format(rancher_config['server'])
    create_registration_token_payload = {}
    create_registration_token_payload["type"] = "clusterRegistrationToken"
    create_registration_token_payload["clusterId"] = cluster_id
    payload = json.dumps(create_registration_token_payload)
    response = _make_request("POST", url, headers=headers, data=payload)
    #print(response.status_code)
    print(response.text)
    response_dict = json.loads(response.text)
    cluster_link = response_dict.get('links').get('self')
    print("Token link:", cluster_link) 
    return cluster_link """

def _get_cluster_registration_status(rancher_config, cluster_name, headers=None):
    status = "Unknown"
    url = "https://{}/v1/provisioning.cattle.io.clusters/fleet-default/{}".format(rancher_config['server'], cluster_name)
    response = _make_request("GET", url, headers=headers)
    #print(response.status_code)
    #print(response.text)
    if response.status_code == 404:
        print("Cluster {} not found".format(cluster_name))
        status = "Not Found"
        return status
    
    if response.status_code == 200:
        print("Cluster {} found".format(cluster_name))
        #print(json.dumps(json.loads(response.text), indent=4, sort_keys=True))
        response_dict = json.loads(response.text)
        status = response_dict.get('metadata').get('state').get('name')

    return status

def _import_cluster(cluster_id, rancher_config, headers=None):
    url = "https://{}/v1/provisioning.cattle.io.cluster/create?mode=import&type=import".format(rancher_config['server'])
    """ headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json;charset=UTF-8',
    'Authorization': 'Bearer {}'.format(token_value)
    } """
    
    import_cluster_payload = {}
    import_cluster_payload["type"] = "provisioning.cattle.io.cluster"
    import_cluster_payload["metadata"] = {}
    import_cluster_payload["metadata"]["name"] = rancher_config["import_cluster_name"]
    import_cluster_payload["metadata"]["namespace"] = "fleet-default"
    import_cluster_payload["spec"] = {}
    
    payload = json.dumps(import_cluster_payload)
    response = _make_request("POST", url, headers=headers, data=payload)
    """ print(response.status_code)
    print(response.text) """
    if response.status_code == 409:
        response_dict = json.loads(response.text)
        alreadyexist = response_dict.get('code')
        if alreadyexist == "AlreadyExists":
            print("Cluster already exists!")
            url = "https://{}/apis/provisioning.cattle.io/v1/namespaces/fleet-default/clusters/{}".format(rancher_config['server'], rancher_config["import_cluster_name"])
            cluster_id = _get_cluster_id(rancher_config["import_cluster_name"], url, headers=headers)

            print("cluster-id:",cluster_id)
            #POST - Create Registration Token
            cluster_link = _create_cluster_token(cluster_id, rancher_config, headers=headers)
            _get_registeration_commands(cluster_link, headers=headers)
            #sys.exit(1)
        
    response_dict = json.loads(response.text)
    cluster_link = response_dict.get('links').get('self')
    print(cluster_link)
    print("We wait here 3 seconds to let rancher finish the process.")
    time.sleep(3)
    cluster_id = _get_cluster_id(rancher_config["import_cluster_name"], cluster_link, headers=headers)
    print("cluster-id:", cluster_id)
    return cluster_id

def _get_registeration_commands(token_link, headers=None):
    url = token_link
    response = _make_request("GET", url, headers=headers)
    #print(response.status_code)
    #print(response.text)
    response_dict = json.loads(response.text)
    #print(response_dict)
    registration_command_insecure = response_dict.get('insecureCommand')
    print(registration_command_insecure)

    return registration_command_insecure

def _lookup_cluster_registrationtoken(rancher_config, cluster_id, headers=None):
    url = "https://{}/v3/clusterregistrationtokens".format(rancher_config['server'])
    response = _make_request("GET", url, headers=headers)
    response_dict = json.loads(response.text)
    #print(response_dict)

    if response.status_code != 200:
        print("Error checking cluster registration tokens!")
        sys.exit(1)
    
    for i in response_dict.get('data'):
        if i.get('clusterId') == cluster_id:
            print("Cluster registration token found!")
            return i.get('links').get('self')
    print("Cluster registration token not found!")
    return "Not Found"

def _write_bash_script(data, file_path):
    bash_content = "#!/bin/bash"
    bash_content += "\n"
    bash_content += data
    bash_content += "\n"

    byte_data = bytes(bash_content, 'utf-8')
    with salt.utils.files.fopen(file_path, "wb") as batch_file:
        batch_file.write(byte_data)

    return 

def register(cluster_name=None, k8s_node="localhost"):
    """
    Import custom rke2 kuberntes cluster into rancher.

    cluster_name
        Provide the name of cluster that should be registered into rancher.

    k8s_node
        provide the minion-id of the downstream cluster where kubectl will be executed.
        /var/lib/rancher/rke2/bin is the default binary directory for kubectl and must exist.
        /etc/rancher/rke2/rke2.yaml is the default kubeconfig file and must exist.

    bash_script_path
        provide the full path including the file name for the bash script that should be executed within a cmd.script sls.


    CLI Example:

    .. code-block:: bash

        salt-run rancher.register cluster_name=new-k8s k8s_node=node1.example.com
    """
    print("----------------Received: {}".format(cluster_name))
    print("----------------Received: {}".format(k8s_node))
    rancher_config = _get_rancher_configuration()
    ret = dict()
    #ret = rancher_config
    
    if cluster_name != None:
        rancher_config['import_cluster_name'] = cluster_name
    else:
        print("cluster_name is not provided. Exit.")
        return ret

    print(rancher_config)
    print("----------------rancher_config: {}".format(rancher_config))
    url = "https://{}/v3-public/localProviders/local?action=login".format(rancher_config['server'])
    login_credentials = {}
    login_credentials['username'] = rancher_config['username']
    login_credentials['password'] = rancher_config['password']

    payload = json.dumps(login_credentials)
    
    headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json;charset=UTF-8'
    }

    response = _make_request("POST", url, headers=headers, data=payload)

    response_dict = json.loads(response.text)
    token_value = response_dict.get('token')
    #print(token_value)
    headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json;charset=UTF-8',
    'Authorization': 'Bearer {}'.format(token_value)
    }

    cluster_status = _get_cluster_registration_status(rancher_config, rancher_config["import_cluster_name"], headers=headers)

    print("Cluster status: {}".format(cluster_status))

    # POST - import existing cluster
    cluster_id = ""
    cluster_link = ""
    local = salt.client.LocalClient()

    if cluster_status == "Not Found":
        print("Cluster {} will be imported...".format(rancher_config["import_cluster_name"]))
        cluster_id = _import_cluster(cluster_id, rancher_config, headers=headers)
        cluster_link = _create_cluster_token(cluster_id, rancher_config, headers=headers)
        #GET - Registration command
        ret['insecure-command'] = _get_registeration_commands(cluster_link, headers=headers)
        curl_cmd = ret['insecure-command'].split('|')[0].strip()
        key = "rancher_registration_curl_cmd"
        set_grains_return = local.cmd("{}".format(k8s_node), 'grains.setval', [key, curl_cmd], force=True)
        print("Set grains: {}".format(set_grains_return))
        
        return ret['insecure-command']
        
    #POST - Create Registration Token
    cluster_status = _get_cluster_registration_status(rancher_config, rancher_config["import_cluster_name"], headers=headers)
    if cluster_status == "pending":
        
        print("Cluster already exists!")
        url = "https://{}/apis/provisioning.cattle.io/v1/namespaces/fleet-default/clusters/{}".format(rancher_config['server'], rancher_config["import_cluster_name"])
        cluster_id = _get_cluster_id(rancher_config["import_cluster_name"], url, headers=headers)
        cluster_link = _create_cluster_token(cluster_id, rancher_config, headers=headers)
        #GET - Registration command
        ret['insecure-command'] = _get_registeration_commands(cluster_link, headers=headers)
        curl_cmd = ret['insecure-command'].split('|')[0].strip()
        key = "rancher_registration_curl_cmd"
        set_grains_return = local.cmd("{}".format(k8s_node), 'grains.setval', [key, curl_cmd], force=True)
        print("Set grains: {}".format(set_grains_return))

        return ret['insecure-command']

    return 

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <path_to_yaml_file>")
        sys.exit(1)
    
    yaml_file_path = sys.argv[1]
    
    try:
        yaml_data = _load_yaml_file(yaml_file_path)
    except Exception as e:
        print("Error:", e)

    url = "https://{}/v3-public/localProviders/local?action=login".format(yaml_data["rancher"]['server'])
    login_credentials = {}
    login_credentials['username'] = yaml_data["rancher"]['username']
    login_credentials['password'] = yaml_data["rancher"]['password']

    payload = json.dumps(login_credentials)
    
    headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json;charset=UTF-8'
    }

    response = _make_request("POST", url, headers=headers, data=payload)

    response_dict = json.loads(response.text)
    token_value = response_dict.get('token')
    #print(token_value)
    headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json;charset=UTF-8',
    'Authorization': 'Bearer {}'.format(token_value)
    }

    cluster_status = _get_cluster_registration_status(yaml_data['rancher'], yaml_data["import_cluster_name"], headers=headers)

    print("Cluster status: {}".format(cluster_status))

    # POST - import existing cluster
    cluster_id = ""
    cluster_link = ""
    if cluster_status == "Not Found":
        print("Cluster {} will be imported...".format(yaml_data["import_cluster_name"]))
        cluster_id = _import_cluster(cluster_id, yaml_data, headers=headers)
        cluster_link = _create_cluster_token(cluster_id, yaml_data, headers=headers)
        #GET - Registration command
        _get_registeration_commands(cluster_link, headers=headers)
        sys.exit(0)
        
    #POST - Create Registration Token
    cluster_status = _get_cluster_registration_status(yaml_data['rancher'], yaml_data["import_cluster_name"], headers=headers)
    if cluster_status == "pending":
        
        print("Cluster already exists!")
        url = "https://{}/apis/provisioning.cattle.io/v1/namespaces/fleet-default/clusters/{}".format(yaml_data["rancher"]['server'], yaml_data["import_cluster_name"])
        cluster_id = _get_cluster_id(yaml_data["import_cluster_name"], url, headers=headers)
        cluster_link = _create_cluster_token(cluster_id, yaml_data['rancher'], headers=headers)
        #GET - Registration command
        _get_registeration_commands(cluster_link, headers=headers)
        sys.exit(0)
        
    
    
 
