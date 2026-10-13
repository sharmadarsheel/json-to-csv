/**
 * @file app.js
 * @description Frontend controller communicating with Python backend REST API.
 */

const SAMPLES = {
  flat: [
    { id: 1, name: "John Doe", email: "john@example.com", active: true },
    { id: 2, name: "Jane Smith", email: "jane@example.com", active: false }
  ],
  nested: [
    {
      id: 101,
      user: {
        name: "Alice Wonderland",
        contact: { email: "alice@wonder.land", phone: "+1-555-0199" }
      },
      location: { city: "Oxford", country: "UK" }
    },
    {
      id: 102,
      user: {
        name: "Bob Builder",
        contact: { email: "bob@builder.org", phone: "+1-555-0144" }
      },
      location: { city: "London", country: "UK" }
    }
  ],
  arrays: [
    { id: 1, product: "Widget A", tags: ["tools", "hardware", "popular"] },
    { id: 2, product: "Widget B", tags: ["office", "stationery"] }
  ],
  'mixed-keys': [
    { id: 1, name: "Alpha", tier: "Gold" },
    { id: 2, name: "Beta", score: 98.5 },
    { id: 3, name: "Gamma", tier: "Silver", score: 75.0, verified: true }
  ],
  unicode: [
    { greeting: "नमस्ते 😀", language: "Hindi", notes: "Unicode & emoji test" },
    { greeting: "Bonjour le monde 🥐", language: "French", notes: "Accents & emoji" },
    { greeting: "こんにちは 🌸", language: "Japanese", notes: "Kanji & Hiragana" }
  ]
};

const state = {
  rawJsonText: '',
  allHeaders: [],
  selectedHeaders: [],
  lastGeneratedCsv: '',
  selectedDataKey: '',
  isProcessing: false
};

const dom = {};

function initDom() {
  dom.themeToggle = document.getElementById('theme-toggle');
  dom.iconSun = document.getElementById('icon-theme-sun');
  dom.iconMoon = document.getElementById('icon-theme-moon');

  dom.tabUpload = document.getElementById('tab-upload');
  dom.tabPaste = document.getElementById('tab-paste');
  dom.panelUpload = document.getElementById('panel-upload');
  dom.panelPaste = document.getElementById('panel-paste');

  dom.dropzone = document.getElementById('dropzone');
  dom.fileInput = document.getElementById('file-input');
  dom.fileStatus = document.getElementById('file-status');
  dom.jsonInput = document.getElementById('json-input');
  dom.charCount = document.getElementById('char-count');
  dom.btnFormatJson = document.getElementById('btn-format-json');
  dom.btnClearJson = document.getElementById('btn-clear-json');

  dom.sampleSelect = document.getElementById('sample-select');
  dom.objectKeyPickerWrapper = document.getElementById('object-key-picker-wrapper');
  dom.selectObjectKey = document.getElementById('select-object-key');

  dom.validationBanner = document.getElementById('validation-banner');
  dom.validationIcon = document.getElementById('validation-icon');
  dom.validationMessage = document.getElementById('validation-message');

  dom.optDelimiter = document.getElementById('opt-delimiter');
  dom.optSeparator = document.getElementById('opt-separator');
  dom.optArrayStrategy = document.getElementById('opt-array-strategy');
  dom.groupArrayJoiner = document.getElementById('group-array-joiner');
  dom.optArrayJoiner = document.getElementById('opt-array-joiner');
  dom.optMaxDepth = document.getElementById('opt-max-depth');
  dom.optFillValue = document.getElementById('opt-fill-value');
  dom.optBom = document.getElementById('opt-bom');
  dom.optIncludeHeader = document.getElementById('opt-include-header');
  dom.optSanitizeFormulas = document.getElementById('opt-sanitize-formulas');
  dom.optProtectNumbers = document.getElementById('opt-protect-numbers');

  dom.btnSavePreset = document.getElementById('btn-save-preset');
  dom.btnLoadPreset = document.getElementById('btn-load-preset');
  dom.btnResetOptions = document.getElementById('btn-reset-options');

  dom.columnSearch = document.getElementById('column-search');
  dom.columnList = document.getElementById('column-list');
  dom.btnSelectAllCols = document.getElementById('btn-select-all-cols');
  dom.btnDeselectAllCols = document.getElementById('btn-deselect-all-cols');
  dom.btnResetCols = document.getElementById('btn-reset-cols');

  dom.statRows = document.getElementById('stat-rows');
  dom.statColumns = document.getElementById('stat-columns');
  dom.statSize = document.getElementById('stat-size');
  dom.statSkipped = document.getElementById('stat-skipped');
  dom.tableLoading = document.getElementById('table-loading');
  dom.previewTheadTr = document.getElementById('preview-thead-tr');
  dom.previewTbody = document.getElementById('preview-tbody');

  dom.filenameInput = document.getElementById('filename-input');
  dom.btnCopyCsv = document.getElementById('btn-copy-csv');
  dom.btnDownloadCsv = document.getElementById('btn-download-csv');

  dom.btnReverseModal = document.getElementById('btn-reverse-modal');
  dom.modalReverse = document.getElementById('modal-reverse');
  dom.btnCloseModal = document.getElementById('btn-close-modal');
  dom.reverseDelimiter = document.getElementById('reverse-delimiter');
  dom.reverseCsvInput = document.getElementById('reverse-csv-input');
  dom.reverseJsonOutput = document.getElementById('reverse-json-output');
  dom.btnRunReverse = document.getElementById('btn-run-reverse');
  dom.btnCopyReverseJson = document.getElementById('btn-copy-reverse-json');
  dom.btnLoadIntoEditor = document.getElementById('btn-load-into-editor');

  dom.toastContainer = document.getElementById('toast-container');
}

