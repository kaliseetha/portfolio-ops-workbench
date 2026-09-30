import { useMemo, useState } from "react";
import {
  Activity,
  ArrowDown,
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  BadgeCheck,
  Bell,
  BookOpen,
  BriefcaseBusiness,
  Check,
  CheckCircle2,
  ChevronDown,
  CircleHelp,
  Clock3,
  Download,
  Ellipsis,
  FileText,
  Filter,
  Landmark,
  LayoutDashboard,
  ListChecks,
  LoaderCircle,
  MessageSquareText,
  Search,
  ShieldCheck,
  Sparkles,
  Wallet,
  X,
} from "lucide-react";

type ExceptionCategory = "Position mismatch" | "Cash variance" | "Unmatched security" | "Stale record";
type ExceptionStatus = "Open" | "Investigating" | "Resolved" | "Dismissed";
type Priority = "High" | "Medium" | "Low";
type ReviewAction = "Investigating" | "Resolved" | "Dismissed";

type PortfolioException = {
  id: string;
  account: string;
  household: string;
  category: ExceptionCategory;
  description: string;
  priority: Priority;
  status: ExceptionStatus;
  age: string;
  value: string;
  rule: string;
  internal: { quantity: string; value: string; asOf: string; source: string };
  external: { quantity: string; value: string; asOf: string; source: string };
  explanation: string;
  checklist: string[];
};

