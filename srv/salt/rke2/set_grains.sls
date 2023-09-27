{% set minionid = grains['id'] %}
check_if_rke2_server_{{ minionid }}:
  file.exists:
    - name: /var/lib/rancher/rke2/server/node-token

check_if_rke2_kubeconf_exist_{{ minionid }}:
  file.exists:
    - name: /etc/rancher/rke2/rke2.yaml

set_grains_rke2_role_{{ minionid }}:
  grains.present:
    - name: rke2-role
    - value: server
    - require:
      - file: check_if_rke2_server_{{ minionid }}
      - file: check_if_rke2_kubeconf_exist_{{ minionid }}

set_grains_rke2_agent_role_{{ minionid }}:
  grains.present:
    - name: rke2-role
    - value: agent
    - onfail:
      - file: check_if_rke2_server_{{ minionid }}
      - file: check_if_rke2_kubeconf_exist_{{ minionid }}

