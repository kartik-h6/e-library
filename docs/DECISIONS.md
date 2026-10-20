# Architecture decision log

Record decisions with date, context, options, choice, and consequences. Proposals remain open until reviewed.

## ADR-001 — Curriculum controlled by official sources
- **Status:** Accepted project rule
- **Decision:** Do not populate/publish curriculum structure until the current applicable official syllabus is obtained and checked.
- **Reason:** Legacy HTML can contain outdated or irrelevant assumptions.
- **Consequence:** Course routes and unit pages wait for source verification.

## ADR-002 — Static-first public reading experience
- **Status:** Proposed
- **Decision:** Begin with static pages and a versioned JSON catalogue.
- **Reason:** Reduces initial cost and operational complexity.
- **Consequence:** Shared edits, authenticated admin, and cross-device accounts remain out of scope until a trusted backend is selected.

## ADR-003 — No client-side admin authentication
- **Status:** Accepted security rule
- **Decision:** Do not rely on passwords/roles checked in public JavaScript.
- **Reason:** Client code and data are visible and modifiable by visitors.
- **Consequence:** Future admin workflows must be server-enforced or reviewed Git contributions.
