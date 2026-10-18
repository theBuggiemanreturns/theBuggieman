---
name: contract-mapping
description: Map a smart-contract protocol completely before security analysis. Use first whenever an audit starts from a repository, Solidity files, a Markdown source bundle, deployed EVM addresses, or contract-info/onchain-recon output. Resolve source and runtime dependencies, proxies, deployments, roles, operational controllers, callable entry points, state relationships, asset flows, lifecycle transitions, external integrations, invariants, configuration, and blind spots; keep code provenance separate from control and scope; produce and validate the canonical protocol-map.md consumed by smart-contract-auditing. Do not hunt or report vulnerabilities in this stage.
---

# Contract Mapping

Produce a deterministic, evidence-linked description of what the protocol is and
how it behaves. Do not perform the vulnerability hunt here. Record suspicious
observations only as routing notes for the independent auditor.

## Required input

Accept one or more of:

- a repository or Solidity folder;
- a Markdown source bundle with fenced Solidity blocks;
- deployed EVM address(es) and chain(s);
- saved `contract-info` or `onchain-recon` output;
- specifications, deployment manifests, previous audit scope, and known issues.

Record exactly what was supplied and what was discovered. Never represent a docs
bundle as a complete protocol until dependencies and deployments are checked.

Read source selectively. Run deterministic gap and recon tools first, then use
model attention to interpret their closed-set outputs and load-bearing behavior.

## Workflow

### 1. Establish identity and scope

Pin the protocol name, audit mode, authorization, repository and commit, compiler
and build settings, chains, addresses, proxy implementations, in-scope and
out-of-scope components, and evidence locations.

If the input includes deployed EVM code, read
`references/contract-info-integration.md` and collect raw inspector output.

### 2. Normalize and close the source set

Run this before reading files one at a time:

```bash
python3 scripts/find_gaps.py <source-or-markdown-path> --json
```

Resolve every project-owned import and inherited type. Record third-party
libraries with exact versions or commits; do not assume a standard-library name
makes its implementation or version irrelevant. Re-run until every remaining gap
is explicitly classified.

Resolution order:

1. local repository, submodules, dependency locks, `lib/`, or `node_modules/`;
2. verified deployment source and proxy/beacon/clone implementation;
3. official upstream repository at the pinned dependency revision;
4. explicit unresolved item with scope impact—never guessed source.

### 3. Close deployment-time and runtime edges

Imports cannot reveal constructor-supplied addresses, proxy slots, factory
products, registry values, multicall payloads, or mutable integration settings.
For deployed inputs, or whenever value/control flows point outside the source
graph, read the `onchain-recon` skill and collect `onchain-graph.md` plus its raw
evidence. Prefer its batched read-only scripts over one RPC call at a time.

Merge confirmed recon edges into the canonical map. The recon graph is evidence,
not a competing map. Treat heuristic address hits, selector guesses, failed calls,
and non-standard deployment patterns as unresolved until decoded manually.

### 4. Separate provenance, operational control, and scope

Never use “external,” “third-party,” “canonical,” or “forked” as a scope verdict.
For every deployed dependency and privileged off-chain actor, record three
independent facts:

1. **Code provenance:** in-house, exact upstream, modified upstream, or unknown,
   with a pinned revision/hash when known.
2. **Operational control:** current owner/admin/beacon/proxy admin, role holders,
   governance/timelock, mutable router/oracle/fee/receiver authorities, or an
   explicitly unresolved controller at a pinned block.
3. **Scope verdict:** in scope, integration-only review, or out of scope, with the
   authorization/scope evidence and security consequence.

Build a normalized set of known protocol actors from deployers, constructor
recipients, owners, role holders, fee recipients, multisigs, timelocks, keepers,
and upgrade authorities. Cross-check every dependency controller against that set.
An exact match, shared role holder, or governance overlap means the dependency is
self-operated or jointly controlled and must not be dismissed as third-party.
Unknown control is a limitation, not evidence of independence.

Exact upstream code can reduce source-diff effort. It never removes the need to
review protocol-controlled configuration, initialization, ownership, upgrades,
assets, callbacks, or integration assumptions.

### 5. Reproduce mechanical facts

Attempt the native build and existing tests. Record failures rather than hiding
them. When compilation works, use Slither or equivalent output for inheritance,
call graph, state, and function visibility. Treat tools as evidence generators;
verify material classifications against source.

Useful EVM commands when installed:

```bash
slither . --print inheritance-graph,call-graph,human-summary
surya inheritance 'src/**/*.sol'
surya graph 'src/**/*.sol'
```

If a partial Markdown bundle cannot compile, continue with gap analysis and manual
evidence, but mark build/static-analysis limitations.

### 6. Map behavior, not merely filenames

Fill every section of `references/map-template.md`:

- contract/dependency/proxy graph;
- roles and exact powers;
- every public/external entry point, callback, hook, fallback, receive, and
  inherited admin surface;
- state reads/writes and variables that must change together;
- assets, liabilities, shares, debt, rewards, and every value-moving path;
- phases, transitions, terminal states, cancellation, pause, and recovery;
- external calls, trust boundaries, token/oracle/bridge/DEX assumptions;
- code provenance, operational controller, controller overlap, and evidenced scope
  verdict for every external/runtime dependency;
- numbered invariants linked to affected entry points;
- deployed configuration and source/bytecode match;
- unresolved facts and their impact on downstream coverage.

Verify important relationships in both directions. For example, do not only note
that a factory points to an implementation; check that the implementation or
registry recognizes the same factory where such a reverse relation exists.

### 7. Set the handoff status

Use exactly one:

- `READY_FOR_AUDIT`: material source, deployment configuration, and controller
  relationships are resolved;
- `READY_WITH_LIMITATIONS`: bounded gaps remain and are explicitly tied to
  affected contracts, invariants, and audit passes;
- `BLOCKED`: missing source, control, or configuration would make downstream
  conclusions misleading.

An empty section is incomplete, not evidence that the category does not exist.
Write `None found — <evidence>` only after checking.

Do not use `READY_FOR_AUDIT` while a material dependency's controller or control
overlap is unknown. Use `READY_WITH_LIMITATIONS` only when downstream coverage can
be bounded honestly; otherwise use `BLOCKED`.

### 8. Validate

Save the canonical file as `protocol-map.md`, then run:

```bash
python3 scripts/validate_map.py path/to/protocol-map.md
```

Fix structural failures. Do not change a justified `BLOCKED` status merely to
make validation pass.

## Output contract

Return:

1. `protocol-map.md` using the exact template headings;
2. paths to raw source, `contract-info`, recon, build/test, and graph evidence;
3. the validator result;
4. a short list of facts the auditor must not assume.

The downstream `smart-contract-auditing` skill consumes this file without
reconstructing the protocol from scratch. If later tracing contradicts the map,
correct the map and rerun every affected audit pass.
