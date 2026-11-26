# Development Progress

## Implemented

- Project skeleton
- Scenario management
- SQLite database setup
- EVTX file copying and tracking
- EVTX parsing
- YAML rule definitions
- YAML rule matching
- JSON findings output
- JSON output validation by constructing an attack timeline with an LLM

## Planned

- Graphical user interface

## Deferred or Scrapped

- **DuckDB:** SQLite is simpler for this project and provides sufficient storage and querying support.
- **Database-level YAML normalization:** The extra complexity does not justify its use for the current scenarios. JSON compression remains a more direct approach to reducing token usage.
- **Sigma HQ integration:** Automatically retrieving and matching the complete Sigma rule repository is outside the current project scope.

Last updated: 26 November 2026

![mama mia](misc\images.jpg)

