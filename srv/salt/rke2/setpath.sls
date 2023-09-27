{% set minionid = grains['id'] %}
check_if_rke2_binary_exist_{{ minionid }}:
  file.exists:
    - name: /var/lib/rancher/rke2/bin

append_path_variable_{{ minionid }}:
  file.managed:
    - name: /root/.bashrc
    - source: salt://rke2/templates/bashrc.template
    - template: jinja
    - require:
      - file: check_if_rke2_binary_exist_{{ minionid }}

check_if_rke2_unix_socket_exist_{{ minionid }}:
  file.exists:
    - name: /var/run/k3s/containerd/containerd.sock

add_crictl_yaml_file_{{ minionid }}:
  file.managed:
    - name: /etc/crictl.yaml
    - source: salt://rke2/templates/etc_crictl.template
    - require:
      - file: check_if_rke2_unix_socket_exist_{{ minionid }}

check_if_rke2_kubeconf_exist_{{ minionid }}:
  file.exists:
    - name: /etc/rancher/rke2/rke2.yaml

set_kubeconf_var_root_user_{{ minionid }}:
  file.append:
    - name: /root/.bashrc
    - text: |
        export KUBECONFIG=/etc/rancher/rke2/rke2.yaml
    - require:
      - file: check_if_rke2_kubeconf_exist_{{ minionid }}
      - file: append_path_variable_{{ minionid }}