function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  dom.toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 250);
  }, 3000);
}

function formatBytes(bytes) {
  if (!Number.isFinite(bytes) || bytes <= 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  const unitIndex = Math.min(i, units.length - 1);
  const size = bytes / Math.pow(1024, unitIndex);
  return `${size.toFixed(unitIndex === 0 ? 0 : 2)} ${units[unitIndex]}`;
}

function getOptions() {
  return {
    delimiter: dom.optDelimiter.value,
    separator: dom.optSeparator.value,
    array_strategy: dom.optArrayStrategy.value,
    array_joiner: dom.optArrayJoiner.value,
    max_depth: parseInt(dom.optMaxDepth.value, 10) || 10,
    fill_value: dom.optFillValue.value,
    bom: dom.optBom.value === 'true',
    include_header: dom.optIncludeHeader.checked,
    sanitize_formulas: dom.optSanitizeFormulas.checked,
    protect_numbers: dom.optProtectNumbers.checked,
    data_key: state.selectedDataKey
  };
}

let activeAbort = null;

async function processData() {
  if (!state.rawJsonText.trim()) {
    clearOutput();
    return;
  }

  if (activeAbort) {
    activeAbort.abort();
  }
  activeAbort = new AbortController();

  dom.tableLoading.classList.remove('hidden');

  try {
    const payload = {
      json_text: state.rawJsonText,
      options: getOptions(),
      selected_headers: state.selectedHeaders.length > 0 ? state.selectedHeaders : null
    };

    const res = await fetch('/api/convert', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: activeAbort.signal
    });

    const data = await res.json();
    dom.tableLoading.classList.add('hidden');

    if (!data.ok) {
      showValidation(false, data.error, data.line, data.column);
      return;
    }

    state.lastGeneratedCsv = data.csv;
    state.allHeaders = data.all_headers;
    state.selectedHeaders = data.effective_headers;

    // Detect array keys
    if (data.detected_array_keys && data.detected_array_keys.length > 0) {
      dom.objectKeyPickerWrapper.classList.remove('hidden');
      dom.selectObjectKey.innerHTML = `
        <option value="">&bull; Root Object (Single Row)</option>
        ${data.detected_array_keys.map(k => `<option value="${escapeHtml(k)}" ${state.selectedDataKey === k ? 'selected' : ''}>Array key: "${escapeHtml(k)}"</option>`).join('')}
      `;
    } else {
      dom.objectKeyPickerWrapper.classList.add('hidden');
    }

    showValidation(true, `Valid JSON &bull; ${data.total_rows} row${data.total_rows === 1 ? '' : 's'} generated`);
    updateStats(data.total_rows, data.total_columns, data.csv.length, data.skipped_count);
    renderColumnPicker();
    renderPreviewTable(data.preview_rows, data.effective_headers);

  } catch (err) {
    if (err.name === 'AbortError') return;
    dom.tableLoading.classList.add('hidden');
    showValidation(false, err.message);
  }
}

