# 09 — Denial of service, griefing & unbounded loops

## DOS-01 — Permissionless action grows an array without bound
**Root cause.** Every call to a permissionless function (deposit, mint,
etc.) appends to an array that is later iterated in full by some other
function; an attacker who is allowed to call the append path many times
cheaply can grow the array until the iterating function runs out of gas.
**Precedents.** Aegis Staked YUSD H-1 (Critical) — every deposit/mint adds
a lockup element to an array; an attacker deposits on behalf of a victim
repeatedly to fill the array and OOG-DoS that victim's withdrawal
specifically (targeted, not just protocol-wide).
**Detection.** For every `push()` onto a storage array reachable from a
permissionless function, find every function that loops over that array
and ask what caps its length.

## DOS-02 — Anyone can spam a request queue to grief legitimate users
**Root cause.** A queue-based withdrawal/redemption system processes
requests in order or in batches; an attacker can flood it with many tiny
requests, delaying or blocking genuine users' processing.
**Precedents.** `BatchOut::withdrawFulfill()` H04 (Clip Finance
Strategies, Critical) — spammable withdrawal-request scheduling with
little-to-no cost, OOG-reverting the fulfillment path.
**Detection.** Any queue with permissionless enqueue and a bounded-gas
dequeue/process step: check for a minimum size, a per-address rate limit,
or a fee that makes spam uneconomical.

## DOS-03 — Low-cost front-run forces a legitimate call to revert
**Root cause.** A privileged or time-sensitive call (liquidation, a
first-of-kind state transition) can be preempted by a trivial ("1 wei")
front-run from anyone, making the real call revert or behave differently
than intended — used to *avoid* an unwanted outcome (e.g. dodge
liquidation) rather than to extract value directly.
**Precedents.** INIT Capital H-01 (Code4rena, Critical) — a borrower could
front-run their own liquidation with a 1-wei partial liquidation to break
an assumption the liquidator's transaction relied on, indefinitely
avoiding real liquidation.
**Detection.** Any liquidation/settlement path whose correctness depends
on an assumption about the account's *current* state at execution time
(not the state the liquidator observed when building the transaction) —
check whether a trivial self-triggered state change can invalidate a
pending liquidation.

## DOS-04 — Full historical array/period iterated with no pagination
**Root cause.** A view or state-mutating function loops from "the first
ever period/epoch/element" to the present on every call; as the protocol
ages, the loop eventually exceeds the block gas limit.
**Precedents.** `IRamsesGauge(gauge).getReward()` L-1 (Yieldoor Gauges) —
iterates every period since the gauge's first period, every time. Maple
`SortedLinkedList::getAllValues()` L-3 — flagged for the same reason,
including RPC provider timeouts as a secondary practical failure mode
even before the true gas limit is hit.
**Fix.** Add pagination (`from`/`to` or `cursor`/`limit` parameters) to
any function whose loop bound grows with protocol age or usage.

## DOS-05 — Batch settlement/finalize function has no batch-size limit
**Root cause.** A "finalize the epoch" / "distribute rewards" function
processes an unbounded set of pending items in one transaction, so once
enough items accumulate, the function can never successfully execute
again — a self-inflicted permanent DoS of a core protocol function, not
just a griefing vector.
**Precedents.** `Voter::finalize()` H-3 (BMX Deli Swap, Critical) —
processes pending removals without a batch-size argument; explicitly
flagged as needing batching to allow finalizing epochs without running out
of gas, since epoch finalization is on the critical path for reward
distribution.
**Detection.** Any "finalize"/"distribute"/"settle" function whose
iteration count is a function of *how much activity happened since last
call* rather than a caller-supplied bound — verify a batch-size parameter
and re-entrant "call again to continue" design exists.

## Cross-references
`AMM-04` (predictable address griefing) and `LIQ-04` (liquidation-timeout
griefing) are DoS/griefing patterns specific enough to warrant their own
files, but belong to this same family conceptually.
