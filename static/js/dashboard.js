const root = document.getElementById('dashboard-root');
const ROLE = root.dataset.role;

let allObservations = [];
let charts = {};

const colors = {
  accent: '#ff9f43',
  accent2: '#ff6b6b',
  blue: '#4dabf7',
  green: '#51cf66',
  grid: 'rgba(255,255,255,0.06)',
  text: '#c9d1d9'
};

function fmtHour(iso) {
  const d = new Date(iso);
  return d.getHours();
}

async function loadObservations() {
  const params = new URLSearchParams();
  const category = document.getElementById('filter-category').value;
  const severity = document.getElementById('filter-severity').value;
  const reporter = document.getElementById('filter-reporter').value;
  if (category) params.set('category', category);
  if (severity) params.set('severity', severity);
  if (reporter) params.set('reporter', reporter);

  const res = await fetch('/api/observations?' + params.toString());
  allObservations = await res.json();
  populateReporterFilter();
  renderAll();
}

function populateReporterFilter() {
  const select = document.getElementById('filter-reporter');
  const current = select.value;
  const names = [...new Set(allObservations.map(o => o.reporter_name))].sort();
  select.innerHTML = '<option value="">All reporters</option>' +
    names.map(n => `<option value="${n}">${n}</option>`).join('');
  select.value = current;
}

function renderAll() {
  const total = allObservations.length;
  const nearMiss = allObservations.filter(o => o.category === 'Near Miss').length;
  const unsafeAct = allObservations.filter(o => o.category === 'Unsafe Act').length;
  const unsafeCond = allObservations.filter(o => o.category === 'Unsafe Condition').length;
  const high = allObservations.filter(o => o.severity === 'High').length;

  document.getElementById('kpi-total').textContent = total;
  document.getElementById('kpi-nearmiss').textContent = nearMiss;
  document.getElementById('kpi-unsafeact').textContent = unsafeAct;
  document.getElementById('kpi-unsafecond').textContent = unsafeCond;
  document.getElementById('kpi-high').textContent = high;
  document.getElementById('obs-count-label').textContent = `${total} observation${total===1?'':'s'} (filtered)`;
  document.getElementById('log-count').textContent = total;

  renderTimeChart();
  renderCategoryChart();
  renderSeverityChart();
  renderLocationsChart();
  renderHourlyChart();
  renderTopReporters();
  renderTable();
}

function destroyIfExists(key) {
  if (charts[key]) { charts[key].destroy(); delete charts[key]; }
}

function baseOptions(extra = {}) {
  return Object.assign({
    responsive: true,
    plugins: { legend: { display: false, labels: { color: colors.text } } },
    scales: {
      x: { ticks: { color: colors.text }, grid: { color: colors.grid } },
      y: { ticks: { color: colors.text }, grid: { color: colors.grid }, beginAtZero: true }
    }
  }, extra);
}

function renderTimeChart() {
  const byDate = {};
  allObservations.forEach(o => {
    const d = o.created_at || 'Unknown';
    byDate[d.split(',')[0]] = (byDate[d.split(',')[0]] || 0) + 1;
  });
  const labels = Object.keys(byDate);
  destroyIfExists('time');
  charts.time = new Chart(document.getElementById('chart-time'), {
    type: 'line',
    data: { labels, datasets: [{ data: Object.values(byDate), borderColor: colors.accent, backgroundColor: 'rgba(255,159,67,0.15)', fill: true, tension: 0.3 }] },
    options: baseOptions()
  });
}

function renderCategoryChart() {
  const cats = ['Unsafe Act', 'Unsafe Condition', 'Near Miss', 'LTI'];
  const counts = cats.map(c => allObservations.filter(o => o.category === c).length);
  destroyIfExists('category');
  charts.category = new Chart(document.getElementById('chart-category'), {
    type: 'doughnut',
    data: { labels: cats, datasets: [{ data: counts, backgroundColor: [colors.blue, colors.green, colors.accent, colors.accent2] }] },
    options: { plugins: { legend: { position: 'bottom', labels: { color: colors.text } } } }
  });
}

function renderSeverityChart() {
  const sevs = ['High', 'Medium', 'Low'];
  const counts = sevs.map(s => allObservations.filter(o => o.severity === s).length);
  destroyIfExists('severity');
  charts.severity = new Chart(document.getElementById('chart-severity'), {
    type: 'bar',
    data: { labels: sevs, datasets: [{ data: counts, backgroundColor: [colors.accent2, colors.accent, colors.green] }] },
    options: baseOptions()
  });
}

function renderLocationsChart() {
  const byLoc = {};
  allObservations.forEach(o => { const l = o.location || 'Not specified'; byLoc[l] = (byLoc[l] || 0) + 1; });
  const labels = Object.keys(byLoc);
  destroyIfExists('locations');
  charts.locations = new Chart(document.getElementById('chart-locations'), {
    type: 'bar',
    data: { labels, datasets: [{ data: Object.values(byLoc), backgroundColor: colors.blue }] },
    options: Object.assign(baseOptions(), { indexAxis: 'y' })
  });
}

function renderHourlyChart() {
  const hours = Array.from({length: 24}, (_, i) => i);
  const counts = hours.map(h => allObservations.filter(o => o.created_at_iso && fmtHour(o.created_at_iso) === h).length);
  destroyIfExists('hourly');
  charts.hourly = new Chart(document.getElementById('chart-hourly'), {
    type: 'bar',
    data: { labels: hours.map(h => h + 'h'), datasets: [{ data: counts, backgroundColor: colors.accent }] },
    options: baseOptions()
  });
}

