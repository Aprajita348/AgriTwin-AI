import { useState } from "react";
import { runWhatIfSimulation } from "./services/api";

function WhatIfSimulator({ result, formData }) {
  const [temperatureChange, setTemperatureChange] = useState(2);
  const [rainfallChange, setRainfallChange] = useState(-20);
  const [irrigationChange, setIrrigationChange] = useState(10);
  const [fertilizerChange, setFertilizerChange] = useState(0);

  const [simulation, setSimulation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSimulation() {
    if (!result) {
      setError("Run AI Farm Analysis first to create a baseline.");
      return;
    }

    setLoading(true);
    setError("");
    setSimulation(null);

    try {
      const data = await runWhatIfSimulation({
        crop: result.recommended_crop.crop,
        farm_size_acres: formData.farm_size_acres,
        baseline_yield_kg_per_ha:
          result.recommended_crop.predicted_yield_kg_per_ha,
        baseline_profit:
          result.recommended_crop.estimated_profit,
        baseline_water_liters:
          result.water_analysis.available_water_liters,
        baseline_sustainability_score:
          result.sustainability.sustainability_score,
        avg_temp_c: formData.avg_temp_c,
        rainfall_mm: formData.rainfall_mm,
        temperature_change: temperatureChange,
        rainfall_change_percent: rainfallChange,
        irrigation_change_percent: irrigationChange,
        fertilizer_change_percent: fertilizerChange,
      });

      setSimulation(data);
    } catch (err) {
      console.error(err);
      setError(
        err?.message ||
          "Could not run the simulation. Make sure the backend is running."
      );
    } finally {
      setLoading(false);
    }
  }

  function resetScenario() {
    setTemperatureChange(2);
    setRainfallChange(-20);
    setIrrigationChange(10);
    setFertilizerChange(0);
    setSimulation(null);
    setError("");
  }

  return (
    <section>
      {/* HERO */}
      <div className="mb-8">
        <span className="rounded-full bg-[#A8DADC] px-3 py-1 text-xs font-semibold text-[#263A32]">
          DIGITAL FARM SIMULATOR
        </span>

        <h2 className="mt-4 text-4xl font-bold tracking-tight text-[#263A32] md:text-5xl">
          What happens if you change the decision?
        </h2>

        <p className="mt-3 max-w-3xl text-sm leading-7 text-[#64746D] md:text-base">
          Test a farming decision virtually before applying it in the field.
          Compare your scenario against the current farm baseline.
        </p>
      </div>

      {/* NO BASELINE */}
      {!result && (
        <div className="mb-6 rounded-3xl bg-[#F6E7A1] p-5 text-sm font-medium text-[#4E4A29]">
          Run AI Farm Analysis first to create your baseline farm condition.
        </div>
      )}

      {/* SCENARIO + BASELINE */}
      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        {/* SCENARIO */}
        <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-[#DDE7DD] md:p-8">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h3 className="text-xl font-bold text-[#263A32]">
                Change your scenario
              </h3>

              <p className="mt-2 text-sm leading-6 text-[#64746D]">
                Adjust one or more conditions and simulate the outcome.
              </p>
            </div>

            <button
              type="button"
              onClick={resetScenario}
              className="rounded-xl border border-[#DDE7DD] px-4 py-2 text-xs font-bold text-[#64746D] transition hover:bg-[#F7F4E9]"
            >
              Reset
            </button>
          </div>

          <div className="mt-7 space-y-7">
            <ScenarioControl
              label="Temperature"
              description="Change in average temperature"
              value={temperatureChange}
              suffix="°C"
              min={-5}
              max={5}
              step={1}
              onChange={setTemperatureChange}
              color="bg-[#A8DADC]"
            />

            <ScenarioControl
              label="Rainfall"
              description="Percentage change in rainfall"
              value={rainfallChange}
              suffix="%"
              min={-50}
              max={50}
              step={5}
              onChange={setRainfallChange}
              color="bg-[#F6E7A1]"
            />

            <ScenarioControl
              label="Irrigation"
              description="Percentage change in irrigation"
              value={irrigationChange}
              suffix="%"
              min={-50}
              max={50}
              step={5}
              onChange={setIrrigationChange}
              color="bg-[#CDE8D2]"
            />

            <ScenarioControl
              label="Fertilizer"
              description="Percentage change in fertilizer"
              value={fertilizerChange}
              suffix="%"
              min={-50}
              max={50}
              step={5}
              onChange={setFertilizerChange}
              color="bg-[#F3B5A4]"
            />
          </div>

          <button
            type="button"
            onClick={handleSimulation}
            disabled={loading || !result}
            className="mt-8 w-full rounded-2xl bg-[#263A32] px-6 py-4 text-sm font-bold text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading
              ? "Running digital farm simulation..."
              : "Run Digital Farm Simulation →"}
          </button>

          {error && (
            <div className="mt-4 rounded-2xl bg-[#F3B5A4] p-4 text-sm leading-6 text-[#5C3025]">
              {error}
            </div>
          )}
        </div>

        {/* BASELINE */}
        <div className="rounded-3xl bg-[#263A32] p-6 text-white shadow-sm md:p-8">
          <span className="rounded-full bg-white/15 px-3 py-1 text-xs font-semibold">
            CURRENT BASELINE
          </span>

          <h3 className="mt-4 text-2xl font-bold">
            {result?.recommended_crop?.crop || "No analysis yet"}
          </h3>

          {result ? (
            <div className="mt-6 space-y-3">
              <BaselineRow
                label="Predicted Yield"
                value={`${Number(
                  result.recommended_crop.predicted_yield_kg_per_ha
                ).toLocaleString("en-IN")} kg/ha`}
              />

              <BaselineRow
                label="Estimated Profit"
                value={formatCurrency(
                  result.recommended_crop.estimated_profit
                )}
              />

              <BaselineRow
                label="Available Water"
                value={`${Math.round(
                  result.water_analysis.available_water_liters
                ).toLocaleString("en-IN")} L`}
              />

              <BaselineRow
                label="Sustainability"
                value={`${result.sustainability.sustainability_score}/100`}
              />
            </div>
          ) : (
            <p className="mt-5 text-sm leading-6 text-[#D5E0DB]">
              Baseline metrics will appear here after farm analysis.
            </p>
          )}

          {result && (
            <div className="mt-6 border-t border-white/10 pt-5">
              <p className="text-xs font-semibold uppercase tracking-wide text-[#AFC1B8]">
                Simulation principle
              </p>

              <p className="mt-2 text-sm leading-6 text-[#E4ECE7]">
                AgriTwin keeps the current farm as the baseline and estimates
                how the selected changes affect yield, profit, water and
                sustainability.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* SIMULATION RESULT */}
      {simulation && (
        <section className="mt-8">
          <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-[#DDE7DD] md:p-8">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <span className="rounded-full bg-[#A8DADC] px-3 py-1 text-xs font-semibold text-[#263A32]">
                  SIMULATION COMPLETE
                </span>

                <h3 className="mt-3 text-2xl font-bold text-[#263A32]">
                  Baseline vs Scenario
                </h3>
              </div>

              <span className="rounded-full bg-[#F7F4E9] px-4 py-2 text-sm font-bold text-[#263A32]">
                {simulation?.climate_risk?.risk_level || "Unknown"} climate risk
              </span>
            </div>

            {/* SCENARIO SUMMARY */}
            <div className="mt-6 grid gap-3 sm:grid-cols-4">
              <SummaryItem
                label="Temperature"
                value={formatSigned(temperatureChange, "°C")}
              />

              <SummaryItem
                label="Rainfall"
                value={formatSigned(rainfallChange, "%")}
              />

              <SummaryItem
                label="Irrigation"
                value={formatSigned(irrigationChange, "%")}
              />

              <SummaryItem
                label="Fertilizer"
                value={formatSigned(fertilizerChange, "%")}
              />
            </div>

            {/* RESULT CARDS */}
            <div className="mt-6 grid gap-4 md:grid-cols-2">
              <ComparisonCard
                title="Yield"
                baseline={`${Number(
                  simulation.baseline.yield_kg_per_ha
                ).toLocaleString("en-IN")} kg/ha`}
                scenario={`${Number(
                  simulation.scenario_result.yield_kg_per_ha
                ).toLocaleString("en-IN")} kg/ha`}
                change={simulation.change.yield_change_kg_per_ha}
                suffix=" kg/ha"
                bg="bg-[#CDE8D2]"
              />

              <ComparisonCard
                title="Profit"
                baseline={formatCurrency(simulation.baseline.profit)}
                scenario={formatCurrency(simulation.scenario_result.profit)}
                change={simulation.change.profit_change}
                currency={true}
                bg="bg-[#F6E7A1]"
              />

              <ComparisonCard
                title="Water"
                baseline={`${Math.round(
                  simulation.baseline.water_liters
                ).toLocaleString("en-IN")} L`}
                scenario={`${Math.round(
                  simulation.scenario_result.water_liters
                ).toLocaleString("en-IN")} L`}
                change={simulation.change.water_change_liters}
                suffix=" L"
                bg="bg-[#A8DADC]"
              />

              <ComparisonCard
                title="Sustainability"
                baseline={`${simulation.baseline.sustainability_score}/100`}
                scenario={`${simulation.scenario_result.sustainability_score}/100`}
                change={simulation.change.sustainability_change}
                suffix=""
                bg="bg-[#E7F1DE]"
              />
            </div>

            {/* CLIMATE IMPACT */}
            <div className="mt-6 rounded-2xl bg-[#F7F4E9] p-5">
              <p className="text-xs font-semibold uppercase tracking-wide text-[#64746D]">
                CLIMATE IMPACT
              </p>

              <p className="mt-2 text-sm leading-6 text-[#263A32]">
                {simulation?.climate_risk?.recommendation ||
                  "No climate recommendation returned."}
              </p>

              {simulation?.climate_risk?.drivers &&
                simulation.climate_risk.drivers.length > 0 && (
                  <div className="mt-4 flex flex-wrap gap-2">
                    {simulation.climate_risk.drivers.map((driver) => (
                      <span
                        key={driver}
                        className="rounded-full bg-white px-3 py-2 text-xs text-[#4E5E55]"
                      >
                        {driver}
                      </span>
                    ))}
                  </div>
                )}
            </div>

            {/* DECISION */}
            <div className="mt-6 rounded-2xl bg-[#F3B5A4] p-5">
              <p className="text-xs font-semibold uppercase tracking-wide text-[#5C3025]">
                AGRITWIN DECISION
              </p>

              <p className="mt-2 text-sm font-medium leading-7 text-[#3E2923]">
                {simulation.decision || "No decision recommendation returned."}
              </p>
            </div>
          </div>
        </section>
      )}
    </section>
  );
}

function ScenarioControl({
  label,
  description,
  value,
  suffix,
  min,
  max,
  step,
  onChange,
  color,
}) {
  return (
    <div>
      <div className="flex items-start justify-between gap-4">
        <div>
          <label className="text-sm font-semibold text-[#263A32]">
            {label}
          </label>

          <p className="mt-1 text-xs text-[#7A877F]">{description}</p>
        </div>

        <span
          className={`rounded-xl ${color} px-3 py-1 text-sm font-bold text-[#263A32]`}
        >
          {value > 0 ? "+" : ""}
          {value}
          {suffix}
        </span>
      </div>

      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
        className="mt-4 w-full accent-[#A8C3A0]"
      />

      <div className="mt-2 flex justify-between text-xs text-[#64746D]">
        <span>
          {min > 0 ? "+" : ""}
          {min}
          {suffix}
        </span>

        <span>Baseline</span>

        <span>
          {max > 0 ? "+" : ""}
          {max}
          {suffix}
        </span>
      </div>
    </div>
  );
}

function BaselineRow({ label, value }) {
  return (
    <div className="flex items-center justify-between rounded-2xl bg-white/10 p-4">
      <span className="text-sm text-[#C9D6D0]">{label}</span>

      <span className="text-right text-sm font-bold text-white">
        {value}
      </span>
    </div>
  );
}

function SummaryItem({ label, value }) {
  return (
    <div className="rounded-2xl border border-[#DDE7DD] bg-[#F7F4E9] p-4">
      <p className="text-xs font-semibold uppercase tracking-wide text-[#7A877F]">
        {label}
      </p>

      <p className="mt-1 text-sm font-bold text-[#263A32]">{value}</p>
    </div>
  );
}

function ComparisonCard({
  title,
  baseline,
  scenario,
  change,
  suffix = "",
  currency = false,
  bg,
}) {
  const numericChange = Number(change) || 0;

  let changeText = "";

  if (currency) {
    changeText = formatCurrency(numericChange);
  } else {
    changeText =
      (numericChange > 0 ? "+" : "") +
      numericChange.toFixed(2) +
      suffix;
  }

  return (
    <div className={`rounded-2xl ${bg} p-5`}>
      <p className="text-sm font-semibold text-[#263A32]">{title}</p>

      <div className="mt-4 grid grid-cols-2 gap-3">
        <div className="rounded-xl bg-white/60 p-4">
          <p className="text-xs text-[#64746D]">Baseline</p>

          <p className="mt-1 text-sm font-bold text-[#263A32]">
            {baseline}
          </p>
        </div>

        <div className="rounded-xl bg-white/80 p-4">
          <p className="text-xs text-[#64746D]">Scenario</p>

          <p className="mt-1 text-sm font-bold text-[#263A32]">
            {scenario}
          </p>
        </div>
      </div>

      <p className="mt-4 text-sm font-bold text-[#263A32]">
        Change: {changeText}
      </p>
    </div>
  );
}

function formatSigned(value, suffix) {
  const number = Number(value) || 0;

  return `${number > 0 ? "+" : ""}${number}${suffix}`;
}

function formatCurrency(value) {
  const number = Number(value) || 0;

  return `₹${Math.round(number).toLocaleString("en-IN")}`;
}

export default WhatIfSimulator;