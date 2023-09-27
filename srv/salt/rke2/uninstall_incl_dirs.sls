lets_uninstall_rke2_{{ grains['fqdn'] }}:
  cmd.run:
    - name: /usr/local/bin/rke2-uninstall.sh

delete_directories_rke2_etc_{{ grains['fqdn'] }}:
  file.directory:
    - name: /etc/rancher/rke2
    - clean: True

/var/lib/rancher/rke2_{{ grains['fqdn'] }}:
  file.directory:
    - name: /var/lib/rancher/rke2
    - clean: True
