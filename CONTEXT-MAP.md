# Context Map

## Contexts

- [Certificate Issuance](docs/domain/certificate-issuance/CONTEXT.md) - decides when to renew,
  creates request material, completes ACME DNS validation, and stores the selected certificate.
- [Certificate Comparison](docs/domain/certificate-comparison/CONTEXT.md) - compares stable and
  current certificates, reports differences, and selects the notification and promotion actions.

## Relationships

- **Certificate Issuance -> Certificate Comparison**: Issuance imports the selected certificate
  into Key Vault as the current certificate. Comparison reads the current and stable certificates
  from Key Vault before selecting notification and promotion actions.
