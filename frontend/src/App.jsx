import { useState } from "react";
import { runDecisionPipeline } from "./services/api";
import WhatIfSimulator from "./WhatIfSimulator";
import FarmInsights from "./FarmInsights";
import DecisionHistory, {
  saveDecisionToHistory,
} from "./DecisionHistory";

const initialFormData = {
  district_code: 63,
  state_code: 20,
  year: 2026,
  district: "Adilabad",
  state_name: "Telangana",
  area_1000_ha: 30.5,

  farm_size_acres: 5,
  previous_crop: "MAIZE",

  nitrogen: 240,
  phosphorus: 45,
  potassium: 180,
  ph: 6.8,
  organic_matter: 3.2,

  available_water_liters: 50000,
  irrigation_type: "Drip",

  rainfall_mm: 1106.23,
  avg_temp_c: 27.4,
  max_temp_c: 33.47,
  min_temp_c: 21.33,
};

function App() {
  const [formData, setFormData] = useState(initialFormData);

  const [result, setResult] = useState(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [activeView, setActiveView] = useState("dashboard");

  function handleChange(event) {
    const { name, value } = event.target;

    const numericFields = [
      "district_code",
      "state_code",
      "year",
      "area_1000_ha",
      "farm_size_acres",
      "nitrogen",
      "phosphorus",
      "potassium",
      "ph",
      "organic_matter",
      "available_water_liters",
      "rainfall_mm",
      "avg_temp_c",
      "max_temp_c",
      "min_temp_c",
    ];

    setFormData((previous) => ({
      ...previous,
      [name]: numericFields.includes(name)
        ? Number(value)
        : value,
    }));
  }

  async function handleAnalyze(event) {
    event.preventDefault();

    setLoading(true);
    setError("");

    try {
      const data = await runDecisionPipeline(formData);

      setResult(data);

      saveDecisionToHistory(data);

      setActiveView("dashboard");
    } catch (err) {
      console.error(err);

      setError(
        "Could not connect to the AgriTwin AI backend. Make sure the FastAPI server is running."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#F7F4E9] text-[#263A32]">

      {/* ====================================================
          HEADER
      ===================================================== */}

      <header className="border-b border-[#DDE7DD] bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">

          {/* Logo */}
          <button
            onClick={() => setActiveView("dashboard")}
            className="flex items-center gap-3"
          >
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#CDE8D2] text-xl">
              🌱
            </div>

            <div className="text-left">
              <h1 className="text-lg font-bold">
                AgriTwin AI
              </h1>

              <p className="text-xs text-[#64746D]">
                Sustainable farming decision intelligence
              </p>
            </div>
          </button>

          {/* Navigation */}
          <div className="hidden items-center gap-2 md:flex">

            <NavButton
              active={activeView === "dashboard"}
              onClick={() =>
                setActiveView("dashboard")
              }
              label="Dashboard"
              activeClass="bg-[#CDE8D2]"
            />

            <NavButton
              active={activeView === "what-if"}
              onClick={() =>
                setActiveView("what-if")
              }
              label="What-If Simulator"
              activeClass="bg-[#A8DADC]"
            />

            <NavButton
              active={activeView === "insights"}
              onClick={() =>
                setActiveView("insights")
              }
              label="Farm Insights"
              activeClass="bg-[#CDE8D2]"
            />

            <NavButton
              active={activeView === "history"}
              onClick={() =>
                setActiveView("history")
              }
              label="History"
              activeClass="bg-[#F6E7A1]"
            />

            <span className="ml-1 rounded-full bg-[#A8DADC] px-4 py-2 text-xs font-semibold">
              AI Farm Intelligence
            </span>

          </div>

        </div>
      </header>


      {/* ====================================================
          MAIN
      ===================================================== */}

      <main className="mx-auto max-w-7xl px-6 py-10">

        {/* ==================================================
            WHAT-IF PAGE
        =================================================== */}

        {activeView === "what-if" && (
          <WhatIfSimulator
            result={result}
            formData={formData}
          />
        )}


        {/* ==================================================
            FARM INSIGHTS PAGE
        =================================================== */}

        {activeView === "insights" && (
          <FarmInsights
            result={result}
            formData={formData}
          />
        )}


        {/* ==================================================
            HISTORY PAGE
        =================================================== */}

        {activeView === "history" && (
          <DecisionHistory />
        )}


        {/* ==================================================
            DASHBOARD PAGE
        =================================================== */}

        {activeView === "dashboard" && (
          <DashboardPage
            formData={formData}
            result={result}
            loading={loading}
            error={error}
            handleChange={handleChange}
            handleAnalyze={handleAnalyze}
          />
        )}

      </main>
    </div>
  );
}


/* ============================================================
   DASHBOARD PAGE
============================================================ */

function DashboardPage({
  formData,
  result,
  loading,
  error,
  handleChange,
  handleAnalyze,
}) {
  return (
    <>
      {/* ==================================================
          HERO
      =================================================== */}

      <section className="mb-10">

        <p className="text-sm font-semibold text-[#64746D]">
          AgriTwin AI
        </p>

        <h2 className="mt-2 text-4xl font-bold tracking-tight md:text-5xl">
          Make smarter farming decisions. 🌾
        </h2>

        <p className="mt-4 max-w-2xl text-sm leading-7 text-[#64746D]">
          Simulate choices, predict outcomes, compare crops
          and understand the impact of every farming decision.
        </p>

      </section>


      {/* ==================================================
          FARM ANALYSIS FORM
      =================================================== */}

      <form
        onSubmit={handleAnalyze}
        className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-[#DDE7DD]"
      >

        <div className="mb-6">

          <p className="text-xs font-semibold uppercase tracking-wide text-[#64746D]">
            Farm Analysis
          </p>

          <h3 className="mt-1 text-2xl font-bold">
            Farm & environmental conditions
          </h3>

        </div>


        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">

          <InputField
            label="Farm size (acres)"
            name="farm_size_acres"
            value={formData.farm_size_acres}
            onChange={handleChange}
            type="number"
            step="0.1"
          />

          <InputField
            label="Previous crop"
            name="previous_crop"
            value={formData.previous_crop}
            onChange={handleChange}
          />

          <InputField
            label="District"
            name="district"
            value={formData.district}
            onChange={handleChange}
          />

          <InputField
            label="State"
            name="state_name"
            value={formData.state_name}
            onChange={handleChange}
          />

          <InputField
            label="Nitrogen"
            name="nitrogen"
            value={formData.nitrogen}
            onChange={handleChange}
            type="number"
          />

          <InputField
            label="Phosphorus"
            name="phosphorus"
            value={formData.phosphorus}
            onChange={handleChange}
            type="number"
          />

          <InputField
            label="Potassium"
            name="potassium"
            value={formData.potassium}
            onChange={handleChange}
            type="number"
          />

          <InputField
            label="Soil pH"
            name="ph"
            value={formData.ph}
            onChange={handleChange}
            type="number"
            step="0.1"
          />

          <InputField
            label="Organic matter"
            name="organic_matter"
            value={formData.organic_matter}
            onChange={handleChange}
            type="number"
            step="0.1"
          />

          <InputField
            label="Available water (L)"
            name="available_water_liters"
            value={formData.available_water_liters}
            onChange={handleChange}
            type="number"
          />

          <SelectField
            label="Irrigation"
            name="irrigation_type"
            value={formData.irrigation_type}
            onChange={handleChange}
            options={[
              "Drip",
              "Sprinkler",
              "Flood",
            ]}
          />

          <InputField
            label="Rainfall (mm)"
            name="rainfall_mm"
            value={formData.rainfall_mm}
            onChange={handleChange}
            type="number"
            step="0.01"
          />

          <InputField
            label="Average temperature (°C)"
            name="avg_temp_c"
            value={formData.avg_temp_c}
            onChange={handleChange}
            type="number"
            step="0.01"
          />

          <InputField
            label="Maximum temperature (°C)"
            name="max_temp_c"
            value={formData.max_temp_c}
            onChange={handleChange}
            type="number"
            step="0.01"
          />

          <InputField
            label="Minimum temperature (°C)"
            name="min_temp_c"
            value={formData.min_temp_c}
            onChange={handleChange}
            type="number"
            step="0.01"
          />

        </div>


        <button
          type="submit"
          disabled={loading}
          className="mt-6 w-full rounded-2xl bg-[#A8C3A0] px-6 py-4 text-sm font-bold transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading
            ? "Analysing your farm..."
            : "Run AI Farm Analysis →"}
        </button>

      </form>


      {/* ==================================================
          ERROR
      =================================================== */}

      {error && (
        <div className="mt-6 rounded-2xl bg-[#F3B5A4] p-4 text-sm font-medium">
          {error}
        </div>
      )}


      {/* ==================================================
          RESULTS
      =================================================== */}

      {result && (
        <DashboardResult result={result} />
      )}
    </>
  );
}


/* ============================================================
   DASHBOARD RESULTS
============================================================ */

function DashboardResult({ result }) {
  const crop = result.recommended_crop;
  const sustainability = result.sustainability;
  const climate = result.climate_analysis;
  const water = result.water_analysis;
  const fertilizer = result.fertilizer_analysis;
  const advisor = result.advisor;
  const explanation = result.explanation;

  return (
    <section className="mt-10">

      {/* ==================================================
          TITLE
      =================================================== */}

      <div className="mb-6">

        <p className="text-sm font-semibold text-[#64746D]">
          AI Analysis Complete
        </p>

        <h2 className="mt-1 text-3xl font-bold">
          Your farm intelligence overview
        </h2>

      </div>


      {/* ==================================================
          KPI CARDS
      =================================================== */}

      <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">

        <MetricCard
          title="Recommended Crop"
          value={crop.crop}
          label={`${crop.decision_score}% decision score`}
          bg="bg-[#CDE8D2]"
        />

        <MetricCard
          title="Predicted Yield"
          value={`${crop.predicted_yield_kg_per_ha} kg/ha`}
          label="XGBoost prediction"
          bg="bg-[#A8DADC]"
        />

        <MetricCard
          title="Estimated Profit"
          value={formatCurrency(crop.estimated_profit)}
          label={`${formatCurrency(
            crop.estimated_profit_per_acre
          )}/acre`}
          bg="bg-[#F6E7A1]"
        />

        <MetricCard
          title="Sustainability"
          value={`${sustainability.sustainability_score}/100`}
          label={sustainability.sustainability_level}
          bg="bg-[#CDE8D2]"
        />

      </div>


      {/* ==================================================
          RECOMMENDATION + STATUS
      =================================================== */}

      <div className="mt-6 grid gap-6 lg:grid-cols-[1.4fr_1fr]">

        <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-[#DDE7DD]">

          <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">

            <div>

              <span className="rounded-full bg-[#CDE8D2] px-3 py-1 text-xs font-semibold">
                AI Recommendation
              </span>

              <h3 className="mt-4 text-4xl font-bold">
                {crop.crop}
              </h3>

              <p className="mt-3 max-w-2xl text-sm leading-6 text-[#64746D]">
                {result.final_recommendation}
              </p>

            </div>


            <div className="rounded-2xl bg-[#F7F4E9] p-5 sm:min-w-40">

              <p className="text-xs text-[#64746D]">
                Decision Score
              </p>

              <p className="mt-1 text-3xl font-bold">
                {crop.decision_score}%
              </p>

            </div>

          </div>


          <div className="mt-6 grid gap-4 sm:grid-cols-3">

            <InfoCard
              title="Expected Yield"
              value={`${crop.predicted_yield_kg_per_ha} kg/ha`}
              bg="bg-[#F7F4E9]"
            />

            <InfoCard
              title="Estimated Profit"
              value={formatCurrency(
                crop.estimated_profit
              )}
              bg="bg-[#CDE8D2]"
            />

            <InfoCard
              title="Climate Risk"
              value={`${climate.climate_risk} · ${climate.risk_level}`}
              bg="bg-[#A8DADC]"
            />

          </div>

        </div>


        <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-[#DDE7DD]">

          <h3 className="text-xl font-bold">
            Farm Status
          </h3>

          <div className="mt-5 space-y-4">

            <StatusRow
              label="Water coverage"
              value={`${water.water_coverage_percent}%`}
              tone="mint"
            />

            <StatusRow
              label="Fertilizer priority"
              value={fertilizer.fertilizer_priority}
              tone="yellow"
            />

            <StatusRow
              label="Climate risk"
              value={`${climate.climate_risk} · ${climate.risk_level}`}
              tone="teal"
            />

            <StatusRow
              label="Soil health"
              value={sustainability.soil_health_score}
              tone="mint"
            />

            <StatusRow
              label="Irrigation efficiency"
              value={
                sustainability.irrigation_efficiency_score
              }
              tone="teal"
            />

          </div>

        </div>

      </div>


      {/* ==================================================
          EXPLAINABLE AI
      =================================================== */}

      <div className="mt-6 rounded-3xl bg-white p-6 shadow-sm ring-1 ring-[#DDE7DD]">

        <div className="flex items-start justify-between gap-4">

          <div>

            <h3 className="text-xl font-bold">
              Why did AgriTwin choose {crop.crop}?
            </h3>

            <p className="mt-2 text-sm text-[#64746D]">
              Transparent explanation of the major decision factors.
            </p>

          </div>

          <div className="rounded-2xl bg-[#CDE8D2] px-4 py-2 text-sm font-bold">
            {explanation.factor_count.positive} positive
          </div>

        </div>


        <div className="mt-6 grid gap-3 md:grid-cols-2">

          {explanation.positive_factors.map(
            (factor, index) => (
              <div
                key={`positive-${index}`}
                className="rounded-2xl bg-[#CDE8D2] p-4 text-sm leading-6"
              >
                ✓ {factor}
              </div>
            )
          )}


          {explanation.neutral_factors.map(
            (factor, index) => (
              <div
                key={`neutral-${index}`}
                className="rounded-2xl bg-[#F7F4E9] p-4 text-sm leading-6"
              >
                • {factor}
              </div>
            )
          )}


          {explanation.negative_factors.map(
            (factor, index) => (
              <div
                key={`negative-${index}`}
                className="rounded-2xl bg-[#F3B5A4] p-4 text-sm leading-6"
              >
                ! {factor}
              </div>
            )
          )}

        </div>

      </div>


      {/* ==================================================
          ADVISOR
      =================================================== */}

      <div className="mt-6 rounded-3xl bg-white p-6 shadow-sm ring-1 ring-[#DDE7DD]">

        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

          <div>

            <span className="rounded-full bg-[#F6E7A1] px-3 py-1 text-xs font-semibold">
              Agricultural Advisor
            </span>

            <h3 className="mt-3 text-xl font-bold">
              What should you do next?
            </h3>

          </div>

          <div className="rounded-full bg-[#CDE8D2] px-4 py-2 text-xs font-bold">
            {advisor.overall_priority} priority
          </div>

        </div>


        <p className="mt-4 text-sm leading-6 text-[#64746D]">
          {advisor.advice}
        </p>


        <div className="mt-5 grid gap-3 md:grid-cols-2">

          {advisor.actions.map(
            (action, index) => (
              <div
                key={index}
                className="rounded-2xl bg-[#F7F4E9] p-4 text-sm leading-6"
              >
                {action}
              </div>
            )
          )}

        </div>

      </div>


      {/* ==================================================
          CROP COMPARISON
      =================================================== */}

      <div className="mt-6 rounded-3xl bg-white p-6 shadow-sm ring-1 ring-[#DDE7DD]">

        <div>

          <h3 className="text-xl font-bold">
            Crop Comparison
          </h3>

          <p className="mt-1 text-sm text-[#64746D]">
            Candidate crops evaluated using suitability,
            predicted yield and estimated profitability.
          </p>

        </div>


        <div className="mt-5 overflow-x-auto">

          <table className="w-full min-w-[700px] text-left text-sm">

            <thead>

              <tr className="border-b border-[#DDE7DD] text-[#64746D]">

                <th className="px-3 py-3">
                  Crop
                </th>

                <th className="px-3 py-3">
                  Yield
                </th>

                <th className="px-3 py-3">
                  Profit
                </th>

                <th className="px-3 py-3">
                  Suitability
                </th>

                <th className="px-3 py-3">
                  Decision
                </th>

              </tr>

            </thead>


            <tbody>

              {result.crop_comparison.map(
                (item, index) => (
                  <tr
                    key={item.crop}
                    className={
                      index === 0
                        ? "bg-[#CDE8D2]"
                        : "border-b border-[#EEF2ED]"
                    }
                  >

                    <td className="px-3 py-4 font-semibold">
                      {item.crop}
                    </td>

                    <td className="px-3 py-4">
                      {item.predicted_yield_kg_per_ha} kg/ha
                    </td>

                    <td className="px-3 py-4">
                      {formatCurrency(
                        item.estimated_profit
                      )}
                    </td>

                    <td className="px-3 py-4">
                      {item.score}%
                    </td>

                    <td className="px-3 py-4 font-bold">
                      {item.decision_score}%
                    </td>

                  </tr>
                )
              )}

            </tbody>

          </table>

        </div>

      </div>


      {/* ==================================================
          BOTTOM STATUS
      =================================================== */}

      <div className="mt-6 grid gap-5 md:grid-cols-3">

        <MetricCard
          title="Water"
          value={`${water.water_coverage_percent}%`}
          label={`${Math.round(
            water.available_water_liters
          ).toLocaleString("en-IN")} L available`}
          bg="bg-[#A8DADC]"
        />

        <MetricCard
          title="Climate"
          value={`${climate.climate_risk}`}
          label={climate.risk_level}
          bg="bg-[#CDE8D2]"
        />

        <MetricCard
          title="Fertilizer"
          value={fertilizer.fertilizer_priority}
          label={`Priority: ${fertilizer.priority_nutrient}`}
          bg="bg-[#F6E7A1]"
        />

      </div>

    </section>
  );
}


/* ============================================================
   NAV BUTTON
============================================================ */

function NavButton({
  active,
  onClick,
  label,
  activeClass,
}) {
  return (
    <button
      onClick={onClick}
      className={`rounded-xl px-4 py-2 text-xs font-semibold transition ${
        active
          ? activeClass
          : "hover:bg-[#F7F4E9]"
      }`}
    >
      {label}
    </button>
  );
}


/* ============================================================
   INPUT FIELD
============================================================ */

function InputField({
  label,
  name,
  value,
  onChange,
  type = "text",
  step,
}) {
  return (
    <label className="block">

      <span className="mb-2 block text-xs font-semibold text-[#64746D]">
        {label}
      </span>

      <input
        name={name}
        type={type}
        step={step}
        value={value}
        onChange={onChange}
        className="w-full rounded-2xl border border-[#DDE7DD] bg-[#F7F4E9] px-4 py-3 text-sm outline-none transition focus:border-[#A8C3A0] focus:ring-2 focus:ring-[#CDE8D2]"
      />

    </label>
  );
}


/* ============================================================
   SELECT FIELD
============================================================ */

function SelectField({
  label,
  name,
  value,
  onChange,
  options,
}) {
  return (
    <label className="block">

      <span className="mb-2 block text-xs font-semibold text-[#64746D]">
        {label}
      </span>

      <select
        name={name}
        value={value}
        onChange={onChange}
        className="w-full rounded-2xl border border-[#DDE7DD] bg-[#F7F4E9] px-4 py-3 text-sm outline-none focus:border-[#A8C3A0] focus:ring-2 focus:ring-[#CDE8D2]"
      >

        {options.map((option) => (
          <option
            key={option}
            value={option}
          >
            {option}
          </option>
        ))}

      </select>

    </label>
  );
}


/* ============================================================
   METRIC CARD
============================================================ */

function MetricCard({
  title,
  value,
  label,
  bg,
}) {
  return (
    <div className={`rounded-3xl ${bg} p-5`}>

      <p className="text-sm font-medium text-[#64746D]">
        {title}
      </p>

      <p className="mt-3 text-2xl font-bold">
        {value}
      </p>

      {label && (
        <p className="mt-1 text-xs text-[#64746D]">
          {label}
        </p>
      )}

    </div>
  );
}


/* ============================================================
   INFO CARD
============================================================ */

function InfoCard({
  title,
  value,
  bg,
}) {
  return (
    <div className={`rounded-2xl ${bg} p-4`}>

      <p className="text-xs text-[#64746D]">
        {title}
      </p>

      <p className="mt-2 text-lg font-bold">
        {value}
      </p>

    </div>
  );
}


/* ============================================================
   STATUS ROW
============================================================ */

function StatusRow({
  label,
  value,
  tone,
}) {
  const tones = {
    mint: "bg-[#CDE8D2]",
    yellow: "bg-[#F6E7A1]",
    teal: "bg-[#A8DADC]",
  };

  return (
    <div className="flex items-center justify-between rounded-2xl bg-[#F7F4E9] p-4">

      <span className="text-sm text-[#64746D]">
        {label}
      </span>

      <span
        className={`rounded-xl px-3 py-2 text-sm font-bold ${tones[tone]}`}
      >
        {value}
      </span>

    </div>
  );
}


/* ============================================================
   CURRENCY
============================================================ */

function formatCurrency(value) {
  return `₹${Math.round(value).toLocaleString("en-IN")}`;
}


export default App;