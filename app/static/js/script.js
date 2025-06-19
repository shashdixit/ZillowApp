document.addEventListener("DOMContentLoaded", function () {
  const directoryForm = document.getElementById("directoryForm");
  const conversionResultContainer = document.getElementById("conversionResult");
  const conversionResultContent = document.getElementById(
    "conversionResultContent"
  );

  const ocrForm = document.getElementById("ocrForm");
  const ocrResultContainer = document.getElementById("ocrResult");
  const ocrResultContent = document.getElementById("ocrResultContent");

  const titleExtractionForm = document.getElementById("titleExtractionForm");
  const titleExtractionResultContainer = document.getElementById(
    "titleExtractionResult"
  );
  const titleExtractionResultContent = document.getElementById(
    "titleExtractionResultContent"
  );
  const titleExtractionProgress = document.getElementById(
    "titleExtractionProgress"
  );
  const titleExtractionPreview = document.getElementById(
    "titleExtractionPreview"
  );
  const titlePreviewTable = document
    .getElementById("titlePreviewTable")
    .querySelector("tbody");

  // TIF to PDF conversion form handler
  directoryForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const inputDir = document.getElementById("inputDir").value;
    const outputDir = document.getElementById("outputDir").value;

    if (!inputDir || !outputDir) {
      showConversionResult(
        "Please provide both input and output directories.",
        "error"
      );
      return;
    }

    // Show loading state
    showConversionResult("Converting files... Please wait.", "info");

    try {
      const formData = new FormData();
      formData.append("input_dir", inputDir);
      formData.append("output_dir", outputDir);

      const response = await fetch("/api/conversion/convert-directory", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        showConversionResult(
          `
                    <p class="success">${data.message}</p>
                    <div class="stats">
                        <p><strong>Total files:</strong> ${data.stats.total_files}</p>
                        <p><strong>Converted:</strong> ${data.stats.converted_files}</p>
                        <p><strong>Skipped:</strong> ${data.stats.skipped_files}</p>
                        <p><strong>Failed:</strong> ${data.stats.failed_files}</p>
                    </div>
                `,
          "success"
        );
      } else {
        showConversionResult(
          `Error: ${data.detail || "Unknown error occurred"}`,
          "error"
        );
      }
    } catch (error) {
      showConversionResult(`Error: ${error.message}`, "error");
    }
  });

  // OCR form handler
  ocrForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const inputDir = document.getElementById("ocrInputDir").value;
    const outputDir = document.getElementById("ocrOutputDir").value;
    const fileTypes = document.getElementById("fileTypes").value;

    if (!inputDir || !outputDir) {
      showOcrResult(
        "Please provide both input and output directories.",
        "error"
      );
      return;
    }

    // Show loading state
    showOcrResult(
      "Processing OCR... This may take some time depending on the number and size of files.",
      "info"
    );

    try {
      const formData = new FormData();
      formData.append("input_dir", inputDir);
      formData.append("output_dir", outputDir);
      if (fileTypes) {
        formData.append("file_types", fileTypes);
      }

      const response = await fetch("/api/ocr/process-directory", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        showOcrResult(
          `
                    <p class="success">${data.message}</p>
                    <div class="stats">
                        <p><strong>Total files:</strong> ${data.stats.total_files}</p>
                        <p><strong>Processed:</strong> ${data.stats.processed_files}</p>
                        <p><strong>Skipped:</strong> ${data.stats.skipped_files}</p>
                        <p><strong>Failed:</strong> ${data.stats.failed_files}</p>
                    </div>
                `,
          "success"
        );
      } else {
        showOcrResult(
          `Error: ${data.detail || "Unknown error occurred"}`,
          "error"
        );
      }
    } catch (error) {
      showOcrResult(`Error: ${error.message}`, "error");
    }
  });

  // Title Extraction form handler
  titleExtractionForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const inputDir = document.getElementById("titleInputDir").value;
    const outputFile = document.getElementById("titleOutputFile").value;
    const batchSize = document.getElementById("batchSize").value;

    if (!inputDir || !outputFile) {
      showTitleExtractionResult(
        "Please provide both input directory and output file path.",
        "error"
      );
      return;
    }

    // Show loading state
    showTitleExtractionResult(
      "Starting title extraction... This process may take several minutes.",
      "info"
    );
    updateProgressBar(0);

    try {
      const formData = new FormData();
      formData.append("input_dir", inputDir);
      formData.append("output_file", outputFile);
      formData.append("batch_size", batchSize);

      const response = await fetch("/api/title-extraction/extract-titles", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (response.ok && data.task_id) {
        // Start polling for task status
        showTitleExtractionResult(
          `Title extraction started. Task ID: ${data.task_id}`,
          "info"
        );
        pollTaskStatus(data.task_id);
      } else {
        showTitleExtractionResult(
          `Error: ${data.detail || "Unknown error occurred"}`,
          "error"
        );
      }
    } catch (error) {
      showTitleExtractionResult(`Error: ${error.message}`, "error");
    }
  });

  // Function to poll task status
  async function pollTaskStatus(taskId) {
    try {
      const response = await fetch(
        `/api/title-extraction/task-status/${taskId}`
      );
      const data = await response.json();

      if (response.ok) {
        // Update progress bar
        updateProgressBar(data.progress || 0);

        // Update status message
        showTitleExtractionResult(
          data.message || "Processing...",
          data.status === "failed" ? "error" : "info"
        );

        // If task is completed, show results
        if (data.status === "completed") {
          showTitleExtractionResult(
            `
                        <p class="success">${data.message}</p>
                    `,
            "success"
          );

          // Show preview if results are available
          if (data.results && data.results.length > 0) {
            showTitlePreview(data.results);
          }

          return; // Stop polling
        } else if (data.status === "failed") {
          showTitleExtractionResult(`Error: ${data.message}`, "error");
          return; // Stop polling
        }

        // Continue polling if task is still running
        setTimeout(() => pollTaskStatus(taskId), 2000);
      } else {
        showTitleExtractionResult(
          `Error checking task status: ${data.detail || "Unknown error"}`,
          "error"
        );
      }
    } catch (error) {
      showTitleExtractionResult(
        `Error checking task status: ${error.message}`,
        "error"
      );
    }
  }

  // Function to update progress bar
  function updateProgressBar(percentage) {
    const progressFill =
      titleExtractionProgress.querySelector(".progress-fill");
    const progressText =
      titleExtractionProgress.querySelector(".progress-text");

    progressFill.style.width = `${percentage}%`;
    progressText.textContent = `${percentage}%`;
  }

  // Function to show title preview
  function showTitlePreview(results) {
    // Clear previous results
    titlePreviewTable.innerHTML = "";

    // Add each result to the table
    results.forEach((result) => {
      const row = document.createElement("tr");

      const filenameCell = document.createElement("td");
      filenameCell.textContent = result[0]; // Filename
      row.appendChild(filenameCell);

      const titleCell = document.createElement("td");
      titleCell.textContent = result[1]; // Title
      row.appendChild(titleCell);

      titlePreviewTable.appendChild(row);
    });

    // Show the preview container
    titleExtractionPreview.classList.remove("hidden");
  }

  function showConversionResult(message, type) {
    conversionResultContainer.classList.remove("hidden");
    conversionResultContent.innerHTML = message;

    // Remove all status classes
    conversionResultContent.classList.remove("success", "error", "info");

    // Add appropriate class
    if (type) {
      conversionResultContent.classList.add(type);
    }

    // Scroll to result
    conversionResultContainer.scrollIntoView({ behavior: "smooth" });
  }

  function showOcrResult(message, type) {
    ocrResultContainer.classList.remove("hidden");
    ocrResultContent.innerHTML = message;

    // Remove all status classes
    ocrResultContent.classList.remove("success", "error", "info");

    // Add appropriate class
    if (type) {
      ocrResultContent.classList.add(type);
    }

    // Scroll to result
    ocrResultContainer.scrollIntoView({ behavior: "smooth" });
  }

  function showTitleExtractionResult(message, type) {
    titleExtractionResultContainer.classList.remove("hidden");
    titleExtractionResultContent.innerHTML = message;

    // Remove all status classes
    titleExtractionResultContent.classList.remove("success", "error", "info");

    // Add appropriate class
    if (type) {
      titleExtractionResultContent.classList.add(type);
    }

    // Scroll to result
    titleExtractionResultContainer.scrollIntoView({ behavior: "smooth" });
  }
});

