# Mechanical Discovery Checks — Grep Patterns & On-Chain Verification

**Where this sits:** feeds `smart-contract-auditing` step 4 ("Generate hypotheses
independently" — the workflow already names "grep seeds" as a legitimate input
alongside static analysis and fuzzing, but never wrote any down). Each block below
is tagged with the exact pass or route it belongs to, so it can be dropped in as
supporting material rather than a new step.

**Discipline reminder from the auditing skill, still applies here:** a grep hit is
a hypothesis, not a finding. "A scanner warning is not reachability." Every match
below still goes through auditing's step 5 (verify reachability/preconditions)
and step 7 (try to kill the finding) before it counts as anything.

---

## → Pass 1: Authorization and lifecycle

**Sibling function family — missing modifier:**
```bash
grep -rn "function vote\|function poke\|function reset\|function update\|function claim\|function harvest" contracts/ -A2
```

**Existence check vs. ownership check:**
```bash
grep -rn "_requireOwned\|ownerOf\|_isApprovedOrOwner\|_checkAuthorized" contracts/ -B5
```

**Silent modifiers (if vs. require):**
```bash
grep -rn "modifier\b" contracts/ -A8 | grep -B3 "if (" | grep -v "require\|revert"
```

**Uninitialized initializer:**
```bash
grep -rn "function initialize\b" contracts/ -A3
grep -rn "_disableInitializers()" contracts/
```

---

## → Pass 2: Accounting, coupled state, and path symmetry

**Accounting variables that must stay in sync:**
```bash
grep -rn "totalSupply\|totalShares\|totalAssets\|totalDebt\|cumulativeReward\|rewardPerShare" contracts/
```

**Early returns in claim/redeem that skip state updates:**
```bash
grep -rn "\breturn\b" contracts/ -B3 | grep -B3 "if\b"
# For each early return: which state updates in the normal path get skipped?
```

**Variables that should update together but might not:**
```bash
grep -rn "totalSupply\|totalDebt" contracts/ -l | xargs grep -l "cumulative\|earmarked\|weight"
```

**Function family comparison (incomplete code path):**
```bash
grep -rn "function place_\|function create_\|function add_\|function open_" contracts/ -A5
grep -rn "function update_\|function modify_\|function cancel_" contracts/ -A5
# For each create/place/add: does the matching update/cancel refund/reverse it?

grep -rn "safeApprove\b" contracts/                 # approve without zero-reset first
grep -rn "\bdelete\b" contracts/ -B5 -A5             # delete before operation completes
grep -rn "function deposit\|function mint\|function withdraw\|function redeem" contracts/ -A10
# do all four have matching validation?
```

---

## → Pass 3: Math, units, precision, and boundaries

**Boundary comparisons (off-by-one):**
```bash
grep -rn "Period\|Epoch\|Round\|Deadline\|period\|epoch\|deadline" contracts/ -A3 | grep "[<>][^=]"
grep -rn "\bbreak\b" contracts/ -B10                                     # loop breaks
grep -rn "\.length\s*-\s*1\|i\s*<=\s*.*\.length\b" contracts/            # array boundary
grep -rn "block\.timestamp" contracts/ -A3 | grep "[<>][^=]"             # timestamp boundary
```
For every `if (A > B)` found: what happens when `A == B`? Is that correct?

---

## → Pass 4: External calls, token behavior, and reentrancy

**External calls before state updates:**
```bash
grep -rn "\.call{value\|safeTransfer\|\.transfer(" contracts/ -B10 | grep -v "require\|revert"
grep -rn "function withdraw\|function redeem\|function claim" contracts/ -A2 | grep -v "nonReentrant"
grep -rn "nonReentrant\|ReentrancyGuard\|_notEntered" contracts/          # guard present?
grep -rn "tokensReceived\|tokensToSend\|onERC1155Received\|onERC721Received" contracts/  # hook surfaces
```

**Transient storage (EIP-1153) — new reentrancy class:**
```bash
grep -rn "tstore\|tload\|TSTORE\|TLOAD" contracts/
# For each: audit for reads-after-external-calls using a stale transient value.
```

---

## → Pass 5: Oracle and economic manipulation

```bash
grep -rn "latestRoundData" contracts/ -A5 | grep -v "updatedAt\|timestamp"     # missing staleness check
grep -rn "getPriceUnsafe\|getPrice\b" contracts/ -A8 | grep -v "conf\|confidence"  # Pyth confidence ignored
grep -rn "secondsAgo\|TWAP\|cardinality" contracts/ -A5                        # short TWAP window
grep -rn "getReserves\|getAmountsOut\|slot0\b" contracts/ -A5                  # spot price, flash-loan manipulatable
```

**LST/LRT depeg assumptions:**
```bash
grep -rn "stETH\|rETH\|wstETH\|cbETH\|sfrxETH" contracts/ -A10
grep -rn "exchangeRate\|getStETHByWstETH\|pricePerShare" contracts/ -A5
# Check: does any protocol use the LST at 1:1 without a depeg guard?
```

