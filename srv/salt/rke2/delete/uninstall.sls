lets_uninstall_rke2_{{ grains['fqdn'] }}:
  cmd.run:
    - name: /usr/local/bin/rke2-uninstall.sh
