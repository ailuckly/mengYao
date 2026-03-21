const form = document.getElementById("predict-form");
const imageInput = document.getElementById("image-input");
const previewImage = document.getElementById("preview-image");
const resultImage = document.getElementById("result-image");
const statusText = document.getElementById("status");
const resultList = document.getElementById("result-list");
const labelsList = document.getElementById("labels-list");
const modeBadge = document.getElementById("mode-badge");

async function loadLabels() {
  try {
    const response = await fetch("/labels");
    const data = await response.json();
    if (!response.ok || data.status !== "ok") {
      throw new Error("读取类别失败");
    }

    modeBadge.textContent = `推理模式：${data.inference_mode}`;
    labelsList.innerHTML = data.labels
      .map((label) => `<span class="label-chip">${label}</span>`)
      .join("");
  } catch (error) {
    modeBadge.textContent = "推理模式：读取失败";
    labelsList.innerHTML = `<span class="label-chip">类别读取失败</span>`;
  }
}

imageInput.addEventListener("change", () => {
  const [file] = imageInput.files;
  if (!file) {
    return;
  }
  previewImage.src = URL.createObjectURL(file);
  statusText.textContent = "图片已选择，等待开始识别。";
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const [file] = imageInput.files;
  if (!file) {
    statusText.textContent = "请先选择图片。";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  statusText.textContent = "系统识别中，请稍候...";
  resultList.innerHTML = "";

  try {
    const response = await fetch("/predict", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();

    if (!response.ok || data.status !== "ok") {
      throw new Error(data.message || "识别失败");
    }

    resultImage.src = data.result_image;
    statusText.textContent = `${data.message}，当前模式：${data.meta.inference_mode}`;

    const fragments = data.predictions.map((item, index) => {
      const advice = data.advice[index] || "暂无建议";
      return `
        <article class="result-item">
          <strong>${item.label}</strong>
          <div>置信度：${Number(item.score).toFixed(4)}</div>
          <div>检测框：${item.box.join(", ")}</div>
          <div>推理来源：${item.source}</div>
          <div>建议：${advice}</div>
        </article>
      `;
    });
    resultList.innerHTML = fragments.join("");
  } catch (error) {
    statusText.textContent = error.message;
    resultImage.removeAttribute("src");
  }
});

loadLabels();