const initialExceptions: PortfolioException[] = [
  {
    id: "EX-20481",
    account: "•••• 4821",
    household: "Morgan Household",
    category: "Position mismatch",
    description: "Quantity differs between source records",
    priority: "High",
    status: "Open",
    age: "2h 14m",
    value: "$18,420",
    rule: "Quantity variance greater than 1 share",
    internal: { quantity: "240.00", value: "$41,280.00", asOf: "Sep 30, 2026", source: "Portfolio ledger" },
    external: { quantity: "120.00", value: "$22,860.00", asOf: "Sep 30, 2026", source: "Custodian feed" },
    explanation:
      "The portfolio ledger reports 240 shares, while the custodian feed reports 120 shares as of the same date. The 120-share difference exceeds the configured one-share threshold. The source records do not identify the cause.",
    checklist: ["Compare the prior-day quantities in both records.", "Check for a pending or recently settled transaction.", "Confirm the account and security mapping before adjusting records."],
  },
  {
    id: "EX-20479",
    account: "•••• 9910",
    household: "Ellis Family",
    category: "Cash variance",
    description: "Cash balance outside tolerance",
    priority: "High",
    status: "Open",
    age: "3h 06m",
    value: "$12,750",
    rule: "Cash variance greater than $500",
    internal: { quantity: "—", value: "$86,440.00", asOf: "Sep 30, 2026", source: "Portfolio ledger" },
    external: { quantity: "—", value: "$73,690.00", asOf: "Sep 30, 2026", source: "Custodian feed" },
    explanation:
      "The ledger cash balance is $12,750 higher than the custodian record. This is outside the configured $500 tolerance. No transaction detail is included in these records to explain the difference.",
    checklist: ["Review cash activity since the previous reconciliation.", "Check whether a settlement is pending.", "Verify both records use the same currency and as-of date."],
  },
  {
    id: "EX-20476",
    account: "•••• 1375",
    household: "Brooks Household",
    category: "Unmatched security",
    description: "Security identifier not mapped",
    priority: "Medium",
    status: "Investigating",
    age: "5h 32m",
    value: "$8,915",
    rule: "Source security ID not found in reference map",
    internal: { quantity: "85.00", value: "$8,915.00", asOf: "Sep 30, 2026", source: "Portfolio ledger" },
    external: { quantity: "85.00", value: "$8,915.00", asOf: "Sep 30, 2026", source: "Custodian feed" },
    explanation:
      "The position quantities and values match, but the source security identifier has no entry in the demo reference map. This may be a mapping issue; the supplied records do not confirm that.",
    checklist: ["Check whether the security has a new or alternate identifier.", "Review the reference-map update history.", "Confirm the security description with an authorized data source."],
  },
  {
    id: "EX-20472",
    account: "•••• 7304",
    household: "Rivera Household",
    category: "Stale record",
    description: "Source records have different as-of dates",
    priority: "Medium",
    status: "Open",
    age: "1d 02h",
    value: "$6,240",
    rule: "Record age difference greater than one business day",
    internal: { quantity: "80.00", value: "$6,240.00", asOf: "Sep 30, 2026", source: "Portfolio ledger" },
    external: { quantity: "80.00", value: "$6,240.00", asOf: "Sep 29, 2026", source: "Custodian feed" },
    explanation:
      "Both records show 80 shares and $6,240, but the custodian record is one calendar day older. The current evidence supports a date mismatch, not a quantity or value break.",
    checklist: ["Check whether the latest custodian file was received.", "Confirm whether the source schedule includes a market holiday.", "Re-run the comparison after the next scheduled feed."],
  },
  {
    id: "EX-20469",
    account: "•••• 2058",
    household: "Chen Household",
    category: "Cash variance",
    description: "Small cash difference below review threshold",
    priority: "Low",
    status: "Open",
    age: "1d 05h",
    value: "$128",
    rule: "Cash variance greater than $100",
    internal: { quantity: "—", value: "$18,504.00", asOf: "Sep 30, 2026", source: "Portfolio ledger" },
    external: { quantity: "—", value: "$18,376.00", asOf: "Sep 30, 2026", source: "Custodian feed" },
    explanation:
      "The ledger is $128 higher than the custodian feed and exceeds the demo rule's $100 review threshold. No cash activity detail is present.",
    checklist: ["Compare posted cash activity in both source records.", "Check for fees or interest posted on different schedules.", "Confirm whether the difference remains after the next feed."],
  },
  {
    id: "EX-20465",
    account: "•••• 6812",
    household: "Patel Household",
    category: "Position mismatch",
    description: "Fractional quantity difference",
    priority: "Low",
    status: "Open",
    age: "1d 08h",
    value: "$34",
    rule: "Quantity variance greater than 0.01 share",
    internal: { quantity: "16.25", value: "$2,744.00", asOf: "Sep 30, 2026", source: "Portfolio ledger" },
    external: { quantity: "16.24", value: "$2,710.00", asOf: "Sep 30, 2026", source: "Custodian feed" },
    explanation:
      "The records differ by 0.01 share, which meets the configured threshold. The records do not include enough detail to determine why the fractional quantities differ.",
    checklist: ["Confirm the precision used by each source.", "Compare the original transaction quantity.", "Check the next feed before making any adjustment."],
  },
  {
    id: "EX-20461",
    account: "•••• 4439",
    household: "Foster Household",
    category: "Unmatched security",
    description: "Ticker present, identifier missing",
    priority: "Medium",
    status: "Open",
    age: "2d 01h",
    value: "$4,380",
    rule: "Identifier is required for a security match",
    internal: { quantity: "60.00", value: "$4,380.00", asOf: "Sep 30, 2026", source: "Portfolio ledger" },
    external: { quantity: "60.00", value: "$4,380.00", asOf: "Sep 30, 2026", source: "Custodian feed" },
    explanation:
      "The displayed quantities and values match, but the custodian record is missing a required security identifier. The ticker alone does not verify the security match.",
    checklist: ["Retrieve the full identifier from an approved reference source.", "Compare the security description across records.", "Do not merge records based only on the ticker."],
  },
  {
    id: "EX-20458",
    account: "•••• 8492",
    household: "Bennett Household",
    category: "Position mismatch",
    description: "Custodian position not in portfolio ledger",
    priority: "High",
    status: "Open",
    age: "2d 04h",
    value: "$27,600",
    rule: "Position exists in only one source",
    internal: { quantity: "0.00", value: "$0.00", asOf: "Sep 30, 2026", source: "Portfolio ledger" },
    external: { quantity: "300.00", value: "$27,600.00", asOf: "Sep 30, 2026", source: "Custodian feed" },
    explanation:
      "A 300-share position valued at $27,600 appears in the custodian record and not in the portfolio ledger. The available evidence does not establish whether this is a missing position or a mapping issue.",
    checklist: ["Verify the account and security identifiers.", "Review recent transfers or corporate actions.", "Escalate for review before updating either source."],
  },
  {
    id: "EX-20453",
    account: "•••• 5603",
    household: "Hayes Household",
    category: "Stale record",
    description: "Latest source file is delayed",
    priority: "Medium",
    status: "Open",
    age: "2d 11h",
    value: "$1,960",
    rule: "Source data exceeds one-day freshness threshold",
    internal: { quantity: "40.00", value: "$1,960.00", asOf: "Sep 30, 2026", source: "Portfolio ledger" },
    external: { quantity: "40.00", value: "$1,960.00", asOf: "Sep 28, 2026", source: "Custodian feed" },
    explanation:
      "The custodian record is two calendar days older than the ledger. Quantity and value match in the displayed data, but the comparison may be incomplete until the feed is refreshed.",
    checklist: ["Check the feed receipt log.", "Confirm the scheduled delivery window.", "Reconcile again when current data is available."],
  },
  {
    id: "EX-20449",
    account: "•••• 1186",
    household: "Ward Household",
    category: "Cash variance",
    description: "Currency field is missing from source",
    priority: "Low",
    status: "Resolved",
    age: "3d 03h",
    value: "$0",
    rule: "Currency is required for cash comparison",
    internal: { quantity: "—", value: "$9,380.00", asOf: "Sep 30, 2026", source: "Portfolio ledger" },
    external: { quantity: "—", value: "$9,380.00", asOf: "Sep 30, 2026", source: "Custodian feed" },
    explanation:
      "The amounts match, but the custodian record does not contain a currency field. A reviewer confirmed the demo records use the same currency.",
    checklist: ["Verify currency from an authorized account source.", "Add a mapping note if the source field is routinely omitted.", "Close only after the reviewer confirms the records are comparable."],
  },
];

