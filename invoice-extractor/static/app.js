// Stage 3: upload an invoice, read it, and show what was read.
// All text from the server goes in with textContent, never innerHTML,
// so a strange file name or a misread piece of text can never run as code.

const LOW_SCORE = 0.8; // boxes scoring below this are drawn dashed and amber
const POLL_MS = 1000; // how often we ask "is it done yet?"

const fileInput = document.getElementById("file");
const uploadButton = document.getElementById("upload");
const message = document.getElementById("message");
const list = document.getElementById("list");
const details = document.getElementById("details");
const toolbar = document.getElementById("toolbar");
const readButton = document.getElementById("read");
const readStatus = document.getElementById("read-status");
const showBoxes = document.getElementById("show-boxes");
const selectedInfo = document.getElementById("selected-info");
const empty = document.getElementById("empty");
const work = document.getElementById("work");
const preview = document.getElementById("preview");
const overlay = document.getElementById("overlay");
const segList = document.getElementById("seg-list");
const segCount = document.getElementById("seg-count");

let documents = [];
let selectedId = null;
let selectionToken = 0; // changes whenever you pick another invoice
let segments = [];
const boxById = new Map();
const itemById = new Map();
let selectedSegmentId = null;

// ---------------------------------------------------------------- helpers

async function getJson(url, options) {
  const response = await fetch(url, options);
  let data = {};
  try {
    data = await response.json();
  } catch (problem) {
    // not JSON: leave data empty
  }
  if (!response.ok) {
    throw new Error(data.error || "The request failed.");
  }
  return data;
}

function showMessage(text, kind) {
  message.textContent = text;
  message.className = kind || "";
}

function setReadStatus(text, kind) {
  readStatus.textContent = text;
  readStatus.className = kind || "";
}

