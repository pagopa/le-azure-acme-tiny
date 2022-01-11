# le-azure-acme-tiny

This repo contains all the script mandatory to create and renew Let's encrypt certificates
used inside PagoPA projects

## acme_tiny.py

This script automates the process of getting a signed TLS certificate from Let's Encrypt using
the ACME protocol.

It is intented to be run in a Azure DevOps pipeline and have access to your private account key.
And be able to create/destroy a DNS TXT records to comunicate with Let's Encrypt

## generate_csr.py

This script generates a CSR in DER format.

## azure-pipelines.yaml

Pipeline that allow to launch and orchestrate all the script to be able to generate the Let's Encrypt certificate and save it inside your KeyVault
