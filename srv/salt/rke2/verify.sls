{% set masters = salt['pillar.get']('rke2:role:server', []) %}
{% set agents = salt['pillar.get']('rke2:role:agents', []) %}
{% set this_minion = salt['grains.get']('id', '') %}

{% if salt['file.file_exists']('/etc/rancher/rke2/rke2.yaml') %}
{% set kubeconfig = '/etc/rancher/rke2/rke2.yaml' %}
{% endif %}

{% if this_minion in masters %}
kubectl_get_nodes_{{ this_minion }}:
  cmd.run:
    - name: /var/lib/rancher/rke2/bin/kubectl  --kubeconfig=/etc/rancher/rke2/rke2.yaml get nodes
{% endif %}