---

## → Pass 6: AMM, migration, MEV, and shared-state seams

```bash
grep -rn "getReserves\|getAmountsOut\|slot0\b" contracts/ -A5     # flash-loan-manipulatable spot prices
grep -rn "oracle\|Oracle\|priceFeed\|getPrice" contracts/ -A5     # oracle source
grep -rn "secondsAgos\|twapPeriod\|observationCardinality" contracts/ -A5
grep -rn "virtualReserve\|setCurve\|graduate\|bonding_curve" contracts/ --include="*.sol" --include="*.rs"
# Kill if curve params immutable and graduation is permissionless.
# pump.fun-specific: mintAuthority retained beyond bonding-curve completion = exit-scam shape.
```

---

## → Pass 7: Vaults, lending, staking, and token supply

**ERC4626 / first-depositor:**
```bash
grep -rn "function transfer\|function transferFrom" contracts/ -A15
# Check: do they also transfer associated lock/stake records?
grep -rn "function deposit\|function mint\|function withdraw\|function redeem" contracts/ -A10
grep -rn "_decimalsOffset\|virtualAssets\|virtualShares" contracts/
# Missing = vulnerable to first-depositor attack.
```

**Hidden mint / unlimited supply:**
```bash
# EVM
grep -rn "function mint\|_mint(\|_balances\[.*\] +=" src/ --include="*.sol" | grep -v "test\|lib\|node_modules"
grep -rn "MAX_SUPPLY\|maxSupply" src/ --include="*.sol"
# Kill if MAX_SUPPLY enforced on every mint path, or mint function removed entirely.

# Solana
grep -rn "MintTo\|mint_to\|mint_authority" src/ --include="*.rs" | grep -v "test\|target"
# Kill if mint_authority = None (verify on-chain, see Solana section below).
```

---

## → Pass 8: Signatures, governance, and account abstraction

**Signature replay:**
```bash
grep -rn "ecrecover\|ECDSA\.recover" contracts/ -B20
grep -rn "nonce\|_nonces\|nonces\[" contracts/
grep -rn "block\.chainid\|chainId\|CHAIN_ID" contracts/
grep -rn "DOMAIN_SEPARATOR\|_buildDomainSeparator\|domainSeparator" contracts/ -A10
```
Check: does the signed hash include nonce + chainId + contract address, all three?

**EIP-7702 delegation:**
```bash
grep -rn "setCode\|DELEGATION_MAGIC\|TYPE_3\|0x04" contracts/
# Is delegation authority properly scoped and revocable?
```

**ERC-4337 paymaster abuse:**
```bash
grep -rn "paymaster\|IPaymaster\|validatePaymasterUserOp" contracts/ -A10
grep -rn "EntryPoint\|IEntryPoint" contracts/ -A5
# Does validatePaymasterUserOp have strict sender validation?
```

---

## → Pass 9: Proxy, clone, and upgrade safety

```bash
grep -rn "function initialize\b\|_disableInitializers\|initializer" contracts/
grep -rn "delegatecall\b" contracts/ -B3 -A5
grep -rn "0x360894\|EIP1967\|_IMPLEMENTATION_SLOT" contracts/       # canonical proxy storage slot
grep -rn "upgradeTo\|upgradeToAndCall\|_authorizeUpgrade" contracts/ -A5   # who can call?
```

---

## → Pass 10: Cross-chain and asynchronous flows

**Message entry points and endpoint authentication:**
```bash
rg -n "lzReceive|ccipReceive|receiveMessage|processMessage|executeMessage|onMessage" contracts src
rg -n "msg\.sender|endpoint|router|messenger|mailbox|bridge" contracts src
```

For every entry point, trace the authenticated endpoint, origin chain/domain,
origin sender, destination, message type, nonce, replay state, and zero/default
semantics. A trusted endpoint check alone is insufficient when the payload's
reported origin sender is caller-controlled.

**Replay, ordering, retry, and mirrored accounting:**
```bash
rg -n "nonce|processed|consumed|messageId|guid|replay|retry|refund|finalize|cancel" contracts src
rg -n "chainId|srcChain|dstChain|domain|origin|sender|receiver" contracts src
rg -n "pending|outbound|inbound|bridged|locked|minted|burned|released" contracts src
```

Compare request/finalize/cancel siblings and identify the single source of truth
for mirrored balance, debt, supply, and pending state. Test duplicate, delayed,
reordered, conflicting, dropped, and partially executed messages.

## → Pass 11: Denial of service and liveness

**Permissionless growth followed by iteration:**
```bash
rg -n "for\s*\(|while\s*\(|\.length|push\(|enqueue|queue|pending|requests" contracts src
rg -n "function .*external|function .*public" contracts src
```

Cross-reference public writers of dynamic collections with loops over those
collections. Check caps, pagination, bounded batches, pull-based claims, deletion,
and whether one malicious entry can revert the whole loop.