function showValidation(valid, message, line, column) {
  dom.validationBanner.classList.remove('hidden', 'valid', 'invalid');
  if (valid) {
    dom.validationBanner.classList.add('valid');
    dom.validationIcon.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`;
    dom.validationMessage.innerHTML = message;
  } else {
    dom.validationBanner.classList.add('invalid');
    dom.validationIcon.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`;
    const posCallout = (line && column) ? `<strong>[Line ${line}, Column ${column}]</strong> ` : '';
    dom.validationMessage.innerHTML = `${posCallout}${escapeHtml(message)}`;
  }
}

function updateStats(rows, cols, bytes, skipped) {
  dom.statRows.textContent = rows.toLocaleString();
  dom.statColumns.textContent = cols.toLocaleString();
  dom.statSize.textContent = formatBytes(bytes);
  dom.statSkipped.textContent = skipped.toLocaleString();
}

function renderPreviewTable(rows, headers) {
  if (!rows || rows.length === 0 || !headers || headers.length === 0) {
    dom.previewTheadTr.innerHTML = '<th>#</th><th class="text-muted">No columns</th>';
    dom.previewTbody.innerHTML = '<tr><td colspan="2" class="table-empty-cell">No rows to display.</td></tr>';
    return;
  }

  dom.previewTheadTr.innerHTML = `<th>#</th>` + headers.map(h => `<th title="${escapeHtml(h)}">${escapeHtml(h)}</th>`).join('');

  dom.previewTbody.innerHTML = rows.map((row, idx) => {
    const cells = headers.map(h => {
      const val = row && Object.prototype.hasOwnProperty.call(row, h) ? row[h] : '';
      let displayVal = val;
      if (val === null || val === undefined) displayVal = '<span class="text-muted italic">null</span>';
      else if (typeof val === 'boolean') displayVal = `<span class="accent-text font-bold">${val}</span>`;
      else if (typeof val === 'object') displayVal = escapeHtml(JSON.stringify(val));
      else displayVal = escapeHtml(String(val));
      return `<td title="${escapeHtml(String(val ?? ''))}">${displayVal}</td>`;
    }).join('');
    return `<tr><td>${idx + 1}</td>${cells}</tr>`;
  }).join('');
}

function renderColumnPicker() {
  const searchTerm = dom.columnSearch.value.trim().toLowerCase();
  const available = state.allHeaders;

  if (available.length === 0) {
    dom.columnList.innerHTML = '<span class="text-muted">No columns detected.</span>';
    return;
  }

  const selectedSet = new Set(state.selectedHeaders);
  const visibleHeaders = state.selectedHeaders.filter(h => !searchTerm || h.toLowerCase().includes(searchTerm));

  dom.columnList.innerHTML = visibleHeaders.map((header) => {
    const isSelected = selectedSet.has(header);
    return `
      <div class="column-badge ${isSelected ? '' : 'disabled'}" draggable="true" data-col="${escapeHtml(header)}">
        <span class="drag-handle" title="Drag to reorder">&#x2630;</span>
        <input type="checkbox" ${isSelected ? 'checked' : ''} data-toggle-col="${escapeHtml(header)}" aria-label="Include ${escapeHtml(header)}">
        <span class="col-name">${escapeHtml(header)}</span>
      </div>
    `;
  }).join('');

  setupColumnDragAndDrop();
}

let draggedElement = null;

function setupColumnDragAndDrop() {
  const badges = dom.columnList.querySelectorAll('.column-badge');
  badges.forEach(badge => {
    badge.addEventListener('dragstart', (e) => {
      draggedElement = badge;
      badge.classList.add('dragging');
      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData('text/plain', badge.dataset.col);
    });

    badge.addEventListener('dragend', () => {
      badge.classList.remove('dragging');
      draggedElement = null;
    });

    badge.addEventListener('dragover', (e) => {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
    });

    badge.addEventListener('drop', (e) => {
      e.preventDefault();
      if (!draggedElement || draggedElement === badge) return;

      const srcCol = draggedElement.dataset.col;
      const targetCol = badge.dataset.col;

      const srcIndex = state.selectedHeaders.indexOf(srcCol);
      const targetIndex = state.selectedHeaders.indexOf(targetCol);

      if (srcIndex !== -1 && targetIndex !== -1) {
        state.selectedHeaders.splice(srcIndex, 1);
        state.selectedHeaders.splice(targetIndex, 0, srcCol);
        renderColumnPicker();
        processData();
      }
    });

    const checkbox = badge.querySelector('input[type="checkbox"]');
    if (checkbox) {
      checkbox.addEventListener('change', (e) => {
        const colName = e.target.dataset.toggleCol;
        if (e.target.checked) {
          if (!state.selectedHeaders.includes(colName)) {
            state.selectedHeaders.push(colName);
          }
        } else {
          state.selectedHeaders = state.selectedHeaders.filter(h => h !== colName);
        }
        badge.classList.toggle('disabled', !e.target.checked);
        processData();
      });
    }
  });
}

