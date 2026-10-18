---
name: onchain-recon
description: Batch read-only EVM reconnaissance for contract mapping. Use with contract-mapping whenever deployed addresses, constructor arguments, creation transactions, multicalls, proxies, factories, registries, zero-argument getters, or runtime configuration may reveal dependencies and controllers that imports cannot; also use when source-level flows do not explain deployed behavior. Extract and verify candidate addresses, sweep safe ABI getters, compare source with pinned upstream templates, record raw evidence at a pinned chain/block, and produce onchain-graph.md for the canonical protocol map. Never infer scope from canonical/external provenance and never broadcast transactions.
---

# On-chain Recon

Acquire deployment and runtime facts mechanically so `contract-mapping` spends
reasoning on interpretation rather than one RPC lookup at a time. This skill is a
mapping sidecar: its graph is evidence that must be merged into `protocol-map.md`,
not a competing architecture or a vulnerability report.

## Safety and evidence contract

- Work only on authorized, user-owned, or published in-scope targets.
- Use read-only RPC/explorer operations. Never sign or broadcast a transaction.
- Pin chain ID, addresses, creation transaction, reference block, source revision,
  and output paths. Do not store RPC credentials in artifacts.
- Treat address extraction and selector resolution as heuristics until confirmed
  by bytecode, ABI/source, receipt/log, storage slot, or successful typed call.
- Stop and record non-standard patterns; do not turn an empty script result into
  “no dependency.”
- Record tool versions and failures. Preserve raw JSON/TSV beside the synthesis.

## Workflow

### 1. Establish the recon target

Record the starting address, chain ID/name, trusted RPC/explorer, reference block,
creation transaction when known, and the source/map question being answered. Use
`references/onchain-graph-template.md` from the start.

If `contract-info` already produced verified source, ABI, proxy information, or a
creation transaction, reuse those artifacts instead of refetching them.

### 2. Trace deployment and encoded addresses in batches

Run:

```bash
scripts/trace_deployment.sh <address> <rpc-url> <creation-tx-hash>
```

The script saves the transaction, checks address-shaped calldata words, and batches
`eth_getCode` checks. A creation transaction input also contains init code, so
candidate words are a shortlist—not decoded constructor arguments.

For any standalone calldata/event blob, run:

```bash
python3 scripts/extract_candidate_addresses.py <hex> --skip-selector
```

Confirm every material hit against deployed bytecode and typed evidence. Manually
decode CREATE2 salts, custom factories, nested structs, unusual proxies, and
non-standard multicalls when the scripts cannot.

### 3. Resolve runtime configuration and control

For every confirmed contract, resolve proxy/implementation/beacon/admin slots,
factory or registry relationships, and verified ABI/source. Batch zero-argument
read-only getters:

```bash
scripts/sweep_view_functions.sh <address> <rpc-url> <abi.json> [block]
```

Use the results to locate tokens, pools, routers, vaults, fee receivers, owners,
admins, implementations, and other configured dependencies. Parameterized
AccessControl membership, enumerable roles, event-derived role history, multisig
owners/thresholds, timelocks, and governance still require explicit checks.

Build a normalized protocol-actor set from deployers, constructor recipients, role
holders, fee recipients, keepers, proxy/beacon admins, multisigs, and timelocks.
Compare every discovered controller against it and record exact match, partial
overlap, unrelated with evidence, or unresolved.

### 4. Compare source provenance without making a scope decision

Run, when network/cache access is authorized:

```bash
scripts/check_canonical.sh <local-source-dir-or-file>
```

`EXACT_UPSTREAM` lowers source-diff priority. `CUSTOM_OR_MODIFIED` raises it.
Neither result decides scope. Exact upstream code can be protocol-controlled,
misconfigured, incorrectly initialized, or used through unsafe glue. Review its
live control, configuration, asset custody, callbacks, and integration behavior.

Pin the upstream repository and revision used for comparison. Filename-only
matching is a prefilter; confirm any material match against the expected path and
revision.

### 5. Synthesize the evidence

Complete `onchain-graph.md` using the template. For each address record:

- discovery edge and confirming evidence;
- code/proxy/source status;
- code provenance;
- operational controller and evidence block;
- overlap with known protocol actors;
- proposed scope treatment and mapping action;
- unresolved facts.

Prioritize attention in this order:

1. modified upstream or project-specific code with asset/control authority;
2. exact upstream code that is self-operated, mutable, or integration-critical;
3. genuinely unrelated third-party dependencies, reviewed at the trust boundary.

Do not label any address “skip.” A dependency may receive lower source-review
priority while its configuration and integration assumptions remain in scope.

## Handoff and completion gate

Return:

1. `onchain-graph.md`;
2. raw transaction, receipt, getter, bytecode, source, and comparison evidence;
3. unresolved/non-standard patterns requiring manual mapping;
4. the exact rows to merge into `protocol-map.md`.

Recon is complete only when every material candidate is confirmed or explicitly
rejected with evidence, every material contract has a controller classification,
and unresolved control/runtime edges are propagated to mapping limitations.

## Resource map

- `scripts/trace_deployment.sh`: batch creation-transaction address/code checks.
- `scripts/extract_candidate_addresses.py`: offline heuristic address extractor.
- `scripts/sweep_view_functions.sh`: batch zero-argument view/pure calls.
- `scripts/check_canonical.sh`: exact-upstream versus custom/modified prefilter.
- `references/known-templates.txt`: pinned upstream comparison sources.
- `references/onchain-graph-template.md`: recon-to-mapping output contract.