function renderTopReporters() {
  const counts = {};
  allObservations.forEach(o => { counts[o.reporter_name] = (counts[o.reporter_name] || 0) + 1; });
  const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 6);
  const el = document.getElementById('top-reporters');
  el.innerHTML = sorted.map(([name, count], i) =>
    `<div class="reporter-row"><span class="reporter-rank">${i+1}</span><span class="reporter-name">${name}</span><span class="reporter-count">${count}</span></div>`
  ).join('') || '<p class="muted">No data yet.</p>';
}

function catClass(cat) {
  return 'tag-' + (cat || '').toLowerCase().replace(/\s+/g, '-');
}

function renderTable() {
  const tbody = document.getElementById('log-tbody');
  tbody.innerHTML = allObservations.map(o => `
    <tr>
      <td>${o.created_at || ''}</td>
      <td>${o.reporter_name || ''}</td>
      <td><span class="tag ${catClass(o.category)}">${o.category}</span></td>
      <td><span class="sev sev-${(o.severity||'').toLowerCase()}">${o.severity}</span></td>
      <td>${o.location || ''}</td>
      <td class="urdu-cell" dir="rtl">${o.urdu_script || ''}</td>
      <td class="translation-cell">${o.english_translation || ''}</td>
      <td>${o.status || ''}</td>
      <td class="row-actions">
        <a href="/api/observations/${o.id}/audio" target="_blank" title="Play audio">▶</a>
        <button onclick="openEdit(${o.id})" title="Edit">✎</button>
        ${ROLE === 'admin' ? `<button onclick="deleteObservation(${o.id})" title="Delete" class="danger">✕</button>` : ''}
      </td>
    </tr>
  `).join('') || '<tr><td colspan="9" class="empty">No observations match these filters.</td></tr>';
}

// ---- Filters ----
['filter-category', 'filter-severity', 'filter-reporter'].forEach(id =>
  document.getElementById(id).addEventListener('change', loadObservations)
);
document.getElementById('clear-filters-btn').addEventListener('click', () => {
  document.getElementById('filter-category').value = '';
  document.getElementById('filter-severity').value = '';
  document.getElementById('filter-reporter').value = '';
  loadObservations();
});

// ---- Edit modal ----
let editingId = null;
function openEdit(id) {
  const o = allObservations.find(x => x.id === id);
  editingId = id;
  document.getElementById('edit-reporter').value = o.reporter_name || '';
  document.getElementById('edit-category').value = o.category;
  document.getElementById('edit-severity').value = o.severity;
  document.getElementById('edit-location').value = o.location || '';
  document.getElementById('edit-status').value = o.status;
  document.getElementById('edit-modal').style.display = 'flex';
}
document.getElementById('edit-cancel-btn').addEventListener('click', () => {
  document.getElementById('edit-modal').style.display = 'none';
});
document.getElementById('edit-save-btn').addEventListener('click', async () => {
  const url = ROLE === 'admin' ? `/admin/observations/${editingId}` : `/hse/observations/${editingId}`;
  await fetch(url, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      reporter_name: document.getElementById('edit-reporter').value,
      category: document.getElementById('edit-category').value,
      severity: document.getElementById('edit-severity').value,
      location: document.getElementById('edit-location').value,
      status: document.getElementById('edit-status').value,
    })
  });
  document.getElementById('edit-modal').style.display = 'none';
  loadObservations();
});

// ---- Admin-only: delete / add observation / manage users ----
async function deleteObservation(id) {
  if (!confirm('Delete this observation and its audio? This cannot be undone.')) return;
  await fetch(`/admin/observations/${id}`, { method: 'DELETE' });
  loadObservations();
}

async function deleteUser(id) {
  if (!confirm('Delete this user account?')) return;
  await fetch(`/admin/users/${id}`, { method: 'DELETE' });
  window.location.reload();
}

if (ROLE === 'admin') {
  document.getElementById('add-observation-btn').addEventListener('click', () => {
    document.getElementById('add-obs-modal').style.display = 'flex';
  });
  document.getElementById('new-cancel-btn').addEventListener('click', () => {
    document.getElementById('add-obs-modal').style.display = 'none';
  });
  document.getElementById('new-save-btn').addEventListener('click', async () => {
    await fetch('/admin/observations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        reporter_name: document.getElementById('new-reporter').value,
        category: document.getElementById('new-category').value,
        severity: document.getElementById('new-severity').value,
        location: document.getElementById('new-location').value,
        english_translation: document.getElementById('new-english').value,
      })
    });
    document.getElementById('add-obs-modal').style.display = 'none';
    loadObservations();
  });

  document.getElementById('add-user-btn').addEventListener('click', () => {
    document.getElementById('add-user-modal').style.display = 'flex';
  });
  document.getElementById('new-user-cancel-btn').addEventListener('click', () => {
    document.getElementById('add-user-modal').style.display = 'none';
  });
  document.getElementById('new-user-save-btn').addEventListener('click', async () => {
    const res = await fetch('/admin/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: document.getElementById('new-user-name').value,
        username: document.getElementById('new-user-username').value,
        password: document.getElementById('new-user-password').value,
        role: document.getElementById('new-user-role').value,
      })
    });
    if (res.ok) { window.location.reload(); }
    else { const err = await res.json(); alert(err.error || 'Failed to create user'); }
  });
}

loadObservations();
