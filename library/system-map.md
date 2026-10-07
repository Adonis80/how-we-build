# How Juku OS fits together

Scope: the whole system. Open when: explaining how Juku OS fits together, or finding which part owns what.

One picture of every part and who owns which truth. It says where things live, never what they say: each box's own file is the rule.

```mermaid
flowchart TB
  CH(["Chairman<br/>money · permissions · product truth · looks · irreversible"])
  PJ["Projects<br/>instructions only, no files"]
  CO["Consultant (other stack)<br/>reads live, writes nothing"]
  subgraph RB["Rulebook · how-we-build · public"]
    direction TB
    HWB["HOW-WE-BUILD.md<br/>the loop, read first"]
    RD["README.md<br/>map · carries list · library index"]
    LIB["library/<br/>one page per topic, on its trigger"]
    REG["model-registry/<br/>the only place a model is named"]
    JL["juku-library/ + decision issues<br/>why each rule is what it is"]
  end
  subgraph PR["Each product repo · private"]
    direction TB
    AG["AGENTS.md<br/>rules true only here"]
    PD["PRODUCT.md + roadmap.json<br/>what we build, what comes next"]
    PL["product library<br/>its own papers"]
  end
  PP["juku-os-papers · private<br/>papers of an idea not yet a product"]
  RV["Independent reviewer"]
  GT["check.sh + gate"]
  BD["Build board"]
  CH -- "rules, approves by looking" --> PJ
  PJ -- "debates big ideas" --> CO
  PJ -- "starts a session that reads" --> HWB
  HWB -- "governs" --> RD
  RD -- "opens on a trigger" --> LIB
  RD -- "maps" --> AG
  AG -- "first line: reads" --> HWB
  AG -- "governs" --> PD
  REG -- "names the model for" --> RV
  RV -- "signs a verdict on the current commit" --> GT
  GT -- "gates the merge of" --> PD
  GT -- "gates the merge of" --> RB
  BD -- "reads the plans in" --> PD
  BD -- "shows progress to" --> CH
  PP -. "moves into on joining" .-> PL
```

**Reading it.** A session starts in a Project, which sends it to `HOW-WE-BUILD.md`, then the README. The README's map sends it to one product repo; the library opens only on a trigger. Work leaves only as a pull request: the reviewer signs a verdict on the current commit and the gate consumes it. A consensus with the consultant never stands in for that verdict. The board reads each product's plan and shows it to the Chairman, who answers only what is his.

**Who owns which truth.** How we build: this repository. What a product is and does next: its own repository. Which model does a job: `model-registry/registry.json`. Why a rule is what it is: the decision issues and `juku-library/`. Papers for an idea not yet a product: `juku-os-papers`. A Project holds instructions, never a copy of any of these.
