const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";


/* ============================================================
   AGRITWIN DECISION PIPELINE
============================================================ */

export async function runDecisionPipeline(
  farmData
) {
  const response = await fetch(
    `${API_BASE_URL}/decision-pipeline`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(farmData),
    }
  );

  if (!response.ok) {
    throw new Error(
      `API request failed: ${response.status}`
    );
  }

  return response.json();
}


/* ============================================================
   WHAT-IF DIGITAL FARM
============================================================ */

export async function runWhatIfSimulation(
  scenarioData
) {
  const response = await fetch(
    `${API_BASE_URL}/what-if`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(scenarioData),
    }
  );

  if (!response.ok) {
    throw new Error(
      `What-if API request failed: ${response.status}`
    );
  }

  return response.json();
}


/* ============================================================
   EARLY WARNING
============================================================ */

export async function getEarlyWarnings(
  warningData
) {
  const response = await fetch(
    `${API_BASE_URL}/early-warning`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(warningData),
    }
  );

  if (!response.ok) {
    throw new Error(
      `Early warning API request failed: ${response.status}`
    );
  }

  return response.json();
}


/* ============================================================
   CROP CALENDAR
============================================================ */

export async function getCropCalendar(
  crop
) {
  const response = await fetch(
    `${API_BASE_URL}/crop-calendar`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        crop,
      }),
    }
  );

  if (!response.ok) {
    throw new Error(
      `Crop calendar API request failed: ${response.status}`
    );
  }

  return response.json();
}