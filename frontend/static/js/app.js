const form = document.getElementById("predict-form");
const imageInput = document.getElementById("image-input");
const previewImage = document.getElementById("preview-image");
const resultImage = document.getElementById("result-image");
const statusText = document.getElementById("status");
const resultList = document.getElementById("result-list");
const labelsList = document.getElementById("labels-list");
const modeBadge = document.getElementById("mode-badge");
const labelsCount = document.getElementById("labels-count");
const predictionCount = document.getElementById("prediction-count");
const serviceHealth = document.getElementById("service-health");
const topLabel = document.getElementById("top-label");
const topScore = document.getElementById("top-score");
const predictionSource = document.getElementById("prediction-source");
const fileName = document.getElementById("file-name");
const previewEmpty = document.getElementById("preview-empty");
const resultEmpty = document.getElementById("result-empty");
const historyLink = document.getElementById("history-link");

function setStatus(message, tone = "idle") {
  if (!statusText) {
    return;
  }
  statusText.textContent = message;
  statusText.className = `status status-${tone}`;
}

function formatMode(mode) {
  return mode === "real" ? "真实模型" : "占位模式";
}

function resetHistoryLink() {
  if (!historyLink) {
    return;
  }
  historyLink.href = "/history";
  historyLink.classList.add("disabled-link");
}

async function loadHealth() {
  if (!serviceHealth || !modeBadge) {
    return;
  }

  try {
    const response = await fetch("/health");
    const data = await response.json();
    if (!response.ok || data.status !== "ok") {
      throw new Error("服务状态读取失败");
    }

    serviceHealth.textContent = data.model_loaded ? "模型已加载" : "占位推理";
    modeBadge.textContent = `推理模式：${formatMode(data.inference_mode)}`;
    modeBadge.classList.toggle("is-live", data.inference_mode === "real");
    modeBadge.classList.toggle("is-mock", data.inference_mode !== "real");
  } catch (error) {
    serviceHealth.textContent = "状态未知";
    modeBadge.textContent = "推理模式：读取失败";
  }
}

async function loadLabels() {
  if (!labelsCount || !labelsList) {
    return;
  }

  try {
    const response = await fetch("/labels");
    const data = await response.json();
    if (!response.ok || data.status !== "ok") {
      throw new Error("读取类别失败");
    }

    labelsCount.textContent = String(data.labels.length);
    labelsList.innerHTML = data.labels
      .map((label) => `<span class="label-chip">${label}</span>`)
      .join("");
  } catch (error) {
    labelsCount.textContent = "--";
    labelsList.innerHTML = `<span class="label-chip">类别读取失败</span>`;
  }
}

function bindDetectPage() {
  if (!form || !imageInput) {
    return;
  }

  imageInput.addEventListener("change", () => {
    const [file] = imageInput.files;
    if (!file) {
      return;
    }

    previewImage.src = URL.createObjectURL(file);
    previewImage.classList.add("visible");
    previewEmpty.style.display = "none";
    fileName.textContent = file.name;
    resetHistoryLink();
    setStatus("图片已选择，等待开始识别。", "idle");
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const [file] = imageInput.files;
    if (!file) {
      setStatus("请先选择图片。", "error");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    resetHistoryLink();
    setStatus("系统识别中，请稍候，正在调用模型进行推理分析。", "loading");
    resultList.innerHTML = `<div class="empty-inline">正在识别中，请稍候...</div>`;

    try {
      const response = await fetch("/predict", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();

      if (!response.ok || data.status !== "ok") {
        throw new Error(data.message || "识别失败");
      }

      if (data.result_image) {
        resultImage.src = data.result_image;
        resultImage.classList.add("visible");
        resultEmpty.style.display = "none";
      } else {
        resultImage.removeAttribute("src");
        resultImage.classList.remove("visible");
        resultEmpty.style.display = "block";
      }

      predictionCount.textContent = String(data.meta.prediction_count);
      topLabel.textContent = data.labels[0] || "未识别";
      topScore.textContent = data.scores.length ? Number(data.scores[0]).toFixed(4) : "--";
      predictionSource.textContent = data.predictions[0]?.source || "--";
      setStatus(`${data.message}，当前模式：${formatMode(data.meta.inference_mode)}。`, "success");

      if (historyLink && data.record_id) {
        historyLink.href = `/history/${data.record_id}`;
        historyLink.classList.remove("disabled-link");
      }

      if (!data.predictions.length) {
        resultList.innerHTML = `<div class="empty-inline">本次未检测到明确目标，请尝试更换更清晰的图片后再次识别。</div>`;
        return;
      }

      const fragments = data.predictions.map((item, index) => {
        const advice = data.advice[index] || "暂无建议";
        return `
          <article class="result-item">
            <strong>${item.label}</strong>
            <p>置信度：<span>${Number(item.score).toFixed(4)}</span></p>
            <p>检测框：<span>${item.box.join(", ")}</span></p>
            <p>推理来源：<span>${item.source}</span></p>
            <p>建议：<span>${advice}</span></p>
          </article>
        `;
      });
      resultList.innerHTML = fragments.join("");
    } catch (error) {
      setStatus(error.message, "error");
      resultImage.removeAttribute("src");
      resultImage.classList.remove("visible");
      resultEmpty.style.display = "block";
      predictionCount.textContent = "0";
      topLabel.textContent = "识别失败";
      topScore.textContent = "--";
      predictionSource.textContent = "--";
      resultList.innerHTML = `<div class="empty-inline">识别未成功完成，请检查图片格式或稍后重试。</div>`;
      resetHistoryLink();
    }
  });

  resetHistoryLink();
  loadHealth();
  loadLabels();
}

bindDetectPage();