const navItems = [
  { label: "Overview", icon: LayoutDashboard },
  { label: "Exceptions", icon: ListChecks, active: true, count: String(initialExceptions.length) },
  { label: "Activity", icon: Activity },
];

function App() {
  const [exceptions, setExceptions] = useState(initialExceptions);
  const [selectedId, setSelectedId] = useState(initialExceptions[0].id);
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("All categories");
  const [statusFilter, setStatusFilter] = useState("All statuses");
  const [explanationVisible, setExplanationVisible] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [toast, setToast] = useState("");
  const [events, setEvents] = useState<string[]>(["Exception detected by Position variance rule"]);

  const selectedException = exceptions.find((item) => item.id === selectedId) ?? exceptions[0];
  const visibleExceptions = useMemo(() => {
    const term = search.trim().toLowerCase();
    return exceptions.filter((item) => {
      const matchesSearch = !term || [item.id, item.account, item.household, item.category].some((value) => value.toLowerCase().includes(term));
      const matchesCategory = categoryFilter === "All categories" || item.category === categoryFilter;
      const matchesStatus = statusFilter === "All statuses" || item.status === statusFilter;
      return matchesSearch && matchesCategory && matchesStatus;
    });
  }, [exceptions, search, categoryFilter, statusFilter]);

  const openCount = exceptions.filter((item) => item.status === "Open").length;
  const highPriorityCount = exceptions.filter((item) => item.priority === "High" && item.status !== "Resolved" && item.status !== "Dismissed").length;

  function showToast(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(""), 2600);
  }

  function generateExplanation() {
    setGenerating(true);
    window.setTimeout(() => {
      setExplanationVisible(true);
      setGenerating(false);
      setEvents((current) => [`Demo explanation viewed · ${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`, ...current]);
    }, 650);
  }

  function reviewException(action: ReviewAction) {
    setExceptions((current) => current.map((item) => item.id === selectedId ? { ...item, status: action } : item));
    setEvents((current) => [`Marked ${action.toLowerCase()} · ${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`, ...current]);
    showToast(action === "Resolved" ? "Exception marked as resolved" : action === "Dismissed" ? "Exception dismissed" : "Review started");
  }

  function exportQueue() {
    const header = ["Exception ID", "Account", "Category", "Priority", "Status", "Age", "Value"];
    const rows = visibleExceptions.map((item) => [item.id, item.account, item.category, item.priority, item.status, item.age, item.value]);
    const csv = [header, ...rows].map((row) => row.map((cell) => `"${cell.replace(/"/g, '""')}"`).join(",")).join("\n");
    const link = document.createElement("a");
    link.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    link.download = "synthetic-exception-queue.csv";
    link.click();
    URL.revokeObjectURL(link.href);
    showToast("Synthetic exception queue exported");
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#home" aria-label="OpsDesk home">
          <span className="brand-mark"><Landmark size={19} strokeWidth={2.2} /></span>
          <span className="brand-name">ops<span>desk</span></span>
        </a>
        <div className="workspace-switcher">
          <div className="workspace-icon">N</div>
          <div className="workspace-copy"><strong>Northstar Demo</strong><span>Operations team</span></div>
          <ChevronDown size={15} />
        </div>
        <div className="nav-label">WORKSPACE</div>
        <nav className="primary-nav" aria-label="Main navigation">
          {navItems.map(({ label, icon: Icon, active, count }) => (
            <button className={`nav-item${active ? " active" : ""}`} key={label} onClick={() => label !== "Exceptions" && showToast(`${label} view is outside this demo scope`)}>
              <Icon size={17} />
              <span>{label}</span>
              {count && <span className="nav-count">{count}</span>}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="governance-card">
            <span className="governance-icon"><ShieldCheck size={16} /></span>
            <strong>Human in control</strong>
            <p>AI drafts are reviewed by your team. No automatic account changes.</p>
            <button onClick={() => showToast("Review controls are enabled for this demo")}><BookOpen size={13} /> Review controls</button>
          </div>
          <button className="nav-item help-item" onClick={() => showToast("This is a synthetic-data product demo")}><CircleHelp size={17} /><span>Help & support</span></button>
          <div className="user-profile">
            <div className="avatar">JD</div>
            <div className="user-copy"><strong>Jordan Davis</strong><span>Operations reviewer</span></div>
            <Ellipsis size={18} />
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumbs"><span>Operations</span><span className="breadcrumb-divider">/</span><strong>Exception workbench</strong></div>
          <div className="topbar-actions">
            <span className="demo-chip"><span className="demo-dot" /> Synthetic data demo</span>
            <button className="icon-button notification-button" aria-label="Notifications" onClick={() => showToast("You’re all caught up")}><Bell size={18} /><i /></button>
            <div className="top-avatar">JD</div>
          </div>
        </header>

        <div className="page-content">
          <section className="page-heading">
            <div>
              <div className="eyebrow"><span className="eyebrow-line" /> PORTFOLIO OPERATIONS</div>
              <h1>Exception workbench</h1>
              <p className="page-subtitle">Review, investigate, and resolve portfolio discrepancies.</p>
            </div>
            <button className="button button-secondary export-button" onClick={exportQueue}><Download size={15} /> Export queue</button>
          </section>

          <section className="metric-grid" aria-label="Exception summary">
            <MetricCard label="Open exceptions" value={String(openCount).padStart(2, "0")} note="Across all categories" icon={<ListChecks size={17} />} tone="blue" />
            <MetricCard label="High priority" value={String(highPriorityCount).padStart(2, "0")} note="Require timely review" icon={<ArrowUpRight size={18} />} tone="orange" />
            <MetricCard label="In investigation" value={String(exceptions.filter((item) => item.status === "Investigating").length).padStart(2, "0")} note="Being reviewed now" icon={<Search size={17} />} tone="violet" />
            <MetricCard label="Resolved in queue" value={String(exceptions.filter((item) => item.status === "Resolved").length).padStart(2, "0")} note="In this synthetic dataset" icon={<BadgeCheck size={17} />} tone="green" />
          </section>

          <section className="workbench">
            <div className="queue-panel">
              <div className="panel-heading queue-heading">
                <div><h2>Reconciliation queue</h2><p>Prioritized items for your review</p></div>
                <button className="icon-button subtle-icon" aria-label="Queue options" onClick={() => showToast("Queue options are not configured in this demo")}><Ellipsis size={19} /></button>
              </div>
              <div className="queue-tools">
                <label className="search-box">
                  <Search size={16} />
                  <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search exceptions..." aria-label="Search exceptions" />
                  {search && <button aria-label="Clear search" onClick={() => setSearch("")}><X size={14} /></button>}
                </label>
                <label className="select-wrap"><Filter size={14} /><select value={categoryFilter} onChange={(event) => setCategoryFilter(event.target.value)} aria-label="Filter by category"><option>All categories</option><option>Position mismatch</option><option>Cash variance</option><option>Unmatched security</option><option>Stale record</option></select><ChevronDown size={13} /></label>
                <label className="select-wrap status-select"><select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)} aria-label="Filter by status"><option>All statuses</option><option>Open</option><option>Investigating</option><option>Resolved</option><option>Dismissed</option></select><ChevronDown size={13} /></label>
              </div>
              <div className="table-scroll">
                <table className="exception-table">
                  <thead><tr><th>EXCEPTION</th><th>CATEGORY</th><th>PRIORITY</th><th>AGE</th><th>STATUS</th><th><span className="sr-only">Select</span></th></tr></thead>
                  <tbody>
                    {visibleExceptions.map((item) => (
                      <tr className={selectedId === item.id ? "selected-row" : ""} key={item.id} onClick={() => { setSelectedId(item.id); setExplanationVisible(false); setEvents(["Exception detected by configured rule"]); }} tabIndex={0} onKeyDown={(event) => { if (event.key === "Enter") { setSelectedId(item.id); setExplanationVisible(false); } }}>
                        <td><div className="exception-main"><span className={`category-symbol ${item.category === "Cash variance" ? "cash" : item.category === "Stale record" ? "stale" : item.category === "Unmatched security" ? "security" : "position"}`}>{item.category === "Cash variance" ? <Wallet size={14} /> : item.category === "Stale record" ? <Clock3 size={14} /> : item.category === "Unmatched security" ? <BriefcaseBusiness size={14} /> : <ArrowDownRight size={14} />}</span><span><strong>{item.id}</strong><small>{item.account} <span className="dot-separator">·</span> {item.household}</small></span></div></td>
                        <td><span className="category-text">{item.category}</span></td>
                        <td><PriorityBadge priority={item.priority} /></td>
                        <td><span className="age-text">{item.age}</span></td>
                        <td><StatusBadge status={item.status} /></td>
                        <td><ArrowRight className="row-arrow" size={15} /></td>
                      </tr>
                    ))}
                    {visibleExceptions.length === 0 && <tr><td className="empty-state" colSpan={6}><Search size={19} /><strong>No exceptions found</strong><span>Try changing your search or filters.</span></td></tr>}
                  </tbody>
                </table>
              </div>
              <div className="queue-footer"><span>Showing <strong>{visibleExceptions.length ? "1–" + visibleExceptions.length : "0"}</strong> of <strong>{exceptions.length}</strong> synthetic records</span><span className="queue-updated"><span className="live-dot" /> Updated just now</span></div>
            </div>

            <aside className="detail-panel">
              <div className="detail-topline"><span className="detail-kicker">EXCEPTION DETAILS</span><button className="icon-button subtle-icon" aria-label="More exception options" onClick={() => showToast("More actions are not available in this demo")}><Ellipsis size={19} /></button></div>
              <div className="detail-id-row"><h2>{selectedException.id}</h2><PriorityBadge priority={selectedException.priority} /></div>
              <p className="detail-summary">{selectedException.description}</p>
              <div className="detail-meta">
                <div><span>ACCOUNT</span><strong>{selectedException.account}</strong></div>
                <div><span>HOUSEHOLD</span><strong>{selectedException.household}</strong></div>
              </div>
              <div className="detail-divider" />
              <div className="section-title-row"><h3>Reconciliation evidence</h3><span className="evidence-count"><FileText size={12} /> 2 records</span></div>
              <p className="rule-note"><span className="rule-icon"><Filter size={12} /></span> Flagged by <strong>{selectedException.rule}</strong></p>
              <div className="source-card">
                <div className="source-heading"><span className="source-dot ledger-dot" /><strong>{selectedException.internal.source}</strong><span>{selectedException.internal.asOf}</span></div>
                <div className="source-data"><div><span>QUANTITY</span><strong>{selectedException.internal.quantity}</strong></div><div><span>VALUE</span><strong>{selectedException.internal.value}</strong></div></div>
              </div>
              <div className="source-card">
                <div className="source-heading"><span className="source-dot custodian-dot" /><strong>{selectedException.external.source}</strong><span>{selectedException.external.asOf}</span></div>
                <div className="source-data"><div><span>QUANTITY</span><strong>{selectedException.external.quantity}</strong></div><div><span>VALUE</span><strong>{selectedException.external.value}</strong></div></div>
              </div>
              <div className="variance-banner"><span className="variance-icon"><ArrowDown size={14} /></span><span><strong>Variance detected</strong><small>Difference to review</small></span><strong className="variance-value">{selectedException.value}</strong></div>

              <div className="ai-heading"><div className="ai-heading-label"><span className="ai-spark"><Sparkles size={14} /></span><h3>AI review assistant</h3></div><span className="draft-label">DRAFT</span></div>
              <div className="ai-card">
                {!explanationVisible ? (
                  <div className="ai-empty">
                    <span className="ai-empty-icon"><MessageSquareText size={19} /></span>
                    <strong>Make sense of this exception</strong>
                    <p>Get an evidence-based summary and a checklist for your review.</p>
                    <button className="button button-ai" disabled={generating} onClick={generateExplanation}>{generating ? <LoaderCircle size={15} className="spin" /> : <Sparkles size={15} />}{generating ? "Preparing demo summary..." : "Generate AI explanation"}</button>
                  </div>
                ) : (
                  <div className="ai-result">
                    <div className="ai-result-label"><Sparkles size={13} /> DEMO-GENERATED · NOT CONNECTED TO AI</div>
                    <p>{selectedException.explanation}</p>
                    <div className="checklist-title"><ListChecks size={14} /><strong>Suggested review checklist</strong></div>
                    <ul>{selectedException.checklist.map((step) => <li key={step}>{step}</li>)}</ul>
                    <div className="ai-source-note"><ShieldCheck size={13} /> Based only on the synthetic records shown above.</div>
                  </div>
                )}
              </div>

              <div className="activity-heading"><h3>Recent activity</h3><button onClick={() => showToast("Showing activity for the selected exception")}>View all</button></div>
              <div className="activity-entry"><span className="activity-marker"><Activity size={12} /></span><span><strong>{events[0]}</strong><small>Jordan Davis <span>· just now</span></small></span></div>
              {events.length > 1 && <div className="activity-entry older-entry"><span className="activity-marker muted-marker"><CheckCircle2 size={12} /></span><span><strong>{events[1]}</strong><small>System <span>· recently</span></small></span></div>}

              <div className="review-actions">
                <button className="button button-secondary" onClick={() => reviewException("Investigating")}><Search size={14} /> Investigate</button>
                <button className="button button-primary" onClick={() => reviewException("Resolved")}><Check size={15} /> Resolve</button>
              </div>
              <button className="dismiss-button" onClick={() => reviewException("Dismissed")}>Dismiss exception</button>
            </aside>
          </section>
          <footer className="page-footer"><span><ShieldCheck size={14} /> Human review required for all exception decisions.</span><span>OpsDesk POC <span className="footer-dot">·</span> v0.1</span></footer>
        </div>
      </main>
      {toast && <div className="toast" role="status"><CheckCircle2 size={16} />{toast}</div>}
    </div>
  );
}

function MetricCard({ label, value, note, icon, tone }: { label: string; value: string; note: string; icon: React.ReactNode; tone: string }) {
  return <article className="metric-card"><span className={`metric-icon ${tone}`}>{icon}</span><div className="metric-copy"><span>{label}</span><div className="metric-value-row"><strong>{value}</strong>{tone === "orange" && <span className="metric-trend"><ArrowUpRight size={13} /> 2 new</span>}</div><small>{note}</small></div></article>;
}

function PriorityBadge({ priority }: { priority: Priority }) {
  return <span className={`priority-badge ${priority.toLowerCase()}`}><i />{priority}</span>;
}

function StatusBadge({ status }: { status: ExceptionStatus }) {
  const style = status.toLowerCase().replace(" ", "-");
  return <span className={`status-badge ${style}`}><i />{status}</span>;
}

export default App;
