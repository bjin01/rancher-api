rke2:
  role:
    server:
      - INTG-K8S-01
      - INTG-K8S-02
      - INTG-K8S-03
    agents:
      - INTG-worker-01.example.com
      - INTG-worker-03.example.com
      - INTG-worker-02.example.com
  first_node: INTG-K8S-01
  tls_san:
    - intg-k8s-01.example.com
    - intg-k8s-02.example.com
    - intg-k8s-03.example.com
    - k8s-test.example.com
  token: asdfpiuwr9
  register_rancher_cluster_name: int-k8s
  root_bashrc: |
      export PATH=$PATH:/var/lib/rancher/rke2/bin

