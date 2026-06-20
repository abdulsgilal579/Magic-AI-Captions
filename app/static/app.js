let currentFile = null;
let jobId       = null;
let originalAss = null;

/* ── ASS ↔ readable ── */

function parseDialogue(line) {
  const content = line.slice(10);
  let rem = content;
  const parts = [];
  for (let i = 0; i < 9; i++) {
    const idx = rem.indexOf(',');
    parts.push(rem.slice(0, idx));
    rem = rem.slice(idx + 1);
  }
  parts.push(rem);
  return { start: parts[1], end: parts[2], text: parts[9] };
}

function assToReadable(ass) {
  return ass.split('\n')
    .filter(l => l.startsWith('Dialogue:'))
    .map(l => {
      const { start, end, text } = parseDialogue(l);
      const clean = text.replace(/\{[^}]*\}/g, '').replace(/\s+/g, ' ').trim();
      return `${start} --> ${end}\n${clean}`;
    })
    .join('\n\n');
}

function readableToAss(readable, origAss) {
  const eventsIdx = origAss.indexOf('[Events]');
  const header = origAss.slice(0, eventsIdx);
  const fmt = 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text';
  const dialogues = readable.trim().split(/\n\n+/)
    .filter(b => b.trim())
    .map(block => {
      const lines = block.split('\n');
      const [start, end] = lines[0].split(' --> ').map(s => s.trim());
      const text = lines.slice(1).join(' ').trim();
      return `Dialogue: 0,${start},${end},Default,,0,0,0,,${text}`;
    }).join('\n');
  return `${header}[Events]\n${fmt}\n${dialogues}`;
}

/* ── Panel navigation ── */

function showPanel(name) {
  ['upload', 'edit', 'done'].forEach(n =>
    document.getElementById('panel-' + n).classList.remove('active'));
  document.getElementById('panel-' + name).classList.add('active');

  const idx = { upload: 0, edit: 1, done: 2 }[name];
  ['s1', 's2', 's3'].forEach((id, i) => {
    const el = document.getElementById(id);
    el.classList.remove('active', 'done');
    if (i < idx)  el.classList.add('done');
    if (i === idx) el.classList.add('active');
  });
  ['sep1', 'sep2'].forEach((id, i) =>
    document.getElementById(id).classList.toggle('done', i < idx));
}

/* ── Helpers ── */

function setLoading(id, on, label) {
  const btn = document.getElementById(id);
  btn.disabled = on;
  btn.innerHTML = on ? '<div class="spinner"></div>' : label;
}

function showErr(id, msg) {
  const el = document.getElementById(id);
  el.textContent = msg;
  el.classList.add('visible');
}

function clearErr(id) {
  document.getElementById(id).classList.remove('visible');
}

/* ── Drop zone ── */

const dropZone  = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const fileLabel = document.getElementById('file-name');
const btnUpload = document.getElementById('btn-upload');

dropZone.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  const f = e.dataTransfer.files[0];
  if (f) setFile(f);
});
fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) setFile(fileInput.files[0]);
});

function setFile(f) {
  currentFile = f;
  fileLabel.textContent = f.name;
  fileLabel.classList.add('visible');
  btnUpload.disabled = false;
  clearErr('upload-error');
}

/* ── Upload & transcribe ── */

btnUpload.addEventListener('click', async () => {
  if (!currentFile) return;
  clearErr('upload-error');
  setLoading('btn-upload', true, 'Transcribe Video');
  try {
    const form = new FormData();
    form.append('file', currentFile);
    const res  = await fetch('/api/v1/upload', { method: 'POST', body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Upload failed');
    jobId = data.job_id;
    originalAss = data.captions;
    document.getElementById('captions-area').value = assToReadable(data.captions);
    showPanel('edit');
  } catch (err) {
    showErr('upload-error', err.message);
  } finally {
    setLoading('btn-upload', false, 'Transcribe Video');
  }
});

/* ── Burn captions ── */

document.getElementById('btn-burn').addEventListener('click', async () => {
  clearErr('burn-error');
  setLoading('btn-burn', true, 'Burn into Video');
  try {
    const captions = readableToAss(document.getElementById('captions-area').value, originalAss);
    const res  = await fetch('/api/v1/burn', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_id: jobId, captions }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Burn failed');
    document.getElementById('download-link').href = data.download_url;
    showPanel('done');
  } catch (err) {
    showErr('burn-error', err.message);
  } finally {
    setLoading('btn-burn', false, 'Burn into Video');
  }
});

/* ── Reset ── */

function reset() {
  currentFile = null;
  jobId       = null;
  originalAss = null;
  fileInput.value = '';
  fileLabel.textContent = '';
  fileLabel.classList.remove('visible');
  btnUpload.disabled = true;
  clearErr('upload-error');
  clearErr('burn-error');
  document.getElementById('captions-area').value = '';
  document.getElementById('download-link').href = '#';
  showPanel('upload');
}

document.getElementById('btn-back').addEventListener('click', reset);
document.getElementById('btn-restart').addEventListener('click', reset);
