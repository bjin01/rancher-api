{% set this_minion = salt['grains.get']('id', '') %}

{% if salt['file.file_exists']('/usr/local/bin/rke2') %}
backup_etcd_to_s3_{{ this_minion }}:
  cmd.script:
    - name: salt://rke2/scripts/etcd_backup.sh 
    - template: jinja
{% endif %}
