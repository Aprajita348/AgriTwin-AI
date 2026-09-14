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
      setError(
        "Run AI Farm Analysis first so AgriTwin has a baseline."
      );
      return;
    }

    setLoading(true);
    setError("");

    try {
      const data = await runWhatIfSimulation({
        crop: result.recommended_crop.crop,

        farm_size_acres:
          formData.farm_size_acres,

        baseline_yield_kg_per_ha:
          result.recommended_crop
            .predicted_yield_kg_per_ha,

        baseline_profit:
          result.recommended_crop
            .estimated_profit,

        baseline_water_liters:
          result.water_analysis
            .available_water_liters,

        baseline_sustainability_score:
          result.sustainability
            .sustainability_score,

        avg_temp_c:
          formData.avg_temp_c,

        rainfall_mm:
          formData.rainfall_mm,

        temperature_change:
          temperatureChange,

        rainfall_change_percent:
          rainfallChange,

        irrigation_change_percent:
          irrigationChange,

        fertilizer_change_percent:
          fertilizerChange,
      });

      setSimulation(data);

    } catch (err) {

      console.error(err);

      setError(
        "Could not run the simulation. Make sure the backend is running."
      );

    } finally {

      setLoading(false);

    }
  }

  return (
    <section>

      {/* =====================================================
          HERO
      ====================================================== */}

      <div className="mb-8">

        <span className="rounded-full bg-[#A8DADC] px-3 py-1 text-xs font-semibold">
          Digital Farm Simulator
        </span>

        <h2 className="mt-4 text-4xl font-bold tracking-tight md:text-5xl">
          What happens if you change the decision? 🌱
        </h2>

        <p className="mt-3 max-w-2xl text-sm leading-7 text-[#64746D]">
          Test a farming decision virtually before taking it to the
          field. Compare the scenario against your current baseline.
        </p>

      </div>


      {/* =====================================================
          NO BASELINE WARNING
      ====================================================== */}

      {!result && (
        <div className="mb-6 rounded-3xl bg-[#F6E7A1] p-5 text-sm font-medium">
          Run AI Farm Analysis first to create your baseline farm
          condition.
        </div>
      )}


      {/* =====================================================
          SCENARIO + BASELINE
      ====================================================== */}

      <div className="grid gap-6 lg:grid-cols-2">

        {/* Scenario controls */}

        <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-[#DDE7DD]">

          <h3 className="text-xl font-bold">
            Change your scenario
          </h3>

          <p className="mt-2 text-sm text-[#64746D]">
            Adjust one or more conditions and simulate the outcome.
          </p>

          <div className="mt-6 space-y-6">

            <ScenarioControl
              label="Temperature"
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
            onClick={handleSimulation}
            disabled={loading || !result}
            className="mt-8 w-full rounded-2xl bg-[#263A32] px-6 py-4 text-sm font-bold text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading
              ? "Running simulation..."
              : "Run Digital Farm Simulation →"}
          </button>


          {error && (
            <div className="mt-4 rounded-2xl bg-[#F3B5A4] p-4 text-sm">
              {error}
            </div>
          )}

        </div>


        {/* Baseline */}

        <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-[#DDE7DD]">

          <span className="rounded-full bg-[#CDE8D2] px-3 py-1 text-xs font-semibold">
            Current Baseline
          </span>

          <h3 className="mt-4 text-2xl font-bold">
            {result?.recommended_crop?.crop || "—"}
          </h3>


          {result ? (

            <div className="mt-6 space-y-4">

              <ComparisonRow
                label="Yield"
                value={`${result.recommended_crop.predicted_yield_kg_per_ha} kg/ha`}
              />

              <ComparisonRow
                label="Profit"
                value={formatCurrency(
                  result.recommended_crop.estimated_profit
                )}
              />

              <ComparisonRow
                label="Water"
                value={`${Math.round(
                  result.water_analysis
                    .available_water_liters
                ).toLocaleString("en-IN")} L`}
              />

              <ComparisonRow
                label="Sustainability"
                value={`${result.sustainability.sustainability_score}/100`}
              />

            </div>

          ) : (

            <p className="mt-4 text-sm text-[#64746D]">
              Baseline will appear here after farm analysis.
            </p>

          )}

        </div>

      </div>


      {/* =====================================================
          SIMULATION RESULT
      ====================================================== */}

      {simulation && (

        <section className="mt-8">

          <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-[#DDE7DD]">

            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">

              <div>

                <span className="rounded-full bg-[#A8DADC] px-3 py-1 text-xs font-semibold">
                  Simulation Result
                </span>

                <h3 className="mt-3 text-2xl font-bold">
                  Baseline vs Scenario
                </h3>

              </div>

              <span className="rounded-full bg-[#F7F4E9] px-4 py-2 text-sm font-bold">
                {simulation.climate_risk.risk_level} climate risk
              </span>

            </div>


            {/* Results */}

            <div className="mt-6 grid gap-4 md:grid-cols-3">

              <ComparisonCard
                title="Yield"
                baseline={`${simulation.baseline.yield_kg_per_ha} kg/ha`}
                scenario={`${simulation.scenario_result.yield_kg_per_ha} kg/ha`}
                change={
                  simulation.change
                    .yield_change_kg_per_ha
                }
                suffix=" kg/ha"
                bg="bg-[#CDE8D2]"
              />

              <ComparisonCard
                title="Profit"
                baseline={formatCurrency(
                  simulation.baseline.profit
                )}
                scenario={formatCurrency(
                  simulation.scenario_result.profit
                )}
                change={
                  simulation.change.profit_change
                }
                currency
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
                change={
                  simulation.change.water_change_liters
                }
                suffix=" L"
                bg="bg-[#A8DADC]"
              />

            </div>


            <div className="mt-4">

              <ComparisonCard
                title="Sustainability"
                baseline={`${simulation.baseline.sustainability_score}`}
                scenario={`${simulation.scenario_result.sustainability_score}`}
                change={
                  simulation.change
                    .sustainability_change
                }
                suffix=""
                bg="bg-[#CDE8D2]"
              />

            </div>


            {/* Climate */}

            <div className="mt-6 rounded-2xl bg-[#F7F4E9] p-5">

              <p className="text-xs font-semibold uppercase tracking-wide text-[#64746D]">
                Climate Impact
              </p>

              <p className="mt-2 text-sm leading-6">
                {simulation.climate_risk.recommendation}
              </p>


              <div className="mt-4 flex flex-wrap gap-2">

                {simulation.climate_risk.drivers.map(
                  (driver) => (
                    <span
                      key={driver}
                      className="rounded-full bg-white px-3 py-2 text-xs"
                    >
                      {driver}
                    </span>
                  )
                )}

              </div>

            </div>


            {/* Decision */}

            <div className="mt-6 rounded-2xl bg-[#F3B5A4] p-5">

              <p className="text-xs font-semibold uppercase tracking-wide">
                AgriTwin Decision
              </p>

              <p className="mt-2 text-sm font-medium leading-6">
                {simulation.decision}
              </p>

            </div>

          </div>

        </section>

      )}

    </section>
  );
}


/* ============================================================
   SCENARIO CONTROL
============================================================ */

function ScenarioControl({
  label,
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

      <div className="flex items-center justify-between">

        <label className="text-sm font-semibold">
          {label}
        </label>

        <span
          className={`rounded-xl ${color} px-3 py-1 text-sm font-bold`}
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
        onChange={(event) =>
          onChange(
            Number(event.target.value)
          )
        }
        className="mt-4 w-full accent-[#A8C3A0]"
      />


      <div className="mt-1 flex justify-between text-xs text-[#64746D]">

        <span>
          {min > 0 ? "+" : ""}
          {min}
          {suffix}
        </span>

        <span>
          Baseline
        </span>

        <span>
          {max > 0 ? "+" : ""}
          {max}
          {suffix}
        </span>

      </div>

    </div>
  );
}


/* ============================================================
   COMPARISON ROW
============================================================ */

function ComparisonRow({
  label,
  value,
}) {

  return (
    <div className="flex items-center justify-between rounded-2xl bg-[#F7F4E9] p-4">

      <span className="text-sm text-[#64746D]">
        {label}
      </span>

      <span className="text-sm font-bold">
        {value}
      </span>

    </div>
  );
}


/* ============================================================
   COMPARISON CARD
============================================================ */

function ComparisonCard({
  title,
  baseline,
  scenario,
  change,
  suffix,
  currency = false,
  bg,
}) {

  return (
    <div className={`rounded-2xl ${bg} p-5`}>

      <p className="text-sm font-semibold">
        {title}
      </p>


      <div className="mt-4 grid grid-cols-2 gap-3">

        <div className="rounded-xl bg-white/60 p-3">

          <p className="text-xs text-[#64746D]">
            Baseline
          </p>

          <p className="mt-1 text-sm font-bold">
            {baseline}
          </p>

        </div>


        <div className="rounded-xl bg-white/80 p-3">

          <p className="text-xs text-[#64746D]">
            Scenario
          </p>

          <p className="mt-1 text-sm font-bold">
            {scenario}
          </p>

        </div>

      </div>


      <p className="mt-4 text-sm font-bold">

        Change:{" "}

        {change > 0 ? "+" : ""}

        {currency
          ? formatCurrency(change)
          : `${Number(change).toFixed(2)}${suffix}`}

      </p>

    </div>
  );
}


/* ============================================================
   CURRENCY FORMATTER
============================================================ */

function formatCurrency(value) {
  return `₹${Math.round(value).toLocaleString("en-IN")}`;
}


export default WhatIfSimulator;