import { useEffect, useMemo, useState } from "react";
import {
  createFarm,
  generateAgriculturalAdvice,
  getCurrentUser,
  getFarms,
  getLiveWeather,
  loginUser,
  registerUser,
  runDecisionPipeline,
} from "./services/api";

const TOKEN_KEY = "agritwin_access_token";
const USERNAME_KEY = "agritwin_username";
const FARM_ID_KEY = "agritwin_farm_id";

function LiveIntelligence({ result, formData }) {
  const [token, setToken] = useState(
    () => localStorage.getItem(TOKEN_KEY) || ""
  );

  const [username, setUsername] = useState(
    () => localStorage.getItem(USERNAME_KEY) || ""
  );

  const [farmId, setFarmId] = useState(
    () => localStorage.getItem(FARM_ID_KEY) || ""
  );

  const [authMode, setAuthMode] = useState("login");

  const [authForm, setAuthForm] = useState({
    username: "",
    email: "",
    password: "",
  });

  const [farmForm, setFarmForm] = useState({
    farm_name: "",
    latitude: "",
    longitude: "",
  });

  const [weather, setWeather] = useState(null);
  const [liveDecision, setLiveDecision] = useState(null);
  const [aiAdvice, setAiAdvice] = useState(null);

  const [authLoading, setAuthLoading] = useState(false);
  const [farmLoading, setFarmLoading] = useState(false);
  const [loading, setLoading] = useState("");
  const [error, setError] = useState("");

  const isAuthenticated = Boolean(token);

  const aiInput = useMemo(() => {
    if (!result) return null;

    return {
      crop: result.recommended_crop.crop,
      predicted_yield_kg_per_ha:
        result.recommended_crop.predicted_yield_kg_per_ha,

      water_coverage_percent:
        result.water_analysis.water_coverage_percent,

      fertilizer_priority:
        result.fertilizer_analysis.fertilizer_priority,

      sustainability_score:
        result.sustainability.sustainability_score,

      climate_risk:
        result.climate_analysis.climate_risk,

      recommended_water_liters:
        result.advisor?.recommended_water_liters ||
        result.water_analysis.available_water_liters,

      rainfall_mm: formData.rainfall_mm,
      avg_temp_c: formData.avg_temp_c,
      max_temp_c: formData.max_temp_c,
      min_temp_c: formData.min_temp_c,
      soil_ph: formData.ph,
      organic_matter: formData.organic_matter,
      language: "English",
    };
  }, [result, formData]);

  useEffect(() => {
    async function restoreSession() {
      if (!token) return;

      try {
        await getCurrentUser(token);

        const farms = await getFarms(token);

        if (!farmId && farms.length > 0) {
          selectFarm(farms[0].id);
        }
      } catch {
        clearSession();
      }
    }

    restoreSession();

    // Intentionally run only on initial mount.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function selectFarm(id) {
    const normalizedId = String(id);

    setFarmId(normalizedId);
    localStorage.setItem(FARM_ID_KEY, normalizedId);
  }

  function clearSession() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USERNAME_KEY);
    localStorage.removeItem(FARM_ID_KEY);

    setToken("");
    setUsername("");
    setFarmId("");
    setWeather(null);
    setLiveDecision(null);
    setAiAdvice(null);
    setError("");
  }

  function handleAuthChange(event) {
    const { name, value } = event.target;

    setAuthForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  async function handleAuthSubmit(event) {
    event.preventDefault();

    setAuthLoading(true);
    setError("");

    try {
      let loginData;

      if (authMode === "register") {
        await registerUser(authForm);

        loginData = await loginUser({
          username: authForm.username,
          password: authForm.password,
        });
      } else {
        loginData = await loginUser({
          username: authForm.username,
          password: authForm.password,
        });
      }

      localStorage.setItem(
        TOKEN_KEY,
        loginData.access_token
      );

      localStorage.setItem(
        USERNAME_KEY,
        authForm.username
      );

      setToken(loginData.access_token);
      setUsername(authForm.username);

      const farms = await getFarms(
        loginData.access_token
      );

      if (farms.length > 0) {
        selectFarm(farms[0].id);
      }

      setAuthForm({
        username: "",
        email: "",
        password: "",
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setAuthLoading(false);
    }
  }

  function handleFarmChange(event) {
    const { name, value } = event.target;

    setFarmForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  async function handleCreateFarm(event) {
    event.preventDefault();

    if (!token) {
      setError("Login first to create a farm.");
      return;
    }

    const latitude = Number(farmForm.latitude);
    const longitude = Number(farmForm.longitude);

    if (
      !Number.isFinite(latitude) ||
      !Number.isFinite(longitude)
    ) {
      setError(
        "Enter valid farm latitude and longitude."
      );
      return;
    }

    setFarmLoading(true);
    setError("");

    try {
      const farm = await createFarm(token, {
        farm_name:
          farmForm.farm_name ||
          `${formData.district} Farm`,

        farm_size_acres: Number(
          formData.farm_size_acres
        ),

        state: formData.state_name,
        district: formData.district,
        latitude,
        longitude,
      });

      selectFarm(farm.id);

      setWeather(null);
      setLiveDecision(null);
      setAiAdvice(null);

      setFarmForm({
        farm_name: "",
        latitude: "",
        longitude: "",
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setFarmLoading(false);
    }
  }

  async function loadWeather() {
    if (!token || !farmId) {
      setError(
        "Login and select/create a farm first."
      );
      return;
    }

    setLoading("weather");
    setError("");

    try {
      const data = await getLiveWeather(
        farmId,
        token
      );

      setWeather(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading("");
    }
  }

  async function generateAdvisor() {
    if (!aiInput) {
      setError(
        "Run AI Farm Analysis first to generate the advisor."
      );
      return;
    }

    setLoading("advisor");
    setError("");

    try {
      const data =
        await generateAgriculturalAdvice(aiInput);

      setAiAdvice(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading("");
    }
  }

  async function runLiveDecision() {
    if (!token || !farmId) {
      setError(
        "Login and create/select a farm before running live intelligence."
      );
      return;
    }

    setLoading("live-decision");
    setError("");
    setAiAdvice(null);

    const basePayload = {
      district_code: Number(
        formData.district_code
      ),

      state_code: Number(
        formData.state_code
      ),

      year: Number(formData.year),

      district: formData.district,
      state_name: formData.state_name,

      area_1000_ha: Number(
        formData.area_1000_ha
      ),

      farm_size_acres: Number(
        formData.farm_size_acres
      ),

      previous_crop: formData.previous_crop,

      nitrogen: Number(
        formData.nitrogen
      ),

      phosphorus: Number(
        formData.phosphorus
      ),

      potassium: Number(
        formData.potassium
      ),

      ph: Number(formData.ph),

      organic_matter: Number(
        formData.organic_matter
      ),

      available_water_liters: Number(
        formData.available_water_liters
      ),

      irrigation_type:
        formData.irrigation_type,

      rainfall_mm: Number(
        formData.rainfall_mm
      ),

      avg_temp_c: Number(
        formData.avg_temp_c
      ),

      max_temp_c: Number(
        formData.max_temp_c
      ),

      min_temp_c: Number(
        formData.min_temp_c
      ),
    };

    let liveWeatherData = weather;
    let usingLiveWeather = Boolean(weather);

    try {
      if (!liveWeatherData) {
        liveWeatherData = await getLiveWeather(
          farmId,
          token
        );

        setWeather(liveWeatherData);
      }
    } catch {
      liveWeatherData = null;
      usingLiveWeather = false;
    }

    const current =
      liveWeatherData?.current || {};

    const daily =
      liveWeatherData?.daily || {};

    const dailyMax = Array.isArray(
      daily.temperature_2m_max
    )
      ? daily.temperature_2m_max
      : [];

    const dailyMin = Array.isArray(
      daily.temperature_2m_min
    )
      ? daily.temperature_2m_min
      : [];

    const dailyRain = Array.isArray(
      daily.precipitation_sum
    )
      ? daily.precipitation_sum
      : [];

    const usedWeather = {
      rainfall_mm:
        dailyRain[0] ??
        current.precipitation ??
        basePayload.rainfall_mm,

      avg_temp_c:
        current.temperature_2m ??
        basePayload.avg_temp_c,

      max_temp_c:
        dailyMax[0] ??
        basePayload.max_temp_c,

      min_temp_c:
        dailyMin[0] ??
        basePayload.min_temp_c,
    };

    const decisionPayload = {
      ...basePayload,
      ...usedWeather,
    };

    try {
      const decision =
        await runDecisionPipeline(
          decisionPayload
        );

      const data = {
        farm: {
          id: Number(farmId),
        },

        live_weather: liveWeatherData,
        used_for_pipeline: usedWeather,
        decision,
      };

      setLiveDecision(data);

      const recommendedCrop =
        decision?.recommended_crop?.crop;

      const predictedYield =
        decision?.recommended_crop
          ?.predicted_yield_kg_per_ha;

      const waterCoverage =
        decision?.water_analysis
          ?.water_coverage_percent;

      const fertilizerPriority =
        decision?.fertilizer_analysis
          ?.fertilizer_priority;

      const sustainabilityScore =
        decision?.sustainability
          ?.sustainability_score;

      const climateRisk =
        decision?.climate_analysis
          ?.climate_risk;

      const recommendedWater =
        decision?.advisor
          ?.recommended_water_liters ??
        decision?.water_analysis
          ?.available_water_liters ??
        Number(
          formData.available_water_liters
        );

      const aiPayload = {
        crop: recommendedCrop,

        predicted_yield_kg_per_ha:
          predictedYield,

        water_coverage_percent:
          waterCoverage,

        fertilizer_priority:
          fertilizerPriority,

        sustainability_score:
          sustainabilityScore,

        climate_risk: climateRisk,

        recommended_water_liters:
          recommendedWater,

        rainfall_mm:
          usedWeather.rainfall_mm,

        avg_temp_c:
          usedWeather.avg_temp_c,

        max_temp_c:
          usedWeather.max_temp_c,

        min_temp_c:
          usedWeather.min_temp_c,

        soil_ph: Number(formData.ph),

        organic_matter: Number(
          formData.organic_matter
        ),

        language: "English",
      };

      try {
        const advice =
          await generateAgriculturalAdvice(
            aiPayload
          );

        setAiAdvice(advice);
      } catch {
        setAiAdvice({
          summary:
            usingLiveWeather
              ? "Decision generated successfully with the live weather feed."
              : "Decision generated successfully using the farm analysis weather inputs.",

          recommendation:
            `Continue with ${
              recommendedCrop ||
              "the recommended crop"
            } based on the current model output. Review farm conditions before implementation.`,

          reasons: [
            `The decision engine selected ${
              recommendedCrop ||
              "the recommended crop"
            } from the supplied farm conditions.`,

            `Predicted yield is ${
              predictedYield ?? "—"
            } kg/ha.`,

            `Water coverage is ${
              waterCoverage ?? "—"
            }%.`,

            `Nutrient availability indicates ${
              fertilizerPriority || "—"
            } fertilizer priority.`,

            `Climate-risk score is ${
              climateRisk ?? "—"
            }.`,

            `Rainfall used for this decision: ${
              usedWeather.rainfall_mm
            } mm.`,

            `Average/current temperature used: ${
              usedWeather.avg_temp_c
            } °C.`,
          ],

          expected_impact: [
            `Expected yield from the current model: ${
              predictedYield ?? "—"
            } kg/ha.`,

            `Sustainability score: ${
              sustainabilityScore ?? "—"
            }/100.`,

            `Climate-risk score: ${
              climateRisk ?? "—"
            }.`,

            `Recommended water planning value: ${
              recommendedWater ?? "—"
            } liters.`,
          ],

          warnings: [
            "Gemini AI provider is temporarily unavailable. A deterministic rule-based fallback advisor is being shown.",

            ...(usingLiveWeather
              ? []
              : [
                  "Live weather was unavailable, so the decision used the weather values already entered in the farm analysis form.",
                ]),
          ],

          next_steps: [
            "Review the live weather and farm inputs before taking action.",

            "Use the What-If simulator to compare irrigation, fertilizer and crop scenarios.",

            "Re-run the decision when weather or resource conditions change.",
          ],

          provider:
            "Rule-based fallback",
        });
      }
    } catch (err) {
      setError(
        err?.message ||
          "Unable to generate the farming decision."
      );
    } finally {
      setLoading("");
    }
  }

  return (
    <section className="mt-10 space-y-6">
      <div>
        <span className="rounded-full bg-[#A8DADC] px-3 py-1 text-xs font-semibold">
          Live Intelligence
        </span>

        <h2 className="mt-4 text-3xl font-bold">
          Connect AgriTwin to live farm data.
        </h2>

        <p className="mt-2 max-w-3xl text-sm leading-7 text-[#64746D]">
          Live weather can feed the decision engine,
          while Gemini turns structured model outputs
          into farmer-friendly explanations.
        </p>
      </div>

      {error && (
        <div className="rounded-2xl bg-[#F3B5A4] p-4 text-sm font-medium">
          {error}
        </div>
      )}

      {!isAuthenticated ? (
        <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-[#DDE7DD]">
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => setAuthMode("login")}
              className={`rounded-xl px-4 py-2 text-xs font-bold ${
                authMode === "login"
                  ? "bg-[#CDE8D2]"
                  : "bg-[#F7F4E9]"
              }`}
            >
              Login
            </button>

            <button
              type="button"
              onClick={() => setAuthMode("register")}
              className={`rounded-xl px-4 py-2 text-xs font-bold ${
                authMode === "register"
                  ? "bg-[#A8DADC]"
                  : "bg-[#F7F4E9]"
              }`}
            >
              Register
            </button>
          </div>

          <form
            onSubmit={handleAuthSubmit}
            className="mt-5 grid gap-4 md:grid-cols-3"
          >
            <input
              name="username"
              value={authForm.username}
              onChange={handleAuthChange}
              placeholder="Username"
              required
              minLength={3}
              className="rounded-2xl border border-[#DDE7DD] bg-[#F7F4E9] px-4 py-3 text-sm"
            />

            {authMode === "register" && (
              <input
                name="email"
                type="email"
                value={authForm.email}
                onChange={handleAuthChange}
                placeholder="Email"
                required
                className="rounded-2xl border border-[#DDE7DD] bg-[#F7F4E9] px-4 py-3 text-sm"
              />
            )}

            <input
              name="password"
              type="password"
              value={authForm.password}
              onChange={handleAuthChange}
              placeholder="Password (8+ chars)"
              required
              minLength={8}
              className="rounded-2xl border border-[#DDE7DD] bg-[#F7F4E9] px-4 py-3 text-sm"
            />

            <button
              type="submit"
              disabled={authLoading}
              className="rounded-2xl bg-[#263A32] px-5 py-3 text-sm font-bold text-white disabled:opacity-50 md:col-span-3"
            >
              {authLoading
                ? "Please wait..."
                : authMode === "register"
                ? "Create Account & Login"
                : "Login to Live Intelligence"}
            </button>
          </form>
        </div>
      ) : (
        <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-[#DDE7DD]">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-[#64746D]">
                Signed in
              </p>

              <p className="mt-1 text-lg font-bold">
                {username}
              </p>

              <p className="text-xs text-[#64746D]">
                {farmId
                  ? `Active farm #${farmId}`
                  : "No active farm"}
              </p>
            </div>

            <button
              type="button"
              onClick={clearSession}
              className="rounded-xl bg-[#F3B5A4] px-4 py-2 text-xs font-bold"
            >
              Logout
            </button>
          </div>

          <form
            onSubmit={handleCreateFarm}
            className="mt-6 grid gap-4 md:grid-cols-4"
          >
            <input
              name="farm_name"
              value={farmForm.farm_name}
              onChange={handleFarmChange}
              placeholder={`${formData.district} Farm`}
              className="rounded-2xl border border-[#DDE7DD] bg-[#F7F4E9] px-4 py-3 text-sm"
            />

            <input
              name="latitude"
              type="number"
              step="0.000001"
              value={farmForm.latitude}
              onChange={handleFarmChange}
              placeholder="Latitude"
              required={!farmId}
              className="rounded-2xl border border-[#DDE7DD] bg-[#F7F4E9] px-4 py-3 text-sm"
            />

            <input
              name="longitude"
              type="number"
              step="0.000001"
              value={farmForm.longitude}
              onChange={handleFarmChange}
              placeholder="Longitude"
              required={!farmId}
              className="rounded-2xl border border-[#DDE7DD] bg-[#F7F4E9] px-4 py-3 text-sm"
            />

            <button
              type="submit"
              disabled={farmLoading}
              className="rounded-2xl bg-[#CDE8D2] px-5 py-3 text-sm font-bold disabled:opacity-50"
            >
              {farmLoading
                ? "Saving..."
                : farmId
                ? "Create Another Farm"
                : "Create Farm"}
            </button>
          </form>

          <p className="mt-3 text-xs text-[#64746D]">
            Latitude/longitude are used only for live
            weather lookups. Use the coordinates of the
            farm you want to monitor.
          </p>

          <div className="mt-6 grid gap-3 md:grid-cols-3">
            <button
              type="button"
              onClick={loadWeather}
              disabled={loading !== ""}
              className="rounded-2xl bg-[#A8DADC] px-4 py-3 text-sm font-bold disabled:opacity-50"
            >
              {loading === "weather"
                ? "Loading..."
                : "Live Weather"}
            </button>

            <button
              type="button"
              onClick={runLiveDecision}
              disabled={loading !== ""}
              className="rounded-2xl bg-[#F6E7A1] px-4 py-3 text-sm font-bold disabled:opacity-50"
            >
              {loading === "live-decision"
                ? "Running..."
                : "Live Decision + AI"}
            </button>

            <button
              type="button"
              onClick={generateAdvisor}
              disabled={
                loading !== "" || !result
              }
              className="rounded-2xl bg-[#F3B5A4] px-4 py-3 text-sm font-bold disabled:opacity-50"
            >
              {loading === "advisor"
                ? "Generating..."
                : "AI Advisor"}
            </button>
          </div>
        </div>
      )}

      {weather && (
        <LiveWeatherCard weather={weather} />
      )}

      {liveDecision && (
        <LiveDecisionCard data={liveDecision} />
      )}

      {aiAdvice && (
        <AIAdviceCard advice={aiAdvice} />
      )}
    </section>
  );
}

function LiveWeatherCard({ weather }) {
  const current = weather.current || {};
  const daily = weather.daily || {};

  const maxTemp =
    daily.temperature_2m_max?.[0];

  const minTemp =
    daily.temperature_2m_min?.[0];

  const rainfall =
    daily.precipitation_sum?.[0];

  return (
    <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-[#DDE7DD]">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <span className="rounded-full bg-[#A8DADC] px-3 py-1 text-xs font-semibold">
            Open-Meteo
          </span>

          <h3 className="mt-3 text-2xl font-bold">
            Live Weather
          </h3>
        </div>

        <span className="text-xs font-semibold text-[#64746D]">
          {weather.timezone || "Auto timezone"}
        </span>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-4">
        <Metric
          title="Temperature"
          value={`${current.temperature_2m ?? "—"} °C`}
        />

        <Metric
          title="Humidity"
          value={`${current.relative_humidity_2m ?? "—"}%`}
        />

        <Metric
          title="Today max"
          value={`${maxTemp ?? "—"} °C`}
        />

        <Metric
          title="Rainfall"
          value={`${
            rainfall ??
            current.precipitation ??
            "—"
          } mm`}
        />
      </div>

      <p className="mt-4 text-xs text-[#64746D]">
        Provider coordinates:{" "}
        {weather.latitude}, {weather.longitude}
      </p>
    </div>
  );
}

function LiveDecisionCard({ data }) {
  const decision =
    data.decision?.recommended_crop;

  return (
    <div className="rounded-3xl bg-[#263A32] p-6 text-white shadow-sm">
      <span className="rounded-full bg-[#CDE8D2] px-3 py-1 text-xs font-semibold text-[#263A32]">
        Live Decision Pipeline
      </span>

      <h3 className="mt-4 text-2xl font-bold">
        {decision?.crop || "Live analysis"}
      </h3>

      <div className="mt-5 grid gap-4 md:grid-cols-4">
        <DarkMetric
          title="Decision score"
          value={`${
            decision?.decision_score ?? "—"
          }%`}
        />

        <DarkMetric
          title="Predicted yield"
          value={`${
            decision?.predicted_yield_kg_per_ha ??
            "—"
          } kg/ha`}
        />

        <DarkMetric
          title="Sustainability"
          value={`${
            data.decision?.sustainability
              ?.sustainability_score ?? "—"
          }/100`}
        />

        <DarkMetric
          title="Climate risk"
          value={`${
            data.decision?.climate_analysis
              ?.climate_risk ?? "—"
          }`}
        />
      </div>
    </div>
  );
}

function AIAdviceCard({ advice }) {
  return (
    <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-[#DDE7DD]">
      <div>
        <span className="rounded-full bg-[#F6E7A1] px-3 py-1 text-xs font-semibold">
          Agricultural Advisor
        </span>

        <h3 className="mt-3 text-2xl font-bold">
          {advice.summary}
        </h3>

        <p className="mt-3 text-sm leading-6">
          <strong>Recommendation:</strong>{" "}
          {advice.recommendation}
        </p>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <AdviceList
          title="Why"
          items={advice.reasons}
          bg="bg-[#CDE8D2]"
        />

        <AdviceList
          title="Expected impact"
          items={advice.expected_impact}
          bg="bg-[#A8DADC]"
        />

        <AdviceList
          title="Warnings"
          items={advice.warnings}
          bg="bg-[#F3B5A4]"
        />

        <AdviceList
          title="Next steps"
          items={advice.next_steps}
          bg="bg-[#F6E7A1]"
        />
      </div>
    </div>
  );
}

function AdviceList({
  title,
  items = [],
  bg,
}) {
  return (
    <div
      className={`rounded-2xl ${bg} p-5`}
    >
      <p className="text-xs font-semibold uppercase tracking-wide">
        {title}
      </p>

      <div className="mt-3 space-y-2">
        {items.map((item, index) => (
          <p
            key={`${title}-${index}`}
            className="text-sm leading-6"
          >
            • {item}
          </p>
        ))}
      </div>
    </div>
  );
}

function Metric({ title, value }) {
  return (
    <div className="rounded-2xl bg-[#F7F4E9] p-4">
      <p className="text-xs text-[#64746D]">
        {title}
      </p>

      <p className="mt-2 text-lg font-bold">
        {value}
      </p>
    </div>
  );
}

function DarkMetric({ title, value }) {
  return (
    <div className="rounded-2xl bg-white/10 p-4">
      <p className="text-xs text-white/70">
        {title}
      </p>

      <p className="mt-2 text-lg font-bold">
        {value}
      </p>
    </div>
  );
}

export default LiveIntelligence;