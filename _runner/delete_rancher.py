import requests, sys, yaml, json, urllib3

urllib3.disable_warnings()

def load_yaml_file(yaml_file_path):
    with open(yaml_file_path, 'r') as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)
    return yaml_data


def make_request(method, url, headers, data=None, params=None):
    response = requests.request(method, url, headers=headers, data=data, params=params, verify=False)
    return response

def delete_cluster(cluster_name, headers=None):
    url = "https://{}/v1/provisioning.cattle.io.clusters/fleet-default/{}".format(yaml_data["rancher"]['server'], cluster_name)
    response = make_request("DELETE", url, headers=headers)
    print(response.status_code)
    if response.status_code == 200:
        print("Cluster {} deleted successfully".format(cluster_name))
    else:
        print("Cluster {} deletion failed. {}, {}".format(cluster_name, response.text, response.status_code))
    return

def get_cluster_registration_status(cluster_name, headers=None):
    status = "Unknown"
    url = "https://{}/v1/provisioning.cattle.io.clusters/fleet-default/{}".format(yaml_data["rancher"]['server'], cluster_name)
    response = make_request("GET", url, headers=headers)
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


def login_rancher():
    url = "https://{}/v3-public/localProviders/local?action=login".format(yaml_data["rancher"]['server'])
    login_credentials = {}
    login_credentials['username'] = yaml_data["rancher"]['username']
    login_credentials['password'] = yaml_data["rancher"]['password']

    payload = json.dumps(login_credentials)
    
    headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json;charset=UTF-8'
    }

    response = make_request("POST", url, headers=headers, data=payload)

    response_dict = json.loads(response.text)
    token_value = response_dict.get('token')
    return token_value

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <path_to_yaml_file>")
        sys.exit(1)
    
    yaml_file_path = sys.argv[1]
    
    try:
        yaml_data = load_yaml_file(yaml_file_path)
    except Exception as e:
        print("Error:", e)

    token_value = login_rancher()
    headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json;charset=UTF-8',
    'Authorization': 'Bearer {}'.format(token_value)
    }

    cluster_status = get_cluster_registration_status(yaml_data["import_cluster_name"], headers=headers)
    #print("Cluster status: {}".format(cluster_status))
    if cluster_status == "pending":
        print("Cluster {} is in pending state. Deleting...".format(yaml_data["import_cluster_name"]))
        delete_cluster(yaml_data["import_cluster_name"], headers=headers)
    else:
        print("Cluster {} is not in pending state. Deleting is not allowed.".format(yaml_data["import_cluster_name"]))
        sys.exit(1)





