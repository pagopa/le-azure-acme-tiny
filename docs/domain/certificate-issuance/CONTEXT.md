# Certificate Issuance

This context defines the language for deciding when to renew a certificate, creating its request
material, completing ACME DNS validation, and storing the selected certificate.

## Language

**Certificate renewal**:
Issuing a replacement when the existing certificate is absent or expiring, or when an operator
explicitly forces a new issuance.
_Avoid_: certificate rotation

**Renewal decision**:
The issuance outcome that determines whether the existing certificate is retained or a new
certificate is requested.
_Avoid_: renewal check

**Certificate signing request (CSR)**:
A request that identifies the certificate subject and is signed by the private key paired with the
issued certificate.
_Avoid_: certificate request

**ACME account**:
The Let's Encrypt registration identity used to authenticate certificate orders.
_Avoid_: Azure account

**DNS-01 challenge**:
An ACME domain-control proof that uses a TXT record below `_acme-challenge`.
_Avoid_: DNS check

**Certificate chain**:
The issued certificate together with the intermediate and root certificates selected for storage.
_Avoid_: certificate file
