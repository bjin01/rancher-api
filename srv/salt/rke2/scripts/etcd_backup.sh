#!/bin/bash

rke2 etcd-snapshot \
  --s3 \
  --s3-region={{ pillar['rke2_backup']['region'] }} \
  --s3-bucket={{ pillar['rke2_backup']['bucket'] }} \
  --s3-access-key={{ pillar['rke2_backup']['access-key'] }} \
  --s3-secret-key={{ pillar['rke2_backup']['secret-key'] }} >/dev/null 2>/dev/null 