// This function would typically use a file dialog, but browsers restrict this for security
// In a real application, you might need to use Electron or a backend solution
function browseDirectory(inputId) {
  // In a web-only environment, we can't directly access the file system
  // So we'll just alert the user about this limitation
  alert(
    "Directory browsing is not available in a web browser due to security restrictions.\n\nPlease manually enter the full directory path."
  );

  // Focus on the input field for better UX
  document.getElementById(inputId).focus();

  // Note: In a desktop application using Electron or similar framework,
  // you would implement actual directory browsing here
}

// Tab functionality
function openTab(tabName) {
  // Hide all tab contents
  const tabContents = document.getElementsByClassName("tab-content");
  for (let i = 0; i < tabContents.length; i++) {
    tabContents[i].classList.remove("active");
  }

  // Remove active class from all tab buttons
  const tabButtons = document.getElementsByClassName("tab-btn");
  for (let i = 0; i < tabButtons.length; i++) {
    tabButtons[i].classList.remove("active");
  }

  // Show the selected tab content and mark its button as active
  document.getElementById(tabName).classList.add("active");

  // Find and activate the button that opened this tab
  const buttons = document.getElementsByClassName("tab-btn");
  for (let i = 0; i < buttons.length; i++) {
    if (buttons[i].getAttribute("onclick").includes(tabName)) {
      buttons[i].classList.add("active");
    }
  }
}
