# le-azure-acme-tiny

This repository automates Let's Encrypt certificate issuance and renewal for Azure resources.
Azure DevOps pipelines coordinate the Python entrypoints, Azure DNS validation, and Key Vault storage.

## Contents

- [Purpose](#purpose)
- [Responsibilities](#responsibilities)
- [Inputs and outputs](#inputs-and-outputs)
- [Dependencies and execution](#dependencies-and-execution)
- [Validation](#validation)
- [Related documentation](#related-documentation)

## Purpose

Use this repository when a certificate must be generated, renewed, compared with a stable
certificate, or stored in Azure Key Vault. The issuance path uses the ACME DNS-01 challenge.

## Responsibilities

- `generate_csr.py` creates a DER-encoded certificate signing request and an RSA private key.
- `acme_tiny.py` submits the request to Let's Encrypt, creates Azure DNS TXT records, attempts their
  cleanup, and writes the returned certificate chain.
- `azure-pipelines.yaml` and `azure-pipelines-federated.yaml` decide whether renewal is needed,
  run issuance, select a chain, and import the result into Key Vault.
- `azure-pipeline-cert-diff.yaml` compares stable and current certificate chains and can send a
  notification, promote the current certificate, or do both during forced renewal.

## Inputs and outputs

The pipelines read their Python version from `.python-version` and receive Azure DevOps variables
for Key Vault, DNS, certificate, identity, and notification configuration. Issuance also receives
the Let's Encrypt account key and registration record as pipeline-provided values; their contents
must not be committed.

The main artifacts are a DER CSR, a private key, a PEM certificate chain, a PFX used for Key Vault
import, and a JSON certificate-comparison report. The pipeline cleanup tasks remove the account,
key, CSR, PEM, PFX, and DER files listed in their unconditional cleanup steps.

## Dependencies and execution

- Use the Python version recorded in `.python-version`.
- Issuance dependencies are pinned in `requirements-output.txt`.
- Certificate-diff dependencies are pinned in `requirements-cert-diff.txt`.
- Run the Python scripts from an Azure DevOps job with the Azure DNS and Key Vault permissions
  required by the selected pipeline and identity mode.

No diagram is provided in this README because the cross-component flow is owned by
[the architecture document](docs/architecture.md).

## Validation

Run the repository's safe local checks before changing pipeline behavior:

```sh
python3 -m compileall -q acme_tiny.py generate_csr.py
pre-commit run --all-files
```

The CI workflow also installs both hashed dependency sets, and the pre-commit workflow runs the
repository's pinned hooks in a container. There is no Makefile or project test suite in this
repository.

## Related documentation

- [Context map](CONTEXT-MAP.md)
- [Architecture](docs/architecture.md)
- [Certificate issuance rules](docs/domain/certificate-issuance/RULES.md)
- [Certificate comparison rules](docs/domain/certificate-comparison/RULES.md)
- [Architecture decisions](docs/adr/README.md)

---
## Repository Structure & Details (Auto-generated)

### Scopo
Automatizza richiesta e rinnovo di certificati Let's Encrypt per risorse Azure, integrandosi con DNS e pipeline CI per assicurare continuità TLS senza interventi manuali.

### Cartelle
- `acme_tiny.py`: client ACME custom.
- `generate_csr.py`: generazione CSR.
- `azure-pipelines*.yaml`: pipeline Azure DevOps per issuance/renewal.

### Script
- `acme_tiny.py`: client ACME.
- `generate_csr.py`: generazione CSR.

### Workflow
- `build-python.yml`: build e test.

### Note
Processo ACME custom; attenzione a finestre di rinnovo e permessi DNS.
