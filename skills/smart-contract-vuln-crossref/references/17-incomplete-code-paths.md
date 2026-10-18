# 17 — Incomplete code paths

A contract has a family of related functions — a "create" and its
"cancel," a "deposit" and its "withdraw," a "place_order" and its
"update_order," an ERC4626 `deposit()` and its `mint()`. One member of
the family does something (takes a transfer, applies a check, records
state); a sibling that logically should mirror or reverse it doesn't.

## INC-01 — The function-family comparison test (methodology)
This is a checklist, not a single bug — apply it to every related pair
or family of functions in scope:
1. List every state change and every token transfer function A performs
   (a "create"/"deposit"/"place"/"open" style function).
2. List every state change and every token transfer its sibling function
   B performs (a "cancel"/"withdraw"/"update"/"close" style function).
3. For every state change in A, does B have the corresponding reverse?
4. For every token transfer *into* the contract in A, does B have the
   corresponding refund/transfer *out* where the economics call for one?
5. For every validation/check present in A, is the equivalent check
   present in every other entry point that reaches the same end state
   (e.g. both `deposit()` and `mint()` in an ERC4626 vault)?
6. Any "A does X, B doesn't do the reverse, and there's no other code
   path that does it either" is a real finding, not a style nit.

## INC-02 — Update/cancel function missing the refund its paired create/deposit function implies
```solidity
function place_order(OrderInput calldata order) external {
    token.safeTransferFrom(msg.sender, address(this), order.price);  // takes tokens
    orders[orderId] = order;
}
function update_order(OrderInput calldata updatedOrder) external {
    // no refund when price decreases — the difference is permanently stuck
    orders[orderId] = updatedOrder;
}
```
**Precedent.** ThunderNFT — `update_order()` changed the stored price but
never refunded the excess when the price decreased, permanently
stranding the difference with no recovery path. High severity. The
report explicitly credits the function-family comparison test (`INC-01`)
with making this "immediately" findable — this is presented as a
detection methodology worth running as a matter of course, not a bug
that required unusual insight to spot.
**Detection.** Any order-book/listing/escrow-style contract: find every
function that takes a payment on creation, then check every function
that can change the recorded price/amount afterward for a matching
refund path.

## INC-03 — An alternate entry point bypasses validation the primary entry point performs
```solidity
function deposit(uint256 assets, address receiver) public override {
    shares = _deposit(assets, receiver);   // includes receipt validation
}
function mint(uint256 shares, address receiver) public override {
    assets = convertToAssets(shares);
    _mint(receiver, shares);               // missing: the same validation _deposit() has
}
```
**Precedent.** An ERC4626-style vault where `mint()` (the shares-first
entry point) didn't route through the same validation as `deposit()` (the
assets-first entry point), allowing shares to be minted without the
receipt-side checks the "main" path enforced.
**Detection.** For any interface with more than one entry point to the
same underlying operation (ERC4626's `deposit`/`mint` pair and
`withdraw`/`redeem` pair are the canonical example), confirm both entry
points route through the *same* internal validation function rather than
each reimplementing their own subset of it.

## Cross-references
This file's methodology (`INC-01`) is the general form of `ACC-03`'s
"read every sibling function" advice from file 05 — `ACC-03` is scoped to
*authorization* checks specifically; this file's scope is broader
(any state change or transfer, not just access control). Also see
`VLT-02`/`VLT-03` for the ERC4626-specific instances of `INC-03`.
