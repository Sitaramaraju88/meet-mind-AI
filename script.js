let mediaRecorder;
let audioChunks = [];

const recordBtn = document.getElementById("recordBtn");
const statusText = document.getElementById("status");
const transcriptDiv = document.getElementById("transcript");
const audioPlayer = document.getElementById("audioPlayer");

console.debug("Script loaded. Waiting for user interaction.");

recordBtn.onclick = async () => {
  console.debug("Record button clicked.");
  if (!mediaRecorder || mediaRecorder.state === "inactive") {
    console.debug("Initializing mediaRecorder...");
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    console.debug("Audio stream acquired:", stream);
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = e => {
      console.debug("ondataavailable event:", e);
      audioChunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      console.debug("Recording stopped. Processing audio chunks:", audioChunks);
      const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
      audioChunks = [];

      const formData = new FormData();
      formData.append("audio", audioBlob);
      console.debug("FormData prepared with audio blob:", audioBlob);

      statusText.innerText = "Processing...";

      try {
        const res = await fetch("/upload", {
          method: "POST",
          body: formData
        });
        console.debug("Upload response received:", res);

        const data = await res.json();
        console.debug("Response JSON parsed:", data);

        transcriptDiv.innerText = data.text;
        audioPlayer.src = data.audio;
        statusText.innerText = "Done";
      } catch (err) {
        console.error("Error during upload or response handling:", err);
        statusText.innerText = "Error";
      }
    };

    mediaRecorder.start();
    console.debug("Recording started.");
    recordBtn.innerText = "Stop Recording";
  } else {
    console.debug("Stopping recording...");
    mediaRecorder.stop();
    recordBtn.innerText = "Start Recording";
  }
};
