{% set this_minion = salt['grains.get']('id', '') %}
check_if_rke2_lock_is_present_{{ this_minion }}:
  file.missing:
    - name: /etc/rke2.lock

lets_uninstall_rke2_{{ grains['fqdn'] }}:
  cmd.run:
    - name: /usr/local/bin/rke2-uninstall.sh
    - require:
      - file: check_if_rke2_lock_is_present_{{ this_minion }}