function clearOutput() {
  state.allHeaders = [];
  state.selectedHeaders = [];
  state.lastGeneratedCsv = '';
  dom.validationBanner.classList.add('hidden');
  updateStats(0, 0, 0, 0);
  renderPreviewTable([], []);
  renderColumnPicker();
}

function escapeHtml(str) {
  if (typeof str !== 'string') return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function setupEvents() {
  dom.themeToggle.addEventListener('click', () => {
    const isLight = document.body.classList.toggle('theme-light');
    document.body.classList.toggle('theme-dark', !isLight);
    dom.iconSun.classList.toggle('hidden', isLight);
    dom.iconMoon.classList.toggle('hidden', !isLight);
    localStorage.setItem('json_to_csv_theme', isLight ? 'light' : 'dark');
  });

  const savedTheme = localStorage.getItem('json_to_csv_theme');
  if (savedTheme === 'light') {
    document.body.classList.add('theme-light');
    document.body.classList.remove('theme-dark');
    dom.iconSun.classList.add('hidden');
    dom.iconMoon.classList.remove('hidden');
  }

  dom.tabUpload.addEventListener('click', () => {
    dom.tabUpload.classList.add('active');
    dom.tabPaste.classList.remove('active');
    dom.panelUpload.classList.add('active');
    dom.panelPaste.classList.remove('active');
  });

  dom.tabPaste.addEventListener('click', () => {
    dom.tabPaste.classList.add('active');
    dom.tabUpload.classList.remove('active');
    dom.panelPaste.classList.add('active');
    dom.panelUpload.classList.remove('active');
    dom.jsonInput.focus();
  });

  dom.dropzone.addEventListener('click', () => dom.fileInput.click());
  dom.dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dom.dropzone.classList.add('dragover');
  });
  dom.dropzone.addEventListener('dragleave', () => dom.dropzone.classList.remove('dragover'));
  dom.dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dom.dropzone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  });

  dom.fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) handleFile(file);
  });

  function handleFile(file) {
    dom.fileStatus.classList.remove('hidden');
    dom.fileStatus.innerHTML = `<strong>${escapeHtml(file.name)}</strong> (${formatBytes(file.size)})`;
    const reader = new FileReader();
    reader.onload = (ev) => {
      state.rawJsonText = ev.target.result;
      dom.jsonInput.value = state.rawJsonText;
      dom.charCount.textContent = `${state.rawJsonText.length.toLocaleString()} characters`;
      processData();
    };
    reader.readAsText(file);
  }

  let pasteDebounce = null;
  dom.jsonInput.addEventListener('input', () => {
    state.rawJsonText = dom.jsonInput.value;
    dom.charCount.textContent = `${state.rawJsonText.length.toLocaleString()} characters`;
    clearTimeout(pasteDebounce);
    pasteDebounce = setTimeout(processData, 200);
  });

  dom.btnFormatJson.addEventListener('click', () => {
    try {
      if (!dom.jsonInput.value.trim()) return;
      const parsed = JSON.parse(dom.jsonInput.value);
      dom.jsonInput.value = JSON.stringify(parsed, null, 2);
      state.rawJsonText = dom.jsonInput.value;
      dom.charCount.textContent = `${state.rawJsonText.length.toLocaleString()} characters`;
      showToast('JSON formatted successfully', 'success');
      processData();
    } catch {
      showToast('Cannot format: invalid JSON', 'error');
    }
  });

  dom.btnClearJson.addEventListener('click', () => {
    dom.jsonInput.value = '';
    state.rawJsonText = '';
    dom.charCount.textContent = '0 characters';
    dom.fileStatus.classList.add('hidden');
    clearOutput();
  });

  dom.sampleSelect.addEventListener('change', (e) => {
    const sampleKey = e.target.value;
    if (SAMPLES[sampleKey]) {
      const jsonStr = JSON.stringify(SAMPLES[sampleKey], null, 2);
      state.rawJsonText = jsonStr;
      dom.jsonInput.value = jsonStr;
      dom.charCount.textContent = `${jsonStr.length.toLocaleString()} characters`;
      dom.fileStatus.classList.remove('hidden');
      dom.fileStatus.innerHTML = `Loaded Sample: <strong>${sampleKey}.json</strong>`;
      processData();
      showToast(`Loaded sample "${sampleKey}"`, 'info');
    }
  });

  dom.selectObjectKey.addEventListener('change', (e) => {
    state.selectedDataKey = e.target.value;
    processData();
  });

  const optionInputs = [
    dom.optDelimiter,
    dom.optSeparator,
    dom.optArrayStrategy,
    dom.optArrayJoiner,
    dom.optMaxDepth,
    dom.optFillValue,
    dom.optBom,
    dom.optIncludeHeader,
    dom.optSanitizeFormulas,
    dom.optProtectNumbers
  ];

  optionInputs.forEach(el => {
    el.addEventListener('change', () => {
      dom.groupArrayJoiner.style.display = dom.optArrayStrategy.value === 'join' ? 'flex' : 'none';
      processData();
    });
  });

  dom.btnSelectAllCols.addEventListener('click', () => {
    state.selectedHeaders = [...state.allHeaders];
    renderColumnPicker();
    processData();
  });

  dom.btnDeselectAllCols.addEventListener('click', () => {
    state.selectedHeaders = [];
    renderColumnPicker();
    processData();
  });

  dom.btnResetCols.addEventListener('click', () => {
    state.selectedHeaders = [...state.allHeaders];
    renderColumnPicker();
    processData();
  });

  dom.columnSearch.addEventListener('input', () => {
    renderColumnPicker();
  });

  dom.btnCopyCsv.addEventListener('click', async () => {
    if (!state.lastGeneratedCsv) {
      showToast('No CSV data available to copy', 'error');
      return;
    }
    await navigator.clipboard.writeText(state.lastGeneratedCsv);
    showToast('CSV copied to clipboard!', 'success');
  });

  dom.btnDownloadCsv.addEventListener('click', () => {
    if (!state.lastGeneratedCsv) {
      showToast('No CSV data available to download', 'error');
      return;
    }
    let filename = dom.filenameInput.value.trim() || 'converted.csv';
    if (!filename.endsWith('.csv')) filename += '.csv';
    const blob = new Blob([state.lastGeneratedCsv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast(`Downloading ${filename}`, 'success');
  });

  dom.btnReverseModal.addEventListener('click', () => {
    dom.modalReverse.classList.remove('hidden');
    dom.reverseCsvInput.focus();
  });

  dom.btnCloseModal.addEventListener('click', () => {
    dom.modalReverse.classList.add('hidden');
  });

  dom.btnRunReverse.addEventListener('click', async () => {
    const csv = dom.reverseCsvInput.value;
    const delimiter = dom.reverseDelimiter.value;
    try {
      const res = await fetch('/api/reverse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ csv_text: csv, delimiter })
      });
      const data = await res.json();
      if (data.ok) {
        dom.reverseJsonOutput.value = JSON.stringify(data.data, null, 2);
        showToast(`Parsed ${data.data.length} records!`, 'success');
      } else {
        showToast(data.error, 'error');
      }
    } catch (e) {
      showToast(e.message, 'error');
    }
  });

  dom.btnCopyReverseJson.addEventListener('click', async () => {
    const val = dom.reverseJsonOutput.value;
    if (!val) return;
    await navigator.clipboard.writeText(val);
    showToast('JSON copied to clipboard!', 'success');
  });

  dom.btnLoadIntoEditor.addEventListener('click', () => {
    const val = dom.reverseJsonOutput.value;
    if (!val) return;
    state.rawJsonText = val;
    dom.jsonInput.value = val;
    dom.charCount.textContent = `${val.length.toLocaleString()} characters`;
    dom.modalReverse.classList.add('hidden');
    dom.tabPaste.click();
    processData();
    showToast('JSON loaded into main editor!', 'info');
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initDom();
  setupEvents();

  const initial = JSON.stringify(SAMPLES.nested, null, 2);
  state.rawJsonText = initial;
  dom.jsonInput.value = initial;
  dom.charCount.textContent = `${initial.length.toLocaleString()} characters`;
  processData();
});
