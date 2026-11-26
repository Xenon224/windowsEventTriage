# Windows Event Triage

Windows Event Triage is a Python tool for ingesting Windows Event Log (`.evtx`) files, normalizing their contents, and identifying potentially suspicious events.

The project combines related event logs into a SQLite database, matches events against a set of YAML rules, and exports the findings as JSON. The resulting JSON is intended to be small enough to send to an LLM for creating a chronological attack timeline.
 
See [PROGRESS.md](./misc/PROGRESS.md) for implemented features, planned work, and scrapped ideas.

## How It Works

1. EVTX files are collected into a scenario.
2. Event records are parsed and normalized.
3. Records are stored in a SQLite database for efficient querying.
4. Event data is matched against rules in `core/rules.yaml`.
5. Matches are exported to a scenario-specific `findings.json` file.
6. The JSON findings can be sent to an LLM to help build an attack timeline.

The JSON format makes it possible to review the relevant events without searching through raw EVTX binaries or XML.

## Why This Project

EVTX files are binary and can contain large volumes of event data. This project narrows that data down to:

- Related events from multiple EVTX files
- Records that match a defined rule
- Structured JSON that is easier to review and send to downstream tools

The original EVTX files remain available for full analysis in Event Viewer or another forensic tool.
(win+R eventvwr wow! DIY , i am not building graphs to view the events)

## Rules

The current rules are intentionally simple and serve as a starting point for learning and experimentation. Sigma rule integration will not yet implemented.(to complex for this project)

## AI-Assisted Development

Most of the project implementation and test cases are written by me. AI assistance has been used for selected tasks, including EVTX parsing, generating simple YAML rules, and debugging unexpected output during testing.

