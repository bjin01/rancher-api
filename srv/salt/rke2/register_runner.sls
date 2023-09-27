{% set tag = salt.pillar.get('event_tag') %}
{% set data = salt.pillar.get('event_data') %}
test_cluster_name:
  salt.function:
    - tgt: {{ data.id }}
    - name: cmd.run
    - arg:
      - echo {{ data.data.register_cluster_name }}

{% if data.data.register_cluster_name|length %}
create_cluster_token_in_rancher_{{ data.id }}:
  salt.runner:
    - name: rancher.register
    - cluster_name: {{ data.data.register_cluster_name }}
    - k8s_node: {{ data.id }}
{% endif %}

do_second_thing:
  salt.state:
    - tgt: {{ data.id }}
    - sls:
      - rke2.execute_registration
    - require:
      - salt: create_cluster_token_in_rancher_{{ data.id }}

