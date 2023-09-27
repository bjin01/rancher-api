# rancher-api
Automate RKE2 deployment and register rke2 as generic cluster into Rancher

The deployment only supports RKE2.
The automated register to rancher works also for other k8s, but not tested much.

### __Prerequisites:__
* Linux OS installed and ready.
* All Linux OS nodes within the specific kubernetes cluster must be able to resolve each others hostname, ideally fqdn.
* The linux OS is using systemd.
* Each node has internet access

salt pillar data needed: [sample_pillar_file](./srv/pillar/rke2/init.sls)
* The token value can be changed to anything (arbitrary).
* The role has two types: server and agents.
* Server role is meant that the node will get kubernetes controlplan components installed.
* Agents role is for all other worker nodes inside a kubernetes cluster.
* First_node is the rke2 deployment term. The deployment starts with one node as first_node and other nodes will simply connect to this first_node and register themself.
* tls_san needs to be adapted according needs.
* For None-High-Availaibility kubernetes Cluster simply leave out agents role.

__Run salt states:__
At the moment those states can be deployed:

* deploy
* uninstall
* verify

### Deploy
```salt "myk8s*" state.apply rke2.deploy```

The deploy state will deploy rke2 on the matching nodes according the pillar definitions.
The state does not wait until the rke2 is fully deployed. Therefore there is a verify state for that purpose.

### Verify
```salt "myk8s*" state.apply rke2.verify```

The verify state will try to run “kubectl get nodes”. If the output shows error e.g.
```
stderr:
        The connection to the server 127.0.0.1:6443 was refused - did you specify the right host or port?
```

The salt states need to be executed on the uyuni server as root user.

### Uninstall:
it is also very easy to uninstall the entire rke2 cluster.

```salt "acc-stag*" state.apply rke2.uninstall```

A salt-run module “rancher” was created that allows to register rke2 k8s into rancher using rancher api.


