# Automation Dependency Pinning

This standard records repeated immutable dependency conventions in the
certificate-automation pipelines. It does not replace existing rules or claim
enforcement where a pipeline only installs a requirements file.

## Standard

- Python dependency lock files use immutable package hashes with pip's
  `--require-hashes` format where the dependency set is published in the
  repository.
- The certificate-diff dependency set is kept separate from the ACME output
  dependency set so each pipeline installs the requirements it consumes.
- Pipeline templates and external task references remain pinned to the
  repository's existing template or task declarations; no new pinning system
  is introduced here.

## Evidence and exceptions

- Evidence: `requirements-output.txt`, `requirements-cert-diff.txt`, and
  `build-python.yml` contain repeated hash-pinned dependency declarations.
- Exceptions: none evidenced in the checked-in dependency files.
- Not established: a repository-wide validator that proves every dependency
  declaration is immutable, and live pipeline execution against Azure DevOps.