**External failure and gas griefing:**
```bash
rg -n "\.call\{|safeTransfer|transferFrom|send\(|try\s+|catch|gasleft|call\{gas" contracts src
rg -n "timeout|deadline|cancel|retry|rescue|recover|emergency|pause|unpause|shutdown" contracts src
```

Inspect external calls inside loops, push payments, revert-on-receive behavior,
caller-chosen gas limits, unavailable oracle/keeper/relayer dependencies, and
whether adverse states retain a timeout, cancellation, rescue, fallback, or
shutdown path. Quantify whether impact is temporary, economically repeatable, or
permanent.

---

## → Pass 12 / protocol-routes.md "Token, launch token, and authority review"

**Fee manipulation:**
```bash
grep -rn "setFee\|setSellFee\|_taxFee\|_sellFee" src/ --include="*.sol"
grep -rn "function set.*Fee" -A5 src/ --include="*.sol" | grep -v "require\|MAX\|<="
# Kill if fee setter has require(fee <= MAX_FEE) with MAX_FEE <= 10%.
```

**LP drain:**
```bash
grep -rn "migrateLP\|emergencyWithdraw\|\.sync()\|setPair\|setRouter" src/ --include="*.sol"
# Kill if LP tokens burned to dead address, no migration function, no pair setter.
```

**LP lock verification (never trust a badge — verify on-chain):**
1. Unlock date — the actual on-chain timestamp, not badge text.
2. Lock owner — is it the deployer? Multiple lockers fragmenting the position?
3. Extension/shortening permission — some lock contracts let the owner shorten the lock.
4. Lock contract bytecode — verify it's the canonical locker, not a fork with a backdoor.

**Fake renounce / hidden ownership:**
```bash
grep -rn "renounceOwnership.*override\|_shadowAdmin\|_backupOwner\|selfdestruct" src/ --include="*.sol"
# Kill if renounceOwnership NOT overridden, no second admin role, no selfdestruct.
# Verify: call owner() on-chain — should return 0x000...dead or 0x0.
```

**Sandwich amplification by design:**
```bash
grep -rn "swapExactTokensForETH" -A5 src/ --include="*.sol" | grep "0,"   # 0 = zero slippage protection
grep -rn "swapThreshold\|_rebase\|mandatoryPool" src/ --include="*.sol"
```

**Honeypot / transfer restriction:**
```bash
# EVM
grep -rn "blacklist\|isBlacklisted\|_bots\|maxTxAmount\|approve.*override\|tradingEnabled" src/ --include="*.sol"
# Solana
grep -rn "freeze_authority\|transfer_hook\|TransferHook\|permanent_delegate" src/ --include="*.rs"
```

**Honeypot behavioral test protocol** (run against live/testnet state):

| Test | Honeypot signal |
|---|---|
| Buy from random wallet | Succeeds (must — or no one touches it) |
| Transfer to second random wallet | Often FAILS on honeypot |
| Sell from original wallet | FAILS or applies > 50% tax |
| Sell from team-controlled wallet | Succeeds (the giveaway) |

---

## → non-evm-and-consensus.md "Solana token screening"

**Authority retention — source check:**
```bash
grep -rn "mint_authority\|freeze_authority\|update_authority\|close_authority" src/ --include="*.rs"
grep -rn "set_authority.*None" src/ --include="*.rs"   # good: revocation present
```

**Authority retention — on-chain check (no source needed):**
```bash
solana account <MINT> --output json | python3 -c "
import json,sys
d=json.load(sys.stdin)
data=d.get('account',{}).get('data',{})
print('mint_authority:', data.get('parsed',{}).get('info',{}).get('mintAuthority'))
print('freeze_authority:', data.get('parsed',{}).get('info',{}).get('freezeAuthority'))
"
# Both should be null for a legitimate token.
```

**Token-2022 extension danger check:**
```bash
spl-token display <MINT_ADDRESS> --program-id TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb
# Critical signals:
# TransferHook { authority: Some(pubkey) } → that key can pause/blacklist/fee-on-transfer any holder
# PermanentDelegate { delegate: Some(pubkey) } → that delegate can move any holder's tokens
```

**Solana 6-point fast filter (no source code required, under 5 minutes):**
```bash
MINT="<TOKEN_MINT_ADDRESS>"

# 1. Mint authority — should be "(not set)"
spl-token display $MINT | grep -i "mint authority"

# 2. Freeze authority — should be "(not set)"
spl-token display $MINT | grep -i "freeze authority"

# 3. Update authority (metadata mutability) — should be null/burn address
metaboss decode mint -a $MINT | python3 -c "import json,sys; d=json.load(sys.stdin); print('update_authority:', d.get('update_authority','unknown'))"

# 4. LP status — check Raydium/Orca: burned to 1111...1111? locked with no backdoor?
#    held by deployer = CRITICAL, instant-rug shape.

# 5. Top holders — Birdeye/Solscan holders tab, top 10 < 30% excluding pools/burn.

# 6. Token-2022 extensions
spl-token display $MINT --program-id TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb
# Look for: TransferHook, PermanentDelegate, MintCloseAuthority
```
