# Pass: Guard-Audit (treat every guard as a target)

The defense is an attack surface. In the XRPL infinite mint, the critical half of
the chain was the *invariant that was supposed to prevent minting XRP* — its
accumulator was a signed int64 and wrapped exactly like the bug it was meant to
catch. The guard did not just fail to help; it actively waved the attack through.

Run this pass after the first hypothesis round and again whenever the map grows.

## Enumerate the guards

List every mechanism whose job is to *stop* something:
- `require` / `revert` / custom-error checks
- invariant checks and post-condition assertions
- supply caps, per-account caps, rate limits, cooldowns
- access modifiers and role checks
- reentrancy locks, pause switches, circuit breakers
- slippage / min-out / deadline checks
- oracle staleness / bounds / sanity checks

For each guard record, in the primitives ledger (CLASS the row `GUARD`):
- **Protects:** which property or invariant it enforces.
- **Reads:** what inputs/state it depends on (type, source, who can move it).
- **Math:** the exact comparison and the accumulator/variable types involved.

## Attack each guard

Ask, per guard:
1. **Can it be bypassed?** An alternate entry point, a sibling function, an early return, a path that never reaches it.
2. **Can it be made to lie?** Can I control its inputs so it reads a false value and passes a bad state? (wrong denomination, stale cache, attacker-set oracle, donated balance.)
3. **Can the guard's own math break?** Same questions you ask the logic: overflow/underflow, rounding, signed/unsigned, narrowing cast, an accumulator that wraps over the *aggregate* instead of per-item.
4. **Does it share a mechanism with what it guards?** If the guard and the guarded code rely on the **same** type, counter, oracle, or assumption, one break disables both. This is the richest chain seam.
5. **Is it disabled by a reachable prior state?** Pausing, role changes, config writes, migration — can a valid action turn the guard off before the exploit?

## Output

Every guard becomes a ledger row. A guard that fails any question above is a
primitive, not a finding yet — feed it to the composition pass, where
"primitive + its own broken guard" is the first pairing to try.

## Anti-patterns
- Assuming a named check (`nonReentrant`, `onlyOwner`, `XRPNotCreated`) works because of its name.
- Checking that a guard *reverts on the obvious input* and concluding it is sound.
- Auditing the business logic but never the invariant/library code that policies it.
