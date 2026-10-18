# Contract-info integration

Use the bundled EVM inspector at `../../../tools/contract-info/` when mapping a
deployed address.

## Collect a root contract

```bash
cd ../../../tools/contract-info
./ci <address> <chain-name-or-id>
```

The tool saves:

- `src/`: verified source files;
- `abi.json`: readable callable/event surface;
- `report.json`: chain identity, deployed address, bytecode-derived state, token
  metadata, owner/pause probes, proxy slots, deployment record, compiler settings,
  source provider, implementations, and source file map.

Preserve the raw output as mapping evidence. Do not edit it into the map by hand
and then discard the original.

## Recurse through the protocol

1. Inspect the root address.
2. If it is an EIP-1967, beacon, or EIP-1167 proxy, inspect every implementation
   and identify its relationship to the proxy.
3. From source, ABI, constructor/initializer arguments, getters, registries,
   factories, events, and frontend configuration, enumerate runtime dependencies.
   Invoke `onchain-recon` to batch deployment/getter evidence when needed.
4. Inspect every material address enough to determine bytecode/proxy identity,
   code provenance, operational controller, overlap with known protocol actors,
   and trust-boundary behavior. Exact upstream token/oracle/router/library code may
   lower source-diff priority, but it is not automatically unrelated or out of
   scope.
5. Verify chain ID and bytecode at every address. An explorer page or filename is
   not sufficient identity evidence.
6. Compare verified source compiler/optimizer settings with the repository and
   record any deployed-versus-repository mismatch.

## Limitations

- `contract-info` is EVM-only.
- Public registry RPCs and explorers can be stale, rate-limited, or incomplete.
- A verified proxy shell is not the implementation logic.
- An ABI does not prove source equivalence.
- Generic read probes such as `owner()` or `paused()` do not discover custom roles.
- Source fetched from multiple providers may use different path layouts; pin the
  compiler metadata and deployed bytecode, not only filenames.

Any failure that affects coverage belongs in `protocol-map.md` sections 2 and 12.
