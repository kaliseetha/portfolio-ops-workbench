# OpsDesk Exception Workbench

## Business overview

OpsDesk is a proof of concept (POC) for helping investment-operations teams review portfolio reconciliation exceptions. A reconciliation exception is a difference, missing value, or data-quality issue found when comparing records from two systems—for example, a portfolio ledger and a custodian feed.

Today this POC uses **fictional, synthetic data only**. It has no client branding, production integrations, live AI calls, or connection to financial accounts. Its purpose is to demonstrate and evaluate a possible workflow, not to perform production reconciliation.

The central idea is to bring the exception, the records that triggered it, and a suggested review checklist into one workbench. Rules determine which records are flagged. An AI assistant may help explain the displayed evidence, but a human reviewer remains responsible for the decision.

## Business problem and opportunity

Operations teams may need to identify and investigate differences across records before they can decide what to do next. When the relevant information and review history are difficult to bring together, staff may spend time assembling context, prioritizing work, and documenting decisions.

This POC explores whether a focused review experience can help teams:

- Find higher-priority exceptions sooner.
- Understand what differs without manually comparing records across screens.
- Follow a consistent investigation checklist.
- Capture reviewer decisions and rationale in a visible activity history.
- Evaluate whether AI-generated summaries are useful, evidence-based, and safe to use as drafts.

These are **potential benefits to test**, not measured or guaranteed business results.

## Intended users

- **Operations reviewer:** works through the exception queue, examines evidence, and records a disposition.
- **Operations lead:** monitors open work, priority, investigation status, and outcomes.
- **Risk, compliance, or technology stakeholder:** evaluates permissions, auditability, data handling, and whether the POC is suitable for a controlled pilot.

The current prototype represents a single demo reviewer. It does not implement real user accounts, roles, or enterprise access management.

## POC workflow

1. **Review the queue.** Search and filter fictional exceptions by category or status.
2. **Select an exception.** Review the account label, household label, category, priority, age, and configured rule.
3. **Compare evidence.** Inspect the synthetic portfolio-ledger and custodian-feed records, including quantities, values, dates, and source labels.
4. **Request a draft explanation.** The current version displays a prewritten sample explanation and review checklist. It is explicitly labeled as demo-generated and is **not connected to an AI model**.
5. **Record a human decision.** Mark an item as investigating, resolved, or dismissed. In this prototype, the status, activity entries, and dashboard counts update in browser memory and reset on page reload.
6. **Export the visible queue.** Download the currently filtered synthetic records as a CSV file.

## POC architecture

### Current implementation

```text
Reviewer
   |
   v
React + TypeScript single-page application
   |-- Synthetic exception examples in the frontend
   |-- Deterministic display and filter behavior
   |-- Sample explanations (no model call)
   |-- Review state and activity in browser memory
   `-- CSV export generated in the browser
   |
   v
Render Static Site (planned deployment target)
```

The current prototype is deliberately frontend-only. It does **not** yet contain a Python API, database, authentication, persistent audit records, or OpenRouter integration.

### Target architecture for a later POC increment

```text
Reviewer browser
   |
   v
React + TypeScript frontend
   |
   | HTTPS API requests; no model or database credentials in the browser
   v
Python + FastAPI service
   |-- Authentication and authorization checks
   |-- Deterministic comparison and prioritization rules
   |-- Structured, evidence-limited AI request
   |-- Response validation and error handling
   `-- Audit-event creation
       |                         |
       v                         v
PostgreSQL database          OpenRouter API
Synthetic cases,             Draft evidence summaries
review events, and           and checklists only
audit history
```

The target design is a future direction, **not functionality currently present**. The approved integration and data route must be confirmed before adding any real external records. Until that work is explicitly approved, use synthetic data only.

## Technology choices and responsibilities

| Technology | Role in the current or target POC | Why it fits |
|---|---|---|
| **React** | Current frontend for the queue, evidence comparison, draft explanation, and review controls. | Supports a responsive, interactive workbench that business reviewers can evaluate early. |
| **TypeScript** | Current frontend language. | Adds compile-time checks for exception fields, status values, and UI interactions. |
| **Vite** | Current development server and frontend build tool. | Provides a quick local workflow and produces static files suitable for Render Static Sites. |
| **Python + FastAPI** | Proposed backend; not implemented yet. Would own API validation, access checks, deterministic rules, AI orchestration, and audit writes. | Python is a practical fit for data processing and model integrations; FastAPI provides typed HTTP endpoints and generated API documentation. |
| **PostgreSQL** | Proposed persistent database; not implemented yet. Would store synthetic source records, exception state, reviewer decisions, and audit events. | A relational database supports structured financial-operation records and traceable review history. A managed free-tier database may pause or have limited storage and must not be treated as a production service. |
| **OpenRouter** | Proposed model gateway; not connected yet. The backend would call it for draft summaries and checklists. | Provides a single API interface to multiple models. Model selection, availability, data handling, rate limits, and provider terms should be reviewed before use. |
| **Render Static Site** | Intended free hosting target for the current frontend. | Serves the built React application as static files with a generated public URL and HTTPS. No backend secrets are needed for this frontend-only stage. |
| **GitHub** | Source repository and deployment trigger when connected to Render. | Supports version history and repeatable deployments from the selected branch. |

### Future request and data flow

1. The browser requests an exception and its authorized source evidence from the FastAPI service.
2. The API applies deterministic comparison and prioritization rules; the model does not calculate balances or decide exception priority.
3. When requested, the API sends only the selected, necessary synthetic evidence to OpenRouter.
4. The API validates the returned structure and evidence references. If the model is unavailable or the evidence is insufficient, the UI should show that clearly rather than invent an explanation or silently substitute a success response.
5. The reviewer edits or records a disposition. The API persists the reviewer action and relevant audit event.

