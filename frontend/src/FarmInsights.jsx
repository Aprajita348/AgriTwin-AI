import { useEffect, useState } from "react";
import {
  getCropCalendar,
  getEarlyWarnings,
} from "./services/api";

function FarmInsights({ result, formData }) {
  const [warnings, setWarnings] = useState(null);
  const [calendar, setCalendar] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadInsights() {
      if (!result) {
        setWarnings(null);
        setCalendar(null);
        return;
      }

      setLoading(true);
      setError("");
      setWarnings(null);
      setCalendar(null);

      try {
        const crop = result.recommended_crop.crop;

        const [warningData, calendarData] =
          await Promise.all([
            getEarlyWarnings({
              crop,
              avg_temp_c: formData.avg_temp_c,
              rainfall_mm: formData.rainfall_mm,
              available_water_liters:
                formData.available_water_liters,
              farm_size_acres:
                formData.farm_size_acres,
              nitrogen: formData.nitrogen,
              phosphorus: formData.phosphorus,
              potassium: formData.potassium,
            }),

            getCropCalendar(crop),
          ]);

        setWarnings(warningData);
        setCalendar(calendarData);

      } catch (err) {
        console.error(err);

        setError(
          "Could not load farm insights. Please make sure the backend is running."
        );
      } finally {
        setLoading(false);
      }
    }

    loadInsights();
  }, [result, formData]);

  /* =========================================================
     NO ANALYSIS YET
  ========================================================= */

  if (!result) {
    return (
      <section>
        <div className="rounded-3xl bg-[#F6E7A1] p-6">
          <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold">
            Farm Insights
          </span>

          <h2 className="mt-4 text-3xl font-bold">
            Understand your farm before you act. 🌿
          </h2>

          <p className="mt-3 max-w-2xl text-sm leading-6">
            Run AI Farm Analysis first to generate early warnings,
            crop calendar and sustainability insights.
          </p>
        </div>
      </section>
    );
  }

  /* =========================================================
     ERROR STATE
  ========================================================= */

  if (error) {
    return (
      <section>
        <div className="rounded-3xl bg-[#F3B5A4] p-6">
          <span className="text-xs font-semibold uppercase tracking-wide">
            Farm Insights
          </span>

          <h2 className="mt-3 text-2xl font-bold">
            Something went wrong
          </h2>

          <p className="mt-2 text-sm leading-6">
            {error}
          </p>
        </div>
      </section>
    );
  }

  /* =========================================================
     LOADING / DATA NOT READY
  ========================================================= */

  if (loading || !warnings || !calendar) {
    return (
      <section>
        <div className="rounded-3xl bg-white p-10 text-center shadow-sm ring-1 ring-[#DDE7DD]">
          <div className="text-4xl">🌱</div>

          <h2 className="mt-4 text-2xl font-bold">
            Loading farm insights...
          </h2>

          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-[#64746D]">
            AgriTwin is checking weather conditions, crop timing,
            early warnings and sustainability indicators.
          </p>

          <div className="mx-auto mt-6 h-2 max-w-xs overflow-hidden rounded-full bg-[#EEF2ED]">
            <div className="h-full w-2/3 animate-pulse rounded-full bg-[#A8C3A0]" />
          </div>
        </div>
      </section>
    );
  }

  const sustainability =
    result.sustainability;

  const recommendedCrop =
    result.recommended_crop.crop;

  return (
    <section>
      {/* =====================================================
          HERO
      ====================================================== */}

      <div className="mb-8">
        <span className="rounded-full bg-[#CDE8D2] px-3 py-1 text-xs font-semibold">
          Farm Intelligence
        </span>

        <h2 className="mt-4 text-4xl font-bold tracking-tight md:text-5xl">
          Understand your farm before you act. 🌿
        </h2>

        <p className="mt-3 max-w-2xl text-sm leading-7 text-[#64746D]">
          AgriTwin combines crop timing, early warnings and
          sustainability indicators to help you plan the next step.
        </p>
      </div>

      {/* =====================================================
          EARLY WARNING
      ====================================================== */}

      <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-[#DDE7DD]">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <span className="rounded-full bg-[#F3B5A4] px-3 py-1 text-xs font-semibold">
              Early Warning System
            </span>

            <h3 className="mt-3 text-2xl font-bold">
              {recommendedCrop} risk monitor
            </h3>

            <p className="mt-1 text-sm text-[#64746D]">
              Current environmental and soil alerts for your recommended crop.
            </p>
          </div>

          <div
            className={`rounded-full px-4 py-2 text-xs font-bold ${
              warnings.overall_alert === "High"
                ? "bg-[#F3B5A4]"
                : warnings.overall_alert === "Moderate"
                ? "bg-[#F6E7A1]"
                : "bg-[#CDE8D2]"
            }`}
          >
            {warnings.overall_alert} alert
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {warnings.warnings.map(
            (warning, index) => (
              <div
                key={`${warning.type}-${index}`}
                className="rounded-2xl bg-[#F7F4E9] p-5"
              >
                <div className="flex items-center justify-between gap-3">
                  <h4 className="font-bold">
                    {warning.type}
                  </h4>

                  <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${
                      warning.severity === "High"
                        ? "bg-[#F3B5A4]"
                        : warning.severity === "Moderate"
                        ? "bg-[#F6E7A1]"
                        : "bg-[#CDE8D2]"
                    }`}
                  >
                    {warning.severity}
                  </span>
                </div>

                <p className="mt-3 text-sm leading-6 text-[#64746D]">
                  {warning.message}
                </p>
              </div>
            )
          )}
        </div>
      </div>

      {/* =====================================================
          CROP CALENDAR
      ====================================================== */}

      <div className="mt-6 rounded-3xl bg-white p-6 shadow-sm ring-1 ring-[#DDE7DD]">
        <div>
          <span className="rounded-full bg-[#A8DADC] px-3 py-1 text-xs font-semibold">
            AI Crop Calendar
          </span>

          <h3 className="mt-3 text-2xl font-bold">
            {calendar.crop}
          </h3>

          <p className="mt-1 text-sm text-[#64746D]">
            Suggested crop-cycle phases for planning.
          </p>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-4">
          <CalendarCard
            phase="Sowing"
            value={calendar.calendar.sowing}
            bg="bg-[#CDE8D2]"
          />

          <CalendarCard
            phase="Vegetative"
            value={calendar.calendar.vegetative}
            bg="bg-[#A8DADC]"
          />

          <CalendarCard
            phase="Flowering"
            value={calendar.calendar.flowering}
            bg="bg-[#F6E7A1]"
          />

          <CalendarCard
            phase="Harvest"
            value={calendar.calendar.harvest}
            bg="bg-[#F3B5A4]"
          />
        </div>
      </div>

      {/* =====================================================
          SUSTAINABILITY ANALYTICS
      ====================================================== */}

      <div className="mt-6 rounded-3xl bg-white p-6 shadow-sm ring-1 ring-[#DDE7DD]">
        <div>
          <span className="rounded-full bg-[#F6E7A1] px-3 py-1 text-xs font-semibold">
            Sustainability Analytics
          </span>

          <h3 className="mt-3 text-2xl font-bold">
            Farm sustainability breakdown
          </h3>

          <p className="mt-1 text-sm text-[#64746D]">
            See which parts of your farming strategy contribute to sustainability.
          </p>
        </div>

        <div className="mt-6 grid gap-5 md:grid-cols-2">
          <ScoreBar
            label="Water efficiency"
            value={sustainability.water_score}
            bg="bg-[#A8DADC]"
          />

          <ScoreBar
            label="Fertilizer efficiency"
            value={sustainability.fertilizer_score}
            bg="bg-[#F6E7A1]"
          />

          <ScoreBar
            label="Soil health"
            value={sustainability.soil_health_score}
            bg="bg-[#CDE8D2]"
          />

          <ScoreBar
            label="Irrigation efficiency"
            value={
              sustainability.irrigation_efficiency_score
            }
            bg="bg-[#A8DADC]"
          />

          <ScoreBar
            label="Crop rotation"
            value={
              sustainability.crop_rotation_score
            }
            bg="bg-[#CDE8D2]"
          />

          <ScoreBar
            label="Profit contribution"
            value={sustainability.profit_score}
            bg="bg-[#F6E7A1]"
          />
        </div>

        <div className="mt-6 rounded-2xl bg-[#CDE8D2] p-5">
          <p className="text-xs font-semibold uppercase tracking-wide">
            Overall Sustainability
          </p>

          <p className="mt-1 text-3xl font-bold">
            {sustainability.sustainability_score}/100
          </p>

          <p className="mt-1 text-sm font-medium">
            {sustainability.sustainability_level}
          </p>
        </div>
      </div>
    </section>
  );
}


/* ============================================================
   CALENDAR CARD
============================================================ */

function CalendarCard({
  phase,
  value,
  bg,
}) {
  return (
    <div className={`rounded-2xl ${bg} p-5`}>
      <p className="text-xs font-semibold uppercase tracking-wide text-[#64746D]">
        {phase}
      </p>

      <p className="mt-3 text-sm font-bold leading-6">
        {value}
      </p>
    </div>
  );
}


/* ============================================================
   SCORE BAR
============================================================ */

function ScoreBar({
  label,
  value,
  bg,
}) {
  const safeValue = Math.max(
    0,
    Math.min(100, Number(value) || 0)
  );

  return (
    <div>
      <div className="flex items-center justify-between text-sm">
        <span className="font-semibold">
          {label}
        </span>

        <span className="font-bold">
          {safeValue}
        </span>
      </div>

      <div className="mt-2 h-3 overflow-hidden rounded-full bg-[#EEF2ED]">
        <div
          className={`h-full rounded-full ${bg}`}
          style={{
            width: `${safeValue}%`,
          }}
        />
      </div>
    </div>
  );
}


export default FarmInsights;