# Chain Card — C-### : <title>

A chain is a first-class finding. Fill every field before it can reach CONFIRMED.

```
CHAIN:          C-###
LINKS:          P-00x + P-00y (+ ...)        # ids from primitives.md
END STATE:      the impossible state the chain reaches
WHY IT CHAINS:  precondition-unlock | guard-disable | shared-mechanism | representation-divergence | entitlement-payment-split
SEQUENCE:       shortest ordered valid-call sequence that reaches END STATE
WITNESS:        assertable storage/balance/claim at END STATE (not prose)
MONETIZATION:   who redeems/withdraws/settles the value; extract vs grief
EVIDENCE:       SOURCE | DEPLOYMENT | RUNTIME | ECONOMICALLY  (highest reached)
CLASS:          EXTRACT | GRIEF | PRIVILEGED   (+ scope.md rubric line if not EXTRACT)
SEVERITY:       scored on END STATE against the program rubric
KILL ATTEMPT:   what you tried to refute it with, and why it survived
POC:            path to the single fork harness that runs the whole sequence
REVISIT IF:     map-growth trigger that would reopen this if killed
```

Rules:
- Severity is the end state's impact, never the max of the links.
- CONFIRMED needs RUNTIME + ECONOMICALLY verified + a recorded kill attempt + a paid CLASS.
- One PoC must execute the entire sequence and assert the witness.
