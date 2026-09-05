# Architecture Decision Records

Repository-wide architectural decisions live in this directory. Use this index to find the current
record and the lifecycle rules that protect accepted decisions.

No diagram is provided in this README because the records form a linear index with fewer than three
material relationships.

## Contents

- [Record format](#record-format)
- [Decision lifecycle](#decision-lifecycle)
- [Validation](#validation)
- [Decisions](#decisions)

## Record format

Use sequential filenames in the form `NNNN-<slug>.md`. Each record contains, in order:

1. An H1 matching the filename subject.
2. `Status: proposed`, `accepted`, `rejected`, `deprecated`, or `superseded by ADR-NNNN`.
3. A short summary of the context, decision, and rationale.
4. Optional `Evidence`, `Considered Options`, and `Consequences` sections when they preserve
   material information.

## Decision lifecycle

A new decision starts as `proposed`; only explicit repository authority may mark it `accepted`.
An accepted body is immutable. A changed accepted decision requires a new record, and both records
must identify the supersession.

## Validation

From the repository root, run the repository hooks on changed records:

```sh
pre-commit run --files docs/adr/README.md docs/adr/0001-certificate-automation-domain-set.md
```

For tracked ADR edits, also run Git's whitespace check:

```sh
git diff --check -- docs/adr
```

Also verify sequential numbering, status vocabulary, heading/filename identity, and local links.

## Decisions

- [0001 - Certificate automation domain set](0001-certificate-automation-domain-set.md) - Proposed
  separation of issuance and comparison knowledge contexts.
