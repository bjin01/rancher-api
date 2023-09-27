{% set minionid = grains['id'] %}
{% set k8scmd = grains['rancher_registration_curl_cmd'] %}
{% if k8scmd|length %}
run_kubectl_cmd_{{ minionid }}:
  cmd.script:
    - name: salt://rke2/scripts/register_rancher.sh "{{ k8scmd }}"
    - source: salt://rke2/scripts/register_rancher.sh
    - cwd: /tmp
    - timeout: 30
{% endif %}
