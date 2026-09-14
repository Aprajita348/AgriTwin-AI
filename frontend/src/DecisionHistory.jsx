import { useEffect, useState } from "react";

const STORAGE_KEY =
  "agritwin_decision_history";

function DecisionHistory() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    loadHistory();
  }, []);

  function loadHistory() {
    const saved =
      localStorage.getItem(STORAGE_KEY);

    if (!saved) {
      setHistory([]);
      return;
    }

    try {
      setHistory(JSON.parse(saved));
    } catch {
      setHistory([]);
    }
  }

  function clearHistory() {
    localStorage.removeItem(
      STORAGE_KEY
    );

    setHistory([]);
  }

  return (
    <section>
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <span className="rounded-full bg-[#F6E7A1] px-3 py-1 text-xs font-semibold">
            Decision History
          </span>

          <h2 className="mt-4 text-4xl font-bold tracking-tight">
            Your previous AI decisions.
          </h2>

          <p className="mt-3 text-sm text-[#64746D]">
            Review previous farm analyses saved in this browser.
          </p>
        </div>

        {history.length > 0 && (
          <button
            onClick={clearHistory}
            className="rounded-xl bg-[#F3B5A4] px-4 py-2 text-xs font-bold"
          >
            Clear History
          </button>
        )}
      </div>

      {history.length === 0 ? (
        <div className="rounded-3xl bg-white p-10 text-center shadow-sm ring-1 ring-[#DDE7DD]">
          <div className="text-4xl">🌱</div>

          <h3 className="mt-4 text-xl font-bold">
            No decisions yet
          </h3>

          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-[#64746D]">
            Run an AI Farm Analysis and your
            previous decision will appear here.
          </p>
        </div>
      ) : (
        <div className="space-y-5">
          {history.map((item) => (
            <HistoryCard
              key={item.id}
              item={item}
            />
          ))}
        </div>
      )}
    </section>
  );
}

function HistoryCard({ item }) {
  return (
    <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-[#DDE7DD]">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <span className="rounded-full bg-[#CDE8D2] px-3 py-1 text-xs font-semibold">
            AI Farm Analysis
          </span>

          <h3 className="mt-3 text-2xl font-bold">
            {item.crop}
          </h3>

          <p className="mt-1 text-xs text-[#64746D]">
            {item.date}
          </p>
        </div>

        <div className="rounded-2xl bg-[#F7F4E9] p-4">
          <p className="text-xs text-[#64746D]">
            Decision Score
          </p>

          <p className="mt-1 text-2xl font-bold">
            {item.decision_score}%
          </p>
        </div>
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-4">
        <HistoryMetric
          label="Yield"
          value={`${item.yield} kg/ha`}
        />

        <HistoryMetric
          label="Profit"
          value={`₹${Number(
            item.profit
          ).toLocaleString("en-IN")}`}
        />

        <HistoryMetric
          label="Sustainability"
          value={`${item.sustainability}/100`}
        />

        <HistoryMetric
          label="Climate Risk"
          value={`${item.climate_risk} · ${item.risk_level}`}
        />
      </div>
    </div>
  );
}

function HistoryMetric({
  label,
  value,
}) {
  return (
    <div className="rounded-2xl bg-[#F7F4E9] p-4">
      <p className="text-xs text-[#64746D]">
        {label}
      </p>

      <p className="mt-2 text-sm font-bold">
        {value}
      </p>
    </div>
  );
}

export function saveDecisionToHistory(
  result
) {
  const existing =
    JSON.parse(
      localStorage.getItem(STORAGE_KEY) ||
      "[]"
    );

  const entry = {
    id: Date.now(),
    date: new Date().toLocaleString(
      "en-IN"
    ),
    crop:
      result.recommended_crop.crop,
    decision_score:
      result.recommended_crop.decision_score,
    yield:
      result.recommended_crop
        .predicted_yield_kg_per_ha,
    profit:
      Math.round(
        result.recommended_crop
          .estimated_profit
      ),
    sustainability:
      result.sustainability
        .sustainability_score,
    climate_risk:
      result.climate_analysis
        .climate_risk,
    risk_level:
      result.climate_analysis
        .risk_level,
  };

  const updated = [
    entry,
    ...existing,
  ].slice(0, 10);

  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify(updated)
  );
}

export default DecisionHistory;