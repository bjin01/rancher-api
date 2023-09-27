run_orch_file_{{ data['id'] }}:
  runner.state.orchestrate:
    - args:
        - mods: rke2.register_runner
        - pillar:
            event_tag: {{ tag }}
            event_data: {{ data|json }}
