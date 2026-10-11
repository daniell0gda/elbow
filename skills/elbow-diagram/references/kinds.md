# Kinds

Pick the kind from what the reader must understand. Groups mean something different in each kind; a kind
without groups ignores them. A trailing `(…)` in a label is the sublabel unless the kind reads it as data.

| `kind` | Use it for | Groups are | Label and edge conventions |
| --- | --- | --- | --- |
| `flow` | Components and their connections, data flow | zones around members | `Name (tech)` |
| `sequence` | Messages between actors over time | — | node order = lifeline order; edge order = message order; replies as `async` edges back to the caller |
| `state` | A lifecycle | zones | shape `state`; `transition` edges labelled with the trigger |
| `tree` | Hierarchies | — | parent → child edges |
| `er` | Entities and relationships | — | `Order (id uuid PK, total numeric)`; edge label `1:N` or `one-to-many` |
| `swimlane` | Steps by owner or team | lanes, `Name (detail)` | members in step order |
| `nested` | Boundaries inside boundaries (cloud, VPC, subnet) | rings; a group may hold another | — |
| `layers` | An architecture stack | bands, top layer first | — |
| `dependency` | What depends on what | — | edge from dependent to dependency; a cycle is drawn as the accent |
| `timeline` | Events and milestones | periods | `Name (2024 Q2)`; focal = milestone |
| `process` | A business process with handoffs | role lanes, `Role (BADGE)` | edge label = what is handed over |
| `loop` | A cycle or flywheel | — | stations in order; the first database, cache or queue is the hub |
| `pyramid`, `funnel` | Ranked levels, narrowing stages | — | top first, `Name (detail)` |
| `venn` | Overlapping sets | the 2–3 sets | items belong to the sets that list them |
| `fishbone` | Causes of one problem | — | effect node, categories, causes; `data` edges category → effect and cause → category; focal = root cause |
| `kanban` | Work by status | columns, `Name (WIP limit)` | `Title (ticket · owner)`; focal = blocked |
| `journey` | One person's experience | — | `Stage (feeling, touchpoint)`; `note` nodes are pain points |
| `story-map` | Activities and stories by release | release slices | activities in no group; edges activity → its stories |
| `uml-class` | Classes | zones | `interface Name (+ attr: T, + op(): R)` (or `abstract`); edge label starts with `implements`, `extends`, `uses`, … and may end in a multiplicity `1:0..*` |
| `deployment` | Where software runs | zones | `Name (POD, image v1, x3)` |
| `medallion` | Data tiers | — | `Tier (bucket; tool; format; writer)` |
| `org-chart` | Who owns what | zones | `Name (how to reach, scope)`; edges owner → report; focal = front door |
| `db-schema` | Tables and foreign keys | schemas | `schema.table (col type PK, col type FK)` |
| `quadrant` | Items on two criteria | quadrants in reading order | the title `A vs B` names the axes |
| `wardley` | A value chain by evolution | — | `Name (genesis/custom/product/commodity, detail)`; `dependency` edges from user-facing down; focal = evolving |

Every kind has an example view in [elbow's `tests/` folder](https://github.com/daniell0gda/elbow/tree/main/tests),
named after the kind, except `flow` (`backend.json`), `sequence` (`login.json`), `state` (`order.json`), `tree`
(`org.json`) and `swimlane` (`hiring.json`).
