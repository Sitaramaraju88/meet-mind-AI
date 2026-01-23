const express = require("express");
const app = express();

app.use(express.static("public")); // serve index.html

app.listen(3000, () => console.log("Frontend running on http://localhost:3000"));
