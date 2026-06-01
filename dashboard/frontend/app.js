// UI Elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const loading = document.getElementById('loading');
const loaderPhase = document.getElementById('loader-phase');
const resultContent = document.getElementById('result-content');
const resultsEmptyState = document.getElementById('results-empty-state');
const incidentsList = document.getElementById('incidents-list');

// Controls
const confSlider = document.getElementById('conf-slider');
const sliderValueDisplay = document.getElementById('slider-value-display');
const downloadBtn = document.getElementById('download-btn');

// Metrics
const systemClock = document.getElementById('system-clock');
const hudScans = document.getElementById('hud-scans');
const hudThreats = document.getElementById('hud-threats');
const hudAccuracy = document.getElementById('hud-accuracy');

let totalScansCount = 0;
let highestConfidence = 0;
let isUploading = false;

// Clock
function updateClock() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-US', { hour12: false });
    const dateStr = now.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' });
    systemClock.innerText = `${dateStr} | ${timeStr}`;
}
updateClock();
setInterval(updateClock, 1000);

// Drag and Drop
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = 'var(--primary)';
    dropZone.style.background = '#f8faff';
});

dropZone.addEventListener('dragleave', () => {
    dropZone.style.borderColor = '';
    dropZone.style.background = '';
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = '';
    dropZone.style.background = '';
    if (e.dataTransfer.files.length) {
        uploadImage(e.dataTransfer.files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
        uploadImage(e.target.files[0]);
    }
});

// Loading text cycle
function startLoadingCycle() {
    const phases = [
        "Uploading image...",
        "Processing image...",
        "Running model...",
        "Detecting objects...",
        "Analyzing results..."
    ];
    let i = 0;
    loaderPhase.innerText = phases[0];
    return setInterval(() => {
        i = (i + 1) % phases.length;
        loaderPhase.innerText = phases[i];
    }, 400);
}

// Class colors for bounding boxes
const CLASS_COLORS = {
    pistol:       '#22c55e',
    rifle:        '#f97316',
    shotgun:      '#ef4444',
    sniper_rifle: '#3b82f6',
    machine_gun:  '#a855f7',
    revolver:     '#eab308'
};
const DEFAULT_BOX_COLOR = '#6b7280';

// Draw bounding boxes on canvas overlay
function drawBoundingBoxes(detections, img) {
    const canvas = document.getElementById('bbox-canvas');
    if (!canvas || !img) return;

    const ctx = canvas.getContext('2d');
    const displayW = img.clientWidth;
    const displayH = img.clientHeight;
    const naturalW = img.naturalWidth;
    const naturalH = img.naturalHeight;

    canvas.width = displayW;
    canvas.height = displayH;
    ctx.clearRect(0, 0, displayW, displayH);

    if (!detections || detections.length === 0) return;

    const scaleX = displayW / naturalW;
    const scaleY = displayH / naturalH;

    detections.forEach(d => {
        const [x1, y1, x2, y2] = d.bbox;
        const sx = x1 * scaleX;
        const sy = y1 * scaleY;
        const sw = (x2 - x1) * scaleX;
        const sh = (y2 - y1) * scaleY;
        const color = CLASS_COLORS[d.class.toLowerCase()] || DEFAULT_BOX_COLOR;
        const conf = (d.confidence * 100).toFixed(0);
        const label = `${d.class.toUpperCase()} ${conf}%`;

        // Draw filled semi-transparent box
        ctx.fillStyle = color + '15';
        ctx.fillRect(sx, sy, sw, sh);

        // Draw box border
        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        ctx.strokeRect(sx, sy, sw, sh);

        // Draw corner brackets
        const cornerLen = Math.min(16, sw * 0.2, sh * 0.2);
        ctx.lineWidth = 4;
        ctx.beginPath();
        // Top-left
        ctx.moveTo(sx, sy + cornerLen); ctx.lineTo(sx, sy); ctx.lineTo(sx + cornerLen, sy);
        // Top-right
        ctx.moveTo(sx + sw - cornerLen, sy); ctx.lineTo(sx + sw, sy); ctx.lineTo(sx + sw, sy + cornerLen);
        // Bottom-left
        ctx.moveTo(sx, sy + sh - cornerLen); ctx.lineTo(sx, sy + sh); ctx.lineTo(sx + cornerLen, sy + sh);
        // Bottom-right
        ctx.moveTo(sx + sw - cornerLen, sy + sh); ctx.lineTo(sx + sw, sy + sh); ctx.lineTo(sx + sw, sy + sh - cornerLen);
        ctx.stroke();

        // Draw label background
        ctx.font = 'bold 13px Inter, sans-serif';
        const textMetrics = ctx.measureText(label);
        const labelW = textMetrics.width + 12;
        const labelH = 22;
        const labelY = sy > labelH + 4 ? sy - labelH - 4 : sy + 4;

        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.roundRect(sx, labelY, labelW, labelH, 4);
        ctx.fill();

        // Draw label text
        ctx.fillStyle = '#ffffff';
        ctx.fillText(label, sx + 6, labelY + 15);
    });
}

// Upload and detect
async function uploadImage(file) {
    if (isUploading) return;

    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/bmp', 'image/tiff', 'image/webp'];
    if (!validTypes.includes(file.type)) {
        alert('Please upload a valid image file (JPG, PNG, BMP, TIFF, or WEBP).');
        return;
    }

    // Validate file size (20MB max)
    if (file.size > 20 * 1024 * 1024) {
        alert('File is too large. Maximum size is 20MB.');
        return;
    }

    isUploading = true;
    totalScansCount++;
    hudScans.innerText = totalScansCount;

    const formData = new FormData();
    formData.append('file', file);

    loading.classList.remove('hidden');
    resultContent.classList.add('hidden');
    resultsEmptyState.classList.add('hidden');

    const loadingInterval = startLoadingCycle();
    const startTime = performance.now();

    try {
        const currentConfVal = (confSlider.value / 100).toFixed(2);
        const res = await fetch(`/api/detect?conf=${currentConfVal}`, {
            method: 'POST',
            body: formData
        });

        if (!res.ok) {
            const errorData = await res.json().catch(() => ({}));
            throw new Error(errorData.detail || `Server error (${res.status})`);
        }
        const data = await res.json();

        clearInterval(loadingInterval);
        loading.classList.add('hidden');
        resultContent.classList.remove('hidden');

        const annotatedImg = document.getElementById('annotated-image');
        annotatedImg.src = data.annotated_image + "?t=" + Date.now();

        // Draw bounding boxes once image loads
        annotatedImg.onload = () => {
    const canvas = document.getElementById('bbox-canvas');
    if (canvas) {
        drawBoundingBoxes(data.detections, annotatedImg);
    }
};

        const latency = data.inference_time_ms || (performance.now() - startTime);
        document.getElementById('inf-time').innerText = latency.toFixed(0);
        document.getElementById('det-count').innerText = data.detections.length;

        const threatEvalCard = document.getElementById('threat-eval-card');
        const threatEvalBadge = document.getElementById('threat-eval-badge');

        if (data.detections.length > 0) {
            const maxConf = Math.max(...data.detections.map(d => d.confidence));
            if (maxConf > highestConfidence) {
                highestConfidence = maxConf;
            }
            hudAccuracy.innerText = (highestConfidence * 100).toFixed(1) + "%";

            threatEvalCard.className = "threat-assessment threat-high";
            threatEvalBadge.className = "assessment-badge badge-critical";
            threatEvalBadge.innerText = "THREAT DETECTED";
        } else {
            threatEvalCard.className = "threat-assessment";
            threatEvalBadge.className = "assessment-badge badge-clear";
            threatEvalBadge.innerText = "CLEAR";

            // Update accuracy display even when clear
            if (highestConfidence > 0) {
                hudAccuracy.innerText = (highestConfidence * 100).toFixed(1) + "%";
            }
        }

        // Build detection list using fragment for better performance
        const list = document.getElementById('detection-list');
        list.innerHTML = '';

        if (data.detections.length === 0) {
            const item = document.createElement('div');
            item.className = 'det-list-item';
            item.innerHTML = '<span>No objects detected</span><span>✓</span>';
            list.appendChild(item);
        } else {
            const fragment = document.createDocumentFragment();
            data.detections.forEach(d => {
                const displayClass = d.class.charAt(0).toUpperCase() + d.class.slice(1);
                const displayConf = (d.confidence * 100).toFixed(1);
                const item = document.createElement('div');
                item.className = 'det-list-item alert-threat';
                item.innerHTML = `
                    <span><strong>${displayClass}</strong></span>
                    <span style="color: var(--danger); font-weight: 600;">${displayConf}%</span>
                `;
                fragment.appendChild(item);
            });
            list.appendChild(fragment);
        }

        await fetchIncidents();

    } catch (err) {
        console.error(err);
        clearInterval(loadingInterval);
        loading.classList.add('hidden');
        resultsEmptyState.classList.remove('hidden');
        alert(err.message || "Connection interrupted.");
    } finally {
        isUploading = false;
        // Reset file input so re-uploading the same file works
        fileInput.value = '';
    }
}

// Fetch incidents
async function fetchIncidents() {
    try {
        const res = await fetch('/api/incidents');
        if (!res.ok) return;
        const data = await res.json();

        hudThreats.innerText = data.length;
        incidentsList.innerHTML = '';

        if (data.length === 0) {
            incidentsList.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">
                    No recent incidents.
                </div>
            `;
            return;
        }

        // Use slice to avoid mutating the original array
        const recentIncidents = data.slice().reverse().slice(0, 6);
        const fragment = document.createDocumentFragment();

        recentIncidents.forEach((inc, index) => {
            const isHighThreat = inc.max_confidence > 0.55;

            let displayTime = inc.time_str || '';
            if (inc.timestamp) {
                const dateObj = new Date(inc.timestamp * 1000);
                displayTime = dateObj.toLocaleTimeString('en-US', { hour12: false }) + " " + dateObj.toLocaleDateString();
            }

            const confPct = (inc.max_confidence * 100).toFixed(1);

            const card = document.createElement('div');
            card.className = `incident-card ${isHighThreat ? 'high-threat' : ''}`;

            card.innerHTML = `
                <div class="incident-header">
                    <strong>${inc.source}</strong>
                    <span>${displayTime}</span>
                </div>
                <div class="incident-body">
                    <span>${isHighThreat ? 'Firearm Detected' : 'Low Confidence'}</span>
                    <strong>${confPct}%</strong>
                </div>
                <div class="confidence-bar-container">
                    <div class="confidence-bar-fill" style="width: ${confPct}%"></div>
                </div>
            `;

            fragment.appendChild(card);
        });

        incidentsList.appendChild(fragment);
    } catch (err) {
        console.error("Failed to fetch logs:", err);
    }
}

// Initial load and auto-refresh
fetchIncidents();
setInterval(fetchIncidents, 6000);

// Slider
if (confSlider && sliderValueDisplay) {
    confSlider.addEventListener('input', () => {
        sliderValueDisplay.innerText = `${confSlider.value}%`;
    });
}

// Download
if (downloadBtn) {
    downloadBtn.addEventListener('click', () => {
        const annotatedImg = document.getElementById('annotated-image');
        if (annotatedImg && annotatedImg.src && annotatedImg.src.includes('/outputs/')) {
            const link = document.createElement('a');
            link.href = annotatedImg.src;
            const fileName = annotatedImg.src.split('/').pop().split('?')[0];
            link.download = `Analyzed_${fileName}`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } else {
            alert("No image available to download.");
        }
    });
}
