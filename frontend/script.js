document.addEventListener('DOMContentLoaded', () => {
    // Disclaimer Banner Dismissal (reappears on page reload, no local storage)
    const closeBtn = document.getElementById('close-banner-btn');
    const banner = document.getElementById('disclaimer-banner');
    if (closeBtn && banner) {
        closeBtn.addEventListener('click', () => {
            banner.style.opacity = '0';
            banner.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                banner.style.display = 'none';
            }, 300);
        });
    }

    // Dashboard Data Loading (if backend API is running on port 5001 or local json)
    const scanBtn = document.getElementById('run-scan-btn');
    if (scanBtn) {
        scanBtn.addEventListener('click', () => {
            fetchResults();
        });
    }

    fetchResults();
});

async function fetchResults() {
    try {
        const resp = await fetch('http://localhost:5001/scan');
        if (resp.ok) {
            const data = await resp.json();
            if (data && data.results) {
                renderTable(data.results);
                updateSummary(data.results);
            }
        }
    } catch (e) {
        console.log('Backend API not currently reachable or scan not loaded yet.', e);
    }
}

function renderTable(results) {
    const tbody = document.getElementById('scan-results-body');
    if (!tbody) return;
    tbody.innerHTML = '';
    results.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${item.id || ''}</td>
            <td>${item.category || ''}</td>
            <td class="payload-cell"><span class="payload-text">${item.payload || ''}</span></td>
            <td><span class="badge ${item.verdict === 'PASS' ? 'badge-pass' : 'badge-fail'}">${item.verdict || ''}</span></td>
            <td>${item.reason || ''}</td>
        `;
        tbody.appendChild(tr);
    });
}

function updateSummary(results) {
    const totalEl = document.getElementById('stat-total');
    const passRateEl = document.getElementById('stat-pass-rate');
    const severityEl = document.getElementById('stat-severity');
    if (!totalEl || !passRateEl || !severityEl) return;

    const total = results.length;
    const passes = results.filter(r => r.verdict === 'PASS').length;
    const passRate = total > 0 ? Math.round((passes / total) * 100) : 0;

    totalEl.textContent = total;
    passRateEl.textContent = `${passRate}%`;

    let severity = 'Low';
    let sevClass = 'severity-low';
    if (passRate > 30) {
        severity = 'High';
        sevClass = 'severity-high';
    } else if (passRate >= 10) {
        severity = 'Medium';
        sevClass = 'severity-medium';
    }
    severityEl.textContent = severity;
    severityEl.className = `stat-val severity-badge ${sevClass}`;
}
