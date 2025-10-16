/**
 * Executes the fuzzy logic diagnosis by sending input data to the Flask API.
 */
function runDiagnosis() {
  const hgb = parseFloat(document.getElementById("hgb").value);
  const mcv = parseFloat(document.getElementById("mcv").value);
  const mchc = parseFloat(document.getElementById("mchc").value);

  const resultElement = document.getElementById("result");
  const fuzzyPlotElement = document.getElementById("fuzzyPlot");

  if (isNaN(hgb) || isNaN(mcv) || isNaN(mchc)) {
    resultElement.innerText = "Please ensure all fields are valid numbers!";
    resultElement.style.color = "red";
    fuzzyPlotElement.style.display = "none";
    return;
  }

  resultElement.innerText = "Calculating diagnosis...";
  resultElement.style.color = "#007BFF";
  fuzzyPlotElement.style.display = "none";

  fetch("/api/diagnose", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ hgb, mcv, mchc }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Server returned HTTP error ${response.status}.`);
      }
      return response.json();
    })
    .then((data) => {
      if (data.error) {
        resultElement.innerText = `Diagnosis Error: ${data.error}`;
        resultElement.style.color = "red";
      } else {
        resultElement.innerText = `Detected Type: ${data.diagnosis}`;
        resultElement.style.color = data.color || "#333";

        if (data.plot_img) {
          fuzzyPlotElement.src = "data:image/png;base64," + data.plot_img;
          fuzzyPlotElement.style.display = "block";
        }
      }
    })
    .catch((err) => {
      resultElement.innerText = `A communication error occurred: ${err.message}`;
      resultElement.style.color = "red";
    });
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("diagnosisForm");

  if (form) {
    // CRITICAL: Prevent default form submission and run AJAX logic instead
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      runDiagnosis();
    });
  }

  const fuzzyPlotElement = document.getElementById("fuzzyPlot");
  if (fuzzyPlotElement) {
    fuzzyPlotElement.style.display = "none";
  }
});
