{% set masters = salt['pillar.get']('rke2:role:server', []) %}
{% set agents = salt['pillar.get']('rke2:role:agents', []) %}
{% set this_minion = salt['grains.get']('id', '') %}
{% set token = salt['pillar.get']('rke2:token') %}

{% if this_minion in masters %}
{% set role = "server" %}
{% else %}
{% set role = "agent" %}
{% endif %}

{% if this_minion in masters or this_minion in agents %}
create_config_dir_rke2_{{ grains['fqdn'] }}:
  file.directory:
    - name: /etc/rancher/rke2
    - user: root
    - group: root
    - dir_mode: "0755"
    - file_mode: "0600"
    - makedirs: True
    - recurse:
      - user
      - group
      - mode

check_if_rke2_already_exist_{{ grains['fqdn'] }}:
  file.missing:
    - name: /etc/rancher/rke2/rke2.yaml

create_rke2_config_yaml_{{ grains['fqdn'] }}:
  file.managed:
    - name: /etc/rancher/rke2/config.yaml
    - source: salt://rke2/files/config.yaml
    - replace: True
    - template: jinja
    - require:
      - file: create_config_dir_rke2_{{ grains['fqdn'] }}
      - file: check_if_rke2_already_exist_{{ grains['fqdn'] }}

run_install_script_{{ grains['fqdn'] }}:
  cmd.script:
    - name: "salt://rke2/scripts/install.sh"
    - env:
      - INSTALL_RKE2_TYPE: {{ role }}
      - RKE2_TOKEN: {{ token }}
    - cwd: /root
    - onchanges:
      - file: create_rke2_config_yaml_{{ grains['fqdn'] }}

service_rke2_enable_{{ grains['fqdn'] }}:
  cmd.run:
    - name: systemctl enable rke2-{{ role }}.service

service_rke2_start_{{ grains['fqdn'] }}:
  cmd.run:
    - name: systemctl start rke2-{{ role }}.service --no-block
    - order: last
{% endif %}
