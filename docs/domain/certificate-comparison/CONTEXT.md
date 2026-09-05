# Certificate Comparison

This context defines the language for comparing stable and current certificates, reporting their
differences, and selecting the notification and promotion actions that follow.

## Language

**Certificate comparison**:
An evaluation of stable and current certificate chains whose result informs notification or
promotion.
_Avoid_: certificate diff

**Stable certificate**:
The certificate currently treated as the comparison baseline for a managed resource.
_Avoid_: old certificate

**Current certificate**:
The candidate certificate stored under the current Key Vault name and evaluated against the stable
certificate.
_Avoid_: new certificate

**Comparison action**:
The pipeline outcome that selects notification, promotion, both actions during forced renewal, or
no action.
_Avoid_: renewal decision

**Certificate promotion**:
Replacing the stable certificate with the current certificate after the comparison gate permits it.
_Avoid_: certificate switch
