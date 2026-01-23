const express = require("express");
const multer = require("multer");
const { exec } = require("child_process");
const path = require("path");
require("dotenv").config();
console.log("GROQ KEY LOADED:", process.env.GROQ_API_KEY ? "YES" : "NO");

const app = express();
app.use(express.static("."));

const upload = multer({ dest: "uploads/" });

app.post("/upload", upload.single("audio"), (req, res) => {
  const audioPath = req.file.path;

  exec(`python ai/app.py ${audioPath}`, (err, stdout) => {
    if (err) return res.sendStatus(500);

    const result = JSON.parse(stdout);
    res.json(result);
  });
});

app.listen(3000, () =>
  console.log("🚀 SafeTalk running on http://localhost:3000")
);
