# Certificate Comparison Rules

These rules govern dependency verification, comparison, promotion, and cleanup in this repository.

## CERT-CMP-001 - Hash-verified comparison dependencies

- Rule ID: CERT-CMP-001
- Owner: Certificate Comparison context
- Severity: blocking
- Enforcement owner: Azure DevOps and GitHub Actions install steps
- Evidence: [azure-pipeline-cert-diff.yaml](../../../azure-pipeline-cert-diff.yaml),
  [build-python.yml](../../../.github/workflows/build-python.yml)
- Remediation: Install `requirements-cert-diff.txt` with `--require-hashes` and update every
  required hash when comparison dependencies change.
- Rule: CI dependency installation for certificate comparison must require hashes.

## CERT-CMP-002 - Released wheel checksum

- Rule ID: CERT-CMP-002
- Owner: Certificate Comparison context
- Severity: blocking
- Enforcement owner: `azure-pipeline-cert-diff.yaml` checksum step
- Evidence: [azure-pipeline-cert-diff.yaml](../../../azure-pipeline-cert-diff.yaml)
- Remediation: Stop before installation when the downloaded `certdiff` wheel does not match its
  released SHA-256 value.
- Rule: The comparison pipeline must verify the downloaded `certdiff` wheel checksum before
  installing it.

## CERT-CMP-003 - Certificate promotion gate

- Rule ID: CERT-CMP-003
- Owner: Certificate Comparison context
- Severity: blocking
- Enforcement owner: `azure-pipeline-cert-diff.yaml` `ChangeCertificate` condition
- Evidence: [azure-pipeline-cert-diff.yaml](../../../azure-pipeline-cert-diff.yaml)
- Remediation: Restore the `Renew` or forced-renewal condition before permitting promotion.
- Rule: The current certificate may replace the stable certificate only when comparison selects
  `Renew` or the current certificate carries the forced-renewal state.

## CERT-CMP-004 - Temporary comparison artifact cleanup

- Rule ID: CERT-CMP-004
- Owner: Certificate Comparison context
- Severity: blocking
- Enforcement owner: Azure DevOps `CleanupEverything` step
- Evidence: [azure-pipeline-cert-diff.yaml](../../../azure-pipeline-cert-diff.yaml)
- Remediation: Keep cleanup unconditional and extend its file list when comparison creates another
  PEM, PFX, or DER artifact.
- Rule: The comparison job must unconditionally remove its temporary PEM, PFX, and DER files.

## CERT-CMP-005 - Required comparison certificates

- Rule ID: CERT-CMP-005
- Owner: Certificate Comparison context
- Severity: blocking
- Enforcement owner: `azure-pipeline-cert-diff.yaml` input file checks
- Evidence: [azure-pipeline-cert-diff.yaml](../../../azure-pipeline-cert-diff.yaml)
- Remediation: Restore both the stable and current PFX downloads before starting certificate-chain
  extraction.
- Rule: Stable and current PFX files must both exist before certificate comparison starts.
