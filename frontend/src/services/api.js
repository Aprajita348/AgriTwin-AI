const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

async function requestJson(path, options = {}) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, options);
  } catch {
    throw new Error(
      "Could not connect to the AgriTwin AI backend. Make sure the FastAPI server is running."
    );
  }

  let payload = null;

  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem("agritwin_access_token");
      localStorage.removeItem("agritwin_username");
      localStorage.removeItem("agritwin_farm_id");

      throw new Error(
        "Your session has expired. Please log in again."
      );
    }

    const detail =
      payload?.detail ||
      `API request failed: ${response.status}`;

    throw new Error(detail);
  }

  return payload;
}

function authHeaders(token) {
  return token
    ? {
        Authorization: `Bearer ${token}`,
      }
    : {};
}

/* ============================================================
   AUTHENTICATION
============================================================ */

export async function registerUser(data) {
  return requestJson("/auth/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
}

export async function loginUser(data) {
  return requestJson("/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
}

export async function getCurrentUser(token) {
  return requestJson("/auth/me", {
    headers: authHeaders(token),
  });
}

/* ============================================================
   FARM MANAGEMENT
============================================================ */

export async function getFarms(token) {
  return requestJson("/farms", {
    headers: authHeaders(token),
  });
}

export async function createFarm(token, farmData) {
  return requestJson("/farms", {
    method: "POST",
    headers: {
      ...authHeaders(token),
      "Content-Type": "application/json",
    },
    body: JSON.stringify(farmData),
  });
}

/* ============================================================
   AGRITWIN DECISION PIPELINE
============================================================ */

export async function runDecisionPipeline(farmData) {
  return requestJson("/decision-pipeline", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(farmData),
  });
}

/* ============================================================
   WHAT-IF DIGITAL FARM
============================================================ */

export async function runWhatIfSimulation(scenarioData) {
  return requestJson("/what-if", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(scenarioData),
  });
}

/* ============================================================
   EARLY WARNING
============================================================ */

export async function getEarlyWarnings(warningData) {
  return requestJson("/early-warning", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(warningData),
  });
}

/* ============================================================
   CROP CALENDAR
============================================================ */

export async function getCropCalendar(crop) {
  return requestJson("/crop-calendar", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      crop,
    }),
  });
}

/* ============================================================
   LIVE WEATHER
============================================================ */

export async function getLiveWeather(farmId, token) {
  return requestJson(`/farms/${farmId}/weather/live`, {
    headers: authHeaders(token),
  });
}

/* ============================================================
   LIVE SOIL
============================================================ */

export async function getLiveSoil(farmId, token) {
  return requestJson(`/farms/${farmId}/soil/live`, {
    headers: authHeaders(token),
  });
}

/* ============================================================
   LIVE DECISION PIPELINE
============================================================ */

export async function runLiveDecisionPipeline(
  farmId,
  token,
  data
) {
  return requestJson(
    `/farms/${farmId}/decision-pipeline/live`,
    {
      method: "POST",
      headers: {
        ...authHeaders(token),
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }
  );
}

/* ============================================================
   GENAI AGRICULTURAL ADVISOR
============================================================ */

export async function generateAgriculturalAdvice(data) {
  return requestJson("/agricultural-advisor/ai", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
}

/* ============================================================
   LIVE + GENAI DECISION PIPELINE
============================================================ */

export async function runLiveAIDecisionPipeline(
  farmId,
  token,
  data
) {
  return requestJson(
    `/farms/${farmId}/decision-pipeline/ai`,
    {
      method: "POST",
      headers: {
        ...authHeaders(token),
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }
  );
}