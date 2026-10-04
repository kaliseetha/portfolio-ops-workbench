from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import EvidenceRecord, PortfolioException, ReviewEvent


CASES = [
    {
        "id": "EX-20481",
        "account": "•••• 4821",
        "household": "Morgan Household",
        "category": "Position mismatch",
        "description": "Quantity differs between source records",
        "priority": "High",
        "status": "Open",
        "age": "2h 14m",
        "display_value": "$18,420",
        "rule": "Quantity variance greater than 1 share",
        "internal": ("240.00", "$41,280.00", "2026-09-30", "Portfolio ledger"),
        "external": ("120.00", "$22,860.00", "2026-09-30", "Custodian feed"),
        "explanation": "The portfolio ledger reports 240 shares, while the custodian feed reports 120 shares as of the same date. The 120-share difference exceeds the configured one-share threshold. The source records do not identify the cause.",
        "checklist": [
            "Compare the prior-day quantities in both records.",
            "Check for a pending or recently settled transaction.",
            "Confirm the account and security mapping before adjusting records.",
        ],
    },
    {
        "id": "EX-20479",
        "account": "•••• 9910",
        "household": "Ellis Family",
        "category": "Cash variance",
        "description": "Cash balance outside tolerance",
        "priority": "High",
        "status": "Open",
        "age": "3h 06m",
        "display_value": "$12,750",
        "rule": "Cash variance greater than $500",
        "internal": ("—", "$86,440.00", "2026-09-30", "Portfolio ledger"),
        "external": ("—", "$73,690.00", "2026-09-30", "Custodian feed"),
        "explanation": "The ledger cash balance is $12,750 higher than the custodian record. This is outside the configured $500 tolerance. No transaction detail is included in these records to explain the difference.",
        "checklist": [
            "Review cash activity since the previous reconciliation.",
            "Check whether a settlement is pending.",
            "Verify both records use the same currency and as-of date.",
        ],
    },
    {
        "id": "EX-20476",
        "account": "•••• 1375",
        "household": "Brooks Household",
        "category": "Unmatched security",
        "description": "Security identifier not mapped",
        "priority": "Medium",
        "status": "Investigating",
        "age": "5h 32m",
        "display_value": "$8,915",
        "rule": "Source security ID not found in reference map",
        "internal": ("85.00", "$8,915.00", "2026-09-30", "Portfolio ledger"),
        "external": ("85.00", "$8,915.00", "2026-09-30", "Custodian feed"),
        "explanation": "The position quantities and values match, but the source security identifier has no entry in the demo reference map. This may be a mapping issue; the supplied records do not confirm that.",
        "checklist": [
            "Check whether the security has a new or alternate identifier.",
            "Review the reference-map update history.",
            "Confirm the security description with an authorized data source.",
        ],
    },
    {
        "id": "EX-20472",
        "account": "•••• 7304",
        "household": "Rivera Household",
        "category": "Stale record",
        "description": "Source records have different as-of dates",
        "priority": "Medium",
        "status": "Open",
        "age": "1d 02h",
        "display_value": "$6,240",
        "rule": "Record age difference greater than one business day",
        "internal": ("80.00", "$6,240.00", "2026-09-30", "Portfolio ledger"),
        "external": ("80.00", "$6,240.00", "2026-09-29", "Custodian feed"),
        "explanation": "Both records show 80 shares and $6,240, but the custodian record is one calendar day older. The current evidence supports a date mismatch, not a quantity or value break.",
        "checklist": [
            "Check whether the latest custodian file was received.",
            "Confirm whether the source schedule includes a market holiday.",
            "Re-run the comparison after the next scheduled feed.",
        ],
    },
    {
        "id": "EX-20469",
        "account": "•••• 2058",
        "household": "Chen Household",
        "category": "Cash variance",
        "description": "Small cash difference below review threshold",
        "priority": "Low",
        "status": "Open",
        "age": "1d 05h",
        "display_value": "$128",
        "rule": "Cash variance greater than $100",
        "internal": ("—", "$18,504.00", "2026-09-30", "Portfolio ledger"),
        "external": ("—", "$18,376.00", "2026-09-30", "Custodian feed"),
        "explanation": "The ledger is $128 higher than the custodian feed and exceeds the demo rule's $100 review threshold. No cash activity detail is present.",
        "checklist": [
            "Compare posted cash activity in both source records.",
            "Check for fees or interest posted on different schedules.",
            "Confirm whether the difference remains after the next feed.",
        ],
    },
    {
        "id": "EX-20465",
        "account": "•••• 6812",
        "household": "Patel Household",
        "category": "Position mismatch",
        "description": "Fractional quantity difference",
        "priority": "Low",
        "status": "Open",
        "age": "1d 08h",
        "display_value": "$34",
        "rule": "Quantity variance greater than 0.01 share",
        "internal": ("16.25", "$2,744.00", "2026-09-30", "Portfolio ledger"),
        "external": ("16.24", "$2,710.00", "2026-09-30", "Custodian feed"),
        "explanation": "The records differ by 0.01 share, which meets the configured threshold. The records do not include enough detail to determine why the fractional quantities differ.",
        "checklist": [
            "Confirm the precision used by each source.",
            "Compare the original transaction quantity.",
            "Check the next feed before making any adjustment.",
        ],
    },
    {
        "id": "EX-20461",
        "account": "•••• 4439",
        "household": "Foster Household",
        "category": "Unmatched security",
        "description": "Ticker present, identifier missing",
        "priority": "Medium",
        "status": "Open",
        "age": "2d 01h",
        "display_value": "$4,380",
        "rule": "Identifier is required for a security match",
        "internal": ("60.00", "$4,380.00", "2026-09-30", "Portfolio ledger"),
        "external": ("60.00", "$4,380.00", "2026-09-30", "Custodian feed"),
        "explanation": "The displayed quantities and values match, but the custodian record is missing a required security identifier. The ticker alone does not verify the security match.",
        "checklist": [
            "Retrieve the full identifier from an approved reference source.",
            "Compare the security description across records.",
            "Do not merge records based only on the ticker.",
        ],
    },
    {
        "id": "EX-20458",
        "account": "•••• 8492",
        "household": "Bennett Household",
        "category": "Position mismatch",
        "description": "Custodian position not in portfolio ledger",
        "priority": "High",
        "status": "Open",
        "age": "2d 04h",
        "display_value": "$27,600",
        "rule": "Position exists in only one source",
        "internal": ("0.00", "$0.00", "2026-09-30", "Portfolio ledger"),
        "external": ("300.00", "$27,600.00", "2026-09-30", "Custodian feed"),
        "explanation": "A 300-share position valued at $27,600 appears in the custodian record and not in the portfolio ledger. The available evidence does not establish whether this is a missing position or a mapping issue.",
        "checklist": [
            "Verify the account and security identifiers.",
            "Review recent transfers or corporate actions.",
            "Escalate for review before updating either source.",
        ],
    },
    {
        "id": "EX-20453",
        "account": "•••• 5603",
        "household": "Hayes Household",
        "category": "Stale record",
        "description": "Latest source file is delayed",
        "priority": "Medium",
        "status": "Open",
        "age": "2d 11h",
        "display_value": "$1,960",
        "rule": "Source data exceeds one-day freshness threshold",
        "internal": ("40.00", "$1,960.00", "2026-09-30", "Portfolio ledger"),
        "external": ("40.00", "$1,960.00", "2026-09-28", "Custodian feed"),
        "explanation": "The custodian record is two calendar days older than the ledger. Quantity and value match in the displayed data, but the comparison may be incomplete until the feed is refreshed.",
        "checklist": [
            "Check the feed receipt log.",
            "Confirm the scheduled delivery window.",
            "Reconcile again when current data is available.",
        ],
    },
    {
        "id": "EX-20449",
        "account": "•••• 1186",
        "household": "Ward Household",
        "category": "Cash variance",
        "description": "Currency field is missing from source",
        "priority": "Low",
        "status": "Resolved",
        "age": "3d 03h",
        "display_value": "$0",
        "rule": "Currency is required for cash comparison",
        "internal": ("—", "$9,380.00", "2026-09-30", "Portfolio ledger"),
        "external": ("—", "$9,380.00", "2026-09-30", "Custodian feed"),
        "explanation": "The amounts match, but the custodian record does not contain a currency field. A reviewer confirmed the demo records use the same currency.",
        "checklist": [
            "Verify currency from an authorized account source.",
            "Add a mapping note if the source field is routinely omitted.",
            "Close only after the reviewer confirms the records are comparable.",
        ],
    },
]


def seed_cases(session: Session) -> None:
    for display_order, data in enumerate(CASES):
        if session.get(PortfolioException, data["id"]) is not None:
            continue

        exception = PortfolioException(
            id=data["id"],
            display_order=display_order,
            account=data["account"],
            household=data["household"],
            category=data["category"],
            description=data["description"],
            priority=data["priority"],
            status=data["status"],
            age=data["age"],
            display_value=data["display_value"],
            rule=data["rule"],
            explanation=data["explanation"],
            checklist=data["checklist"],
        )
        exception.evidence = [
            EvidenceRecord(
                side=side,
                quantity=record[0],
                value=record[1],
                as_of=date.fromisoformat(record[2]),
                source=record[3],
            )
            for side, record in (("internal", data["internal"]), ("external", data["external"]))
        ]
        exception.activities = [
            ReviewEvent(
                event_type="detected",
                message="Exception detected by configured rule",
                actor="System",
            )
        ]
        session.add(exception)

    session.commit()