function formatSize(bytes) {
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(0) + " KB";
  return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

function formatTime(isoText) {
  return new Date(isoText).toLocaleString();
}

function percent(fraction) {
  return (fraction * 100).toFixed(4) + "%";
}

function isLow(segment) {
  return segment.score < LOW_SCORE || segment.text.trim() === "";
}

// ------------------------------------------------------- the invoice list

function renderList() {
  list.replaceChildren();
  for (const doc of documents) {
    const item = document.createElement("li");
    const button = document.createElement("button");
    button.className = "doc" + (doc.document_id === selectedId ? " active" : "");

    const name = document.createElement("span");
    name.className = "doc-name";
    name.textContent = doc.original_filename;

    const meta = document.createElement("span");
    meta.className = "doc-meta";
    meta.textContent = formatTime(doc.uploaded_at) + " · " + doc.status;

    button.append(name, meta);
    button.addEventListener("click", () => selectDocument(doc.document_id));
    item.append(button);
    list.append(item);
  }
}

async function loadDocuments() {
  documents = await getJson("/api/documents");
  renderList();
}

// ------------------------------------------------- the boxes and the text

function clearResult() {
  segments = [];
  selectedSegmentId = null;
  boxById.clear();
  itemById.clear();
  overlay.replaceChildren();
  segList.replaceChildren();
  segCount.textContent = "";
  selectedInfo.textContent = "";
  setReadStatus("");
}

function renderResult() {
  overlay.replaceChildren();
  segList.replaceChildren();
  boxById.clear();
  itemById.clear();

  for (const segment of segments) {
    const [x0, y0, x1, y1] = segment.box_norm;
    const low = isLow(segment);
    const shown = segment.text === "" ? "(no text)" : segment.text;

    // The box over the picture.
    const box = document.createElement("div");
    box.className = "box" + (low ? " low" : "");
    box.style.left = percent(x0);
    box.style.top = percent(y0);
    box.style.width = percent(x1 - x0);
    box.style.height = percent(y1 - y0);
    box.title = shown + "  (score " + segment.score.toFixed(2) + ")";
    box.addEventListener("click", () => selectSegment(segment.id, "box"));
    overlay.append(box);
    boxById.set(segment.id, box);

    // The matching line in the list.
    const item = document.createElement("button");
    item.className = "seg" + (low ? " low" : "");
    const score = document.createElement("span");
    score.className = "score";
    score.textContent = segment.score.toFixed(2);
    const text = document.createElement("span");
    text.className = "txt" + (segment.text === "" ? " blank" : "");
    text.textContent = shown;
    item.append(score, text);
    item.addEventListener("click", () => selectSegment(segment.id, "list"));
    segList.append(item);
    itemById.set(segment.id, item);
  }

  segCount.textContent = "(" + segments.length + ")";
  overlay.hidden = !showBoxes.checked;
}

function selectSegment(segmentId, source) {
  if (selectedSegmentId !== null) {
    boxById.get(selectedSegmentId)?.classList.remove("selected");
    itemById.get(selectedSegmentId)?.classList.remove("selected");
  }
  selectedSegmentId = segmentId;

  const segment = segments.find((s) => s.id === segmentId);
  const box = boxById.get(segmentId);
  const item = itemById.get(segmentId);
  if (!segment || !box || !item) return;

  box.classList.add("selected");
  item.classList.add("selected");

  const [x0, y0, x1, y1] = segment.box_norm;
  const shown = segment.text === "" ? "(no text)" : segment.text;
  selectedInfo.textContent =
    "Selected #" + segment.id + ": “" + shown + "”" +
    " · score " + segment.score.toFixed(2) +
    " · position x " + x0.toFixed(3) + "–" + x1.toFixed(3) +
    ", y " + y0.toFixed(3) + "–" + y1.toFixed(3) + " (fractions of the page)";

  if (source === "list") box.scrollIntoView({ block: "nearest", inline: "nearest" });
  if (source === "box") item.scrollIntoView({ block: "nearest" });
}

// ------------------------------------------------------------- reading

function describeBusy(state) {
  if (state === "queued") return "Waiting in line…";
  if (state === "loading_models") {
    return "Loading the reading models… the first read after start-up can take up to a minute.";
  }
  return "Reading the invoice… about 10 to 15 seconds.";
}

async function loadResult(documentId, token) {
  const result = await getJson("/api/documents/" + documentId + "/ocr");
  if (token !== selectionToken) return; // you moved on to another invoice
  segments = result.segments;
  renderResult();
  readButton.disabled = false;
  setReadStatus(
    "Read " + segments.length + " pieces of text (took " + result.seconds_read_image + " s).",
    "ok"
  );
  await loadDocuments(); // the list now says "ocr_done"
}

async function handleStatus(documentId, status, token) {
  if (token !== selectionToken) return;

  if (status.state === "done") {
    await loadResult(documentId, token);
  } else if (status.state === "failed") {
    readButton.disabled = false;
    setReadStatus(status.error || "Reading failed.", "error");
  } else if (status.state === "not_read") {
    readButton.disabled = false;
    setReadStatus("Not read yet. Click “Read invoice”.", "");
  } else {
    // queued, loading_models or running: keep asking until it finishes
    readButton.disabled = true;
    setReadStatus(describeBusy(status.state), "");
    setTimeout(async () => {
      if (token !== selectionToken) return;
      try {
        const next = await getJson("/api/documents/" + documentId + "/ocr/status");
        await handleStatus(documentId, next, token);
      } catch (problem) {
        readButton.disabled = false;
        setReadStatus("Lost contact with the app. Is it still running?", "error");
      }
    }, POLL_MS);
  }
}

async function readInvoice() {
  if (!selectedId) return;
  const documentId = selectedId;
  const token = selectionToken;
  readButton.disabled = true;
  setReadStatus("Sending…", "");
  try {
    const status = await getJson("/api/documents/" + documentId + "/ocr", {
      method: "POST",
    });
    await handleStatus(documentId, status, token);
  } catch (problem) {
    readButton.disabled = false;
    setReadStatus(problem.message, "error");
  }
}

// ------------------------------------------------------------ choosing

async function selectDocument(documentId) {
  const doc = documents.find((d) => d.document_id === documentId);
  if (!doc) return;
  selectedId = documentId;
  const token = ++selectionToken;
  clearResult();

  details.textContent =
    doc.original_filename +
    " · " + doc.width_px + " × " + doc.height_px + " px" +
    " · " + formatSize(doc.size_bytes) +
    " · fingerprint " + doc.sha256.slice(0, 12);

  preview.src = "/api/documents/" + doc.document_id + "/preview";
  empty.hidden = true;
  work.hidden = false;
  toolbar.hidden = false;
  readButton.disabled = true;
  renderList();

  try {
    const status = await getJson("/api/documents/" + documentId + "/ocr/status");
    await handleStatus(documentId, status, token);
  } catch (problem) {
    setReadStatus(problem.message, "error");
  }
}

// ------------------------------------------------------------ uploading

async function upload() {
  const file = fileInput.files[0];
  if (!file) {
    showMessage("Choose a file first.", "error");
    return;
  }
  uploadButton.disabled = true;
  showMessage("Uploading…", "");

  try {
    const form = new FormData();
    form.append("file", file);
    const result = await getJson("/api/documents", { method: "POST", body: form });

    await loadDocuments();
    selectDocument(result.document.document_id);
    if (result.duplicate) {
      showMessage("This exact file was uploaded before. Showing the earlier copy.", "ok");
    } else {
      showMessage("Uploaded.", "ok");
    }
    fileInput.value = "";
  } catch (problem) {
    showMessage(problem.message || "Could not reach the app. Is it still running?", "error");
  } finally {
    uploadButton.disabled = false;
  }
}

uploadButton.addEventListener("click", upload);
readButton.addEventListener("click", readInvoice);
showBoxes.addEventListener("change", () => {
  overlay.hidden = !showBoxes.checked;
});
loadDocuments();