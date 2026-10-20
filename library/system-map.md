# How Juku OS fits together

Scope: the whole system. Open when: explaining how Juku OS fits together, or finding which part owns what.

One picture of where things live and which check guards them. Each box's own file is the rule.

```mermaid
flowchart TB
  CH(["Chairman<br/>money · permissions · product truth · looks by picture"])
  subgraph READ["Read first, every session (word budget)"]
    HWB["HOW-WE-BUILD.md<br/>who decides · which rule wins · the loop"]
    RD["README.md<br/>map of products · library index"]
  end
  LIB["library/<br/>one page per topic, opened on its trigger<br/>HyperSolid owns every look"]
  subgraph PROD["Each product repo (private)"]
    AG["AGENTS.md<br/>rules true only here"]
    CON["design/CONSTITUTION.md<br/>tokens · units · money · domain law · dated picture approvals"]
    PD["PRODUCT.md + roadmap.json<br/>what it does, what comes next"]
  end
  ARC["Archive: juku-library/ · decision issues · product libraries<br/>never read unless asked why"]
  MEM["Memory<br/>who he is, how he likes to be spoken to — never rules"]
  subgraph CHECKS["Every change, before it merges"]
    RC["rules-check.py — free<br/>word budgets · Replaces: line · constitution shape"]
    CK["check.sh — free<br/>files, links, secrets, gate"]
    RV["Cold reviewer — one existing read<br/>judges the diff · sits the exam in its brief"]
  end
  CH -- "rules · approves by looking" --> PD
  HWB --> RD --> LIB
  RD -- "maps" --> AG
  AG --> CON
  CON -. "values only" .-> LIB
  RC --> CK --> RV
  RV -- "green: merge" --> READ
  RV -- "green: merge" --> PROD
  READ -. "why" .-> ARC
```

**Which rule wins** is written once, in `HOW-WE-BUILD.md`. **Who owns which truth**: how we build, this repository; what a product is and does, its own repository; which model does a job, `model-registry/registry.json`; why a rule is what it is, the archive. A Project holds instructions, never a copy of any of these.
