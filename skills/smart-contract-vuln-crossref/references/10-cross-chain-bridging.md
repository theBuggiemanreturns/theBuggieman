# 10 — Cross-chain, bridging & message-passing

## XCH-01 — Chain-fork replay because `chainid` is baked into an id/hash
**Root cause.** An id or commitment includes `block.chainid` at creation
time; after a chain fork (both chains now share history but diverge), the
id computation on the new fork no longer matches, silently orphaning
existing state rather than being exploitable directly — a correctness/
liveness issue more than a fund-theft one, but worth flagging.
**Precedents.** `IdLib.toId()` L-1 (Morpho Midnight) — obligation ids
include `block.chainid`, so after a fork every existing obligation becomes
unreachable and any interaction silently creates a fresh obligation
instead of erroring loudly.
**Detection.** Grep for `block.chainid` inside any hash/id computation
that is expected to remain stable long-term.

## XCH-02 — Caller-supplied cross-chain message args can permanently lock the counterpart
**Root cause.** A function that relays a cross-chain result (e.g. "raffle
winner," "settlement outcome") accepts caller-supplied parameters that
feed directly into the message sent to the other chain; if those
parameters are wrong (whether by mistake or malice) the receiving side can
end up in a state with no recovery path.
**Precedents.** `WinnablesTicketManager::propagateRaffleWinner()` H-1
(Winnables Raffles, Critical) — incorrect CCIP inputs could permanently
lock prize assets on `WinnablesPrizeManager` with no way to recover them.
**Detection.** Any cross-chain message send whose payload is influenced by
caller input rather than derived entirely from validated on-chain state:
check what happens on the receiving side if that payload is wrong, and
whether *any* code path (even an owner-guarded one) can recover from it.

## XCH-03 — Non-atomic cross-chain updates overwrite or desync shared global state
**Root cause.** State that's meant to be a single logical value (a pool
total, a debt figure) is tracked per-chain and synchronized via
asynchronous messages; because cross-chain calls are never atomic with
local state changes, races between "local update" and "message from the
other chain" can overwrite or double/under-count the shared value.
**Precedents.** This is the dominant bug class in the Autonomint report
(Code4rena, 20+ Critical/High findings on one omnichain CDP/CDS system):
`omniChainData.cdsPoolValue` reinitialized and losing prior value on
certain deposit/withdraw sequences (H-27); `noOfLiquidations` sent as a
liquidation index and overwriting the *other* chain's index instead of a
shared counter (H-20); `totalAvailableLiquidationAmount` not updated on
withdraw while it is updated on deposit (H-28); and several more variants
of the same "two chains' views of one number drift apart" root cause.
Also: LayerZero global-state overwrite H-26 in the same report,
called out generically as "lack of a locking mechanism combined with
non-atomic cross-chain operations."
**Detection.** For any value that's supposed to represent one logical
total across two or more chains: enumerate every code path (on every
chain) that writes to the local copy, and check whether each one assumes
it has the authoritative/latest value or could be racing an in-flight
message. This is the single highest-density bug class found in the corpus
for cross-chain protocols — allocate real audit time here, it rarely has
just one instance once you start pulling the thread.

## XCH-04 — Cross-chain fee/gas assumed symmetric between chains
**Root cause.** Code computes a fee or gas cost using the *local* chain's
parameters and applies it uniformly, or double-charges by assuming a fee
applies on both legs of a transfer when it should apply once.
**Precedents.** `GlobalVariables::oftOrCollateralReceiveFromOtherChains()`
M-23/M-24 (Autonomint) — assumed the fee is the same on both chains
(false), and separately always charged ETH for a collateral-transfer case
that didn't need it.
**Detection.** Any fee computation feeding a cross-chain message: verify
it's parameterized per-destination-chain, not a single shared constant.

## XCH-05 — Smart-contract wallet address differs across chains
**Root cause.** A bridging function sends the bridged asset to
`msg.sender`'s address on the destination chain, assuming the same address
resolves to the same (or any) contract there. Some smart-contract wallets
have different addresses per chain, or the deployer's counterfactual
address generation differs.
**Precedents.** MetaZero Omnichain NFTs H-02 — `send()` delivers to the
same address that called on the source chain; smart-contract wallets with
per-chain address divergence can lose the bridged NFT entirely.
**Detection.** Any bridge/omnichain transfer that doesn't take an explicit
destination-chain recipient parameter, defaulting instead to "same address
as sender."

## XCH-06 — Missing minimum-gas / adapter-param validation blocks the message channel
**Root cause.** A LayerZero-style (or similar) message-sending wrapper
lets the caller under-specify gas/adapter parameters; if the resulting
message can never execute on the destination, it can permanently jam that
channel for everyone else queued behind it.
**Precedents.** Tapioca DAO H-17 (Code4rena, Critical) — incorrect
overriding of `lzSend` combined with no minimum-gas validation let an
attacker block the LayerZero channel for the whole protocol.
**Detection.** Any wrapper around a generic cross-chain messaging library:
check whether caller-supplied gas/adapter params are validated against a
sane floor before the message is dispatched.

## Cross-references
`ACC-05` (admin bypasses its own timelock) and `DOS-05` (unbounded batch
settlement) both recur inside cross-chain/omnichain protocols specifically
because of the added complexity — expect overlap.
