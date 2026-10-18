# On-chain Recon — [Protocol Name]

**Chain / chain ID:** [value]
**Reference block:** [value]
**Evidence directory:** [path]
**Tool versions:** [cast/jq/python/inspector versions]

## 1. Starting point and question

| Field | Value |
|---|---|
| Starting address(es) | |
| Creation transaction(s) | |
| Trusted RPC/explorer | |
| Mapping question / trigger | |
| Existing contract-info/source/ABI evidence | |

## 2. Known protocol actors

Normalize addresses before comparing them.

| Actor/address | How discovered | Role/power | Evidence block/transaction |
|---|---|---|---|
| | | | |

## 3. Confirmed and rejected candidates

Never promote an address-shaped word without confirming evidence. Keep rejected
candidates so the mapper can see what was checked.

| Address | Discovery edge | Confirming/rejecting evidence | Code/proxy/source status | Code provenance | Operational controller | Control overlap | Proposed scope treatment | Mapping action |
|---|---|---|---|---|---|---|---|---|
| | | | | in-house/exact upstream/modified upstream/unknown | address/role/unresolved | match/overlap/unrelated/unresolved | in scope/integration-only/out of scope/unresolved | merge/reject/manual resolution |

A provenance result is never a scope result. Exact-upstream code that is
self-operated or integration-critical still requires configuration, control,
asset, callback, and trust-boundary review.

## 4. Runtime edges to merge

Represent each confirmed edge explicitly:

```text
[source] --[constructor/config/getter/factory/proxy/call]--> [target]
```

For each edge, name the raw evidence file and pinned block/transaction.

## 5. Prioritized mapping work

1. Modified/project-specific code with asset or control authority.
2. Exact-upstream code that is self-operated, mutable, or integration-critical.
3. Unrelated third-party dependencies at their trust boundaries.

## 6. Unresolved or non-standard patterns

List CREATE2/custom-factory decoding, proxy ambiguity, failed getter calls,
unverified code, unknown controllers, missing role history, and any script result
that required manual resolution. Propagate material items to `protocol-map.md`
section 12.