The OpenRouter API key must be held by the backend as a secret. It must never be compiled into the React application or sent to the browser.

## Exception examples in the demo

The seed examples illustrate categories such as:

- **Position mismatch:** quantities or values differ, or a position appears in only one record.
- **Cash variance:** cash amounts differ beyond a configured review threshold.
- **Unmatched security:** a required identifier cannot be matched in the demo reference data.
- **Stale record:** the source records have different or outdated as-of dates.

All examples and thresholds are for demonstration. They do not represent a real firm's procedures, approved tolerances, security master, accounting policy, or recommended investment action.

## Business benefits and how to test them

| Potential benefit | POC evidence to collect |
|---|---|
| Less time spent assembling evidence | Compare median review time with and without the workbench on the same representative synthetic cases. |
| More consistent initial triage | Measure reviewer agreement with the rules-based category and priority; record disagreements and overrides. |
| Clearer, more repeatable investigation | Ask reviewers whether the proposed checklist is understandable and useful; capture what they edit or reject. |
| Better traceability | Verify that each displayed comparison identifies its source and that every decision creates an attributable audit event in the future backend increment. |
| Safer AI use | Test missing, conflicting, and ambiguous evidence. Confirm that the assistant identifies uncertainty and does not assert a cause unsupported by records. |

Set acceptance thresholds with business stakeholders **before** running an evaluation. Candidate targets for discussion—not current results—might include a meaningful reduction in median triage time, high reviewer agreement on clear-cut cases, and complete source references for generated claims. Report accuracy, unsupported statements, override rate, and latency alongside time savings.

## Safety, governance, and limitations

- **Human decision-making:** AI output is a draft. Reviewers decide whether to investigate, resolve, or dismiss an exception.
- **No autonomous financial actions:** The POC must not trade, change accounts or records, close a reconciliation automatically, or send client communications.
- **Evidence-grounded AI:** Provide the model only the selected records needed for a draft; display source references and uncertainty. Do not rely on a model for financial calculations or rule-based prioritization.
- **Synthetic data only:** Do not enter real names, account numbers, holdings, statements, credentials, or other confidential information into this public demo or an AI prompt.
- **No production security claim:** The current app has no login, server-side authorization, durable audit storage, or production monitoring. A public Render URL is not a private or regulated deployment.
- **Free-tier constraints:** Free hosting and model quotas may include cold starts, inactivity pauses, rate limits, limited storage, or changing availability. These are suitable only for a non-critical demonstration, not a service-level commitment.
- **No assumed integration:** The prototype does not establish that a particular portfolio, CRM, custodian, or reconciliation API is available. Confirm an authorized data source before planning a connected pilot.
- **No business outcome claims:** Benefits and target measures are hypotheses until tested with representative users and agreed evaluation data.

## Suggested delivery phases

### Phase 1 — Frontend demo (current)

- Deploy the React application as a Render Static Site.
- Walk through the synthetic queue, evidence, sample explanation, human review actions, and CSV export.
- Gather feedback on terminology, exception categories, priority presentation, and review steps.

### Phase 2 — API and persistence

- Add a Python/FastAPI service and PostgreSQL storage for synthetic cases and review events.
- Move demo records and deterministic rules behind the API.
- Add server-side validation, basic authentication/authorization appropriate to the demo, and durable audit events.
- Keep the demo usable when AI is unavailable.

### Phase 3 — OpenRouter draft assistance

- Store the OpenRouter key only in backend secrets.
- Choose and pin an available model after reviewing provider terms, data handling, limits, and cost.
- Send minimal synthetic evidence and request a structured explanation, evidence references, and checklist.
- Validate output, set token/request limits, handle rate limits and provider errors visibly, and test ambiguous cases.

### Phase 4 — Evaluation and go/no-go

- Compare the assisted workflow against a manual baseline on a curated holdout set.
- Review time, reviewer agreement, evidence support, overrides, errors, and model latency.
- Decide whether the demonstrated value justifies a separately scoped, approved pilot.
- Do not move to real data without explicit data-owner approval, an authorized integration route, security/privacy review, and appropriate operational controls.

## Current status and known limitations

- 10 fictional exception examples are embedded in the frontend.
- Exception state and activity are held in browser memory and reset after refresh.
- Explanation text and checklists are static examples, not model output.
- Queue CSV export is generated locally from the visible filtered rows.
- There is no backend, database, login, external integration, or live AI.
- The rendered demo is a workflow prototype, not an operational reconciliation system.

## Run locally

Requirements: Node.js 20 or later.

```sh
npm install
npm run dev
```

The production build can be checked locally with:

```sh
npm run build
npm run preview
```

## Deploy the frontend to Render

1. Push this project to a GitHub repository.
2. In Render, create a **Static Site** and connect the repository.
3. Render can use the included `render.yaml` blueprint, or enter:
   - Build command: `npm install && npm run build`
   - Publish directory: `dist`
4. Deploy and open the generated `onrender.com` URL.

The included rewrite serves the React application for browser routes. This frontend-only deployment needs no environment variables, API server, database, or OpenRouter key.

## Glossary

- **Reconciliation:** comparing records from separate systems to identify differences.
- **Exception:** a discrepancy, missing value, unmatched record, or data-freshness issue that needs review.
- **Custodian feed:** a data file or approved data connection containing custody-side account or position records.
- **Portfolio ledger:** the portfolio-side records being compared in this demo.
- **Synthetic data:** artificial data created for demonstration and testing, not copied from real people or accounts.
- **Evidence reference:** an indication of which displayed record or field supports a generated statement.
- **Human-in-the-loop:** a workflow where a person reviews and owns the final decision rather than allowing AI to make it automatically.
