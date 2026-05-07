import axios from "axios";

const API_SERVER_URL =
  process.env.API_SERVER_URL ||
  (process.env.NODE_ENV === "production" ? "" : "http://localhost:8000/api");

export default async function handler(req, res) {
  if (!API_SERVER_URL) {
    res.status(500).json({
      message: "API_SERVER_URL is not configured for this deployment."
    });
    return;
  }

  const path = Array.isArray(req.query.path) ? req.query.path.join("/") : req.query.path;
  const targetUrl = `${API_SERVER_URL.replace(/\/$/, "")}/${path || ""}`;
  const { path: _path, ...params } = req.query;

  try {
    const response = await axios.request({
      url: targetUrl,
      method: req.method,
      data: req.body,
      params,
      headers: {
        authorization: req.headers.authorization,
        "content-type": req.headers["content-type"] || "application/json"
      },
      timeout: 15000,
      validateStatus: () => true
    });

    res.status(response.status).json(response.data);
  } catch (error) {
    res.status(502).json({
      message: "Backend API is unreachable. Check API_SERVER_URL and confirm the ITMS backend is running.",
      detail: error.message
    });
  }
}
