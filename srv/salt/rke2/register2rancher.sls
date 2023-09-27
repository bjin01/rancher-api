{% set masters = salt['pillar.get']('rke2:role:server', []) %}
{% set agents = salt['pillar.get']('rke2:role:agents', []) %}
{% set first_node = salt['pillar.get']('rke2:first_node', []) %}
{% set this_minion = salt['grains.get']('id', '') %}
{% set register_cluster_name = salt['pillar.get']('rke2:register_rancher_cluster_name', '') %}

{% if salt['file.file_exists']('/etc/rancher/rke2/rke2.yaml') %}
{% set kubeconfig = '/etc/rancher/rke2/rke2.yaml' %}
{% endif %}

{% if this_minion in masters %}
kubectl_get_nodes_{{ this_minion }}:
  cmd.run:
    - name: /var/lib/rancher/rke2/bin/kubectl  --kubeconfig=/etc/rancher/rke2/rke2.yaml get nodes

{% if this_minion in first_node and register_cluster_name is defined and register_cluster_name|length %}
send_registration_event_reactor_{{ this_minion }}:
  event.send:
    - name: rke2/registration/event/{{ this_minion }}
    - data:
        node_k8s: {{ this_minion }}
        register_cluster_name: {{ register_cluster_name }}
    - require:
      - cmd: kubectl_get_nodes_{{ this_minion }}

deploy_coredns_config_{{ this_minion }}:
  file.managed:
    - name: /var/lib/rancher/rke2/server/manifests/rke2-coredns-config.yaml
    - source: salt://rke2/files/rke2-coredns-config.yaml
    - replace: False
{% endif %}
{% endif %}

