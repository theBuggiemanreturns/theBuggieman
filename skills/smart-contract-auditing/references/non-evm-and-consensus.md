# Non-EVM and consensus routing

Read only for applicable scope. The bundled `contract-info` tool and Solidity gap
finder do not cover these targets; use the protocol-map schema manually and attach
platform-native build, graph, deployment, and state evidence.

## Solana and Anchor programs

- Verify every account's owner/program, signer, writable status, type/discriminator,
  seeds, canonical bump, address relationship, initialization state, and close
  destination.
- Reject arbitrary CPI/program IDs and unchecked remaining accounts. Check duplicate
  mutable accounts, confused-deputy authority, PDA signer seeds, sysvar authenticity,
  account reinitialization, revival after close, and rent/lamport accounting.
- Test integer/decimal math, token/mint ownership, delegate/close/freeze/mint/update
  authorities, Token versus Token-2022 program IDs, transfer fees/hooks,
  PermanentDelegate, confidential/default-account-state extensions, and extension
  combinations.
- Check upgrade authority, IDL/deployment identity, instruction sibling symmetry,
  transaction atomicity/order, compute limits, realloc growth, and account-lock DoS.
- Use program-test/Bankrun/Anchor tests with adversarial accounts; token authority
  screening alone is not a Solana program audit.

## Solana token screening

Verify on-chain mint, freeze, update, close, transfer-hook, and permanent-delegate
authorities; Token-2022 extensions; supply/mint paths; LP custody/lock terms; holder
concentration; bonding-curve graduation; and post-graduation authority revocation.
This is a risk screen, not proof of safety or a substitute for program review.

## Rust consensus and validator clients

Pin the bounty/engagement scope and exact live commit. Known issues and moving-master
drift are first-class duplicate/eligibility checks.

Review distinct properties:

1. safety: conflicting finalization or certificate acceptance below honest threshold;
2. liveness: permanent/unrecoverable stalls, timeout/parent-ready deadlocks, and one
   participant blocking progress;
3. stake deduplication across signer, certificate, round, epoch, and split-vote sets;
4. BLS proof-of-possession, signer-set binding, message/domain separation, and
   aggregation API use;
5. exact threshold operators and widened/checked fraction arithmetic;
6. equivocation prevention and persist-before-broadcast across restart;
7. consensus migration/handover state;
8. dissemination/repair response validation, sibling message-arm asymmetry,
   length/index bounds, and Merkle leaf/node domain separation;
9. reward/credit accounting and window boundaries.

Model the documented Byzantine fault bound. A test that bypasses the real fault
model is not a finding. Drive the real state machine with adversarial schedules
where feasible and assert safety invariants. State limitations where wall-clock,
multi-node behavior, unavailable crates, or feature-gated tests prevent proof.

Maintain an explicit coverage matrix for every in-scope crate/subsystem.
