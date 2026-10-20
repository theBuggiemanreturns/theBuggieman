# Target: chain-overflow-invariant

A minimal ERC20-style vault. Users batch-deposit via `batchCredit`, which sums an
array of amounts into a running total and mints shares equal to the aggregate. A
`supplyInvariant()` guard is supposed to guarantee total minted never exceeds
`CAP`.

Mode: hunt. Authorization: local fork only. Scope: `src/Vault.sol`.
