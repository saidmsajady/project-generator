const functions = require("firebase-functions");
const express = require("express");
const cors = require("cors");
const axios = require("axios"); // For making HTTP requests to the FastAPI backend

const app = express();
app.use(cors({ origin: true }));  // Enable CORS for all origins

// API route that handles /api requests (example of a proxy to FastAPI)
app.post("/api/generate-project", async (req, res) => {
  try {
    // Make a request to your FastAPI backend here
    const response = await axios.post("https://project-generator-site.web.app/", req.body);

    res.json(response.data);  // Forward the response from FastAPI to the client
  } catch (error) {
    console.error("Error communicating with FastAPI:", error);
    res.status(500).json({ error: "Error generating project ideas." });
  }
});

// API route for testing (hello world)
app.get("/api/hello", (req, res) => {
  res.json({ message: "Hello from Firebase Functions!" });
});

// Exports the Express app as a Firebase Function
exports.api = functions.https.onRequest(app);