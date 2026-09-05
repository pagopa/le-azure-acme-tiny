# Certificate Issuance Rules

These rules govern certificate renewal, request generation, ACME validation, and storage in this
repository.

## CERT-ISS-001 - Required DNS execution context

- Rule ID: CERT-ISS-001
- Owner: Certificate Issuance context
- Severity: blocking
- Enforcement owner: `acme_tiny.py` startup checks
- Evidence: [acme_tiny.py](../../../acme_tiny.py)
- Remediation: Provide the required Azure subscription, DNS resource group, and DNS zone values
  before running issuance.
- Rule: Issuance must have `AZURE_SUBSCRIPTION_ID`, `AZURE_DNS_ZONE_RESOURCE_GROUP`, and
  `AZURE_DNS_ZONE` available before it starts.

## CERT-ISS-002 - Hash-verified dependencies

- Rule ID: CERT-ISS-002
- Owner: Certificate Issuance context
- Severity: blocking
- Enforcement owner: Azure DevOps and GitHub Actions install steps
- Evidence: [azure-pipelines.yaml](../../../azure-pipelines.yaml),
  [azure-pipelines-federated.yaml](../../../azure-pipelines-federated.yaml),
  [build-python.yml](../../../.github/workflows/build-python.yml)
- Remediation: Install `requirements-output.txt` with `--require-hashes` and update every required
  hash when issuance dependencies change.
- Rule: CI dependency installation for issuance must require hashes.

## CERT-ISS-003 - DNS challenge cleanup

- Rule ID: CERT-ISS-003
- Owner: Certificate Issuance context
- Severity: warning
- Enforcement owner: not enforced
- Evidence: [acme_tiny.py](../../../acme_tiny.py)
- Remediation: Put each TXT-record deletion in a `finally` path that also covers update failures,
  then add a focused failure-path check.
- Rule: After creating a DNS-01 TXT record, issuance must attempt to delete it whether challenge
  processing succeeds or fails.

## CERT-ISS-004 - Temporary issuance artifact cleanup

- Rule ID: CERT-ISS-004
- Owner: Certificate Issuance context
- Severity: blocking
- Enforcement owner: Azure DevOps `CleanupEverything` steps
- Evidence: [azure-pipelines.yaml](../../../azure-pipelines.yaml),
  [azure-pipelines-federated.yaml](../../../azure-pipelines-federated.yaml)
- Remediation: Keep cleanup unconditional and extend its file list when issuance creates another
  account, key, CSR, certificate-chain, or PFX artifact.
- Rule: Issuance jobs must unconditionally remove their temporary account files, private keys,
  CSRs, certificate chains, and PFX files.

## CERT-ISS-005 - DNS zone containment

- Rule ID: CERT-ISS-005
- Owner: Certificate Issuance context
- Severity: blocking
- Enforcement owner: `acme_tiny.py` CSR domain validation
- Evidence: [acme_tiny.py](../../../acme_tiny.py)
- Remediation: Use a CSR whose common name and subject alternative names belong to the configured
  Azure DNS zone.
- Rule: Every domain in the CSR must end with the configured `AZURE_DNS_ZONE`.

## CERT-ISS-006 - HTTPS ACME transport

- Rule ID: CERT-ISS-006
- Owner: Certificate Issuance context
- Severity: blocking
- Enforcement owner: `acme_tiny.py` request schema check
- Evidence: [acme_tiny.py](../../../acme_tiny.py)
- Remediation: Configure an HTTPS ACME directory and reject non-HTTPS request targets.
- Rule: Every ACME request URL must use HTTPS.

## CERT-ISS-007 - Supported Azure identity mode

- Rule ID: CERT-ISS-007
- Owner: Certificate Issuance context
- Severity: blocking
- Enforcement owner: `acme_tiny.py` DNS client construction
- Evidence: [acme_tiny.py](../../../acme_tiny.py)
- Remediation: Set `AZURE_IDENTITY_TYPE` to `CLIENT_SECRET` or `MANAGED_IDENTITY`; in client-secret
  mode, also provide the client ID, client secret, and tenant ID.
- Rule: Azure DNS operations must use a supported identity mode and its required credential inputs.
