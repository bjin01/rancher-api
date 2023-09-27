#!/bin/bash
KUBECTL="/var/lib/rancher/rke2/bin/kubectl"
KUBECONF="/etc/rancher/rke2/rke2.yaml"
if [ -f $KUBECTL ] && [ -f $KUBECONF ]
then
    echo "$1"
    curl -k $1 -o /tmp/register.yaml
    $KUBECTL --kubeconfig=$KUBECONF apply -f /tmp/register.yaml
    rm /tmp/register.yaml
fi

