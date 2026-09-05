# Certificate Automation Domain Set

Status: accepted through the approved execution plan.

This repository will use separate Certificate Issuance and Certificate Comparison knowledge
contexts. They share a certificate lifecycle through Key Vault, but comparison has its own
representation, tool set, delivery process, and directional dependency on issued certificate
artifacts. The separation keeps each glossary and rule set aligned with the machinery it describes.
The accepted domain set is limited to these two contexts; future changes require
a superseding decision.

## Evidence

- Representation: issuance uses account keys, CSRs, ACME orders, and DNS challenges; comparison uses
  stable/current certificate chains, reports, notifications, and promotion.
- Tool set: issuance uses `requirements-output.txt` and the ACME entrypoints; comparison uses
  `requirements-cert-diff.txt`, a released `certdiff` wheel, and shared Azure pipeline templates.
- Delivery process: issuance and comparison have separate Azure DevOps pipeline definitions.
- Directional dependency: issuance imports the current certificate into Key Vault, and comparison
  reads current and stable certificates from Key Vault.

## Considered Options

- Separate issuance and comparison contexts: selected because four domain-promotion signals are
  evidenced on disk.
- One certificate-automation context: not selected because it merges distinct vocabulary and rules
  and would leave the comparison dependency boundary implicit.

## Consequences

- `CONTEXT-MAP.md` owns the relationship between the two contexts.
- Each context owns its glossary and rules under `docs/domain/`.
- `docs/architecture.md` owns physical components, external dependencies, and runtime flows.
- A change to the accepted domain set will require a superseding decision.
