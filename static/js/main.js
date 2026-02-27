/* =================================================================
   THEME MANAGER  —  dark / light / system
   ================================================================= */
const ThemeManager = (() => {
  const KEY = 'myapp-theme';
  const html = document.documentElement;

  function getSystemTheme() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function apply(pref) {
    const resolved = pref === 'system' ? getSystemTheme() : pref;
    html.setAttribute('data-theme', resolved);
    // update button states
    document.querySelectorAll('.theme-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.theme === pref);
    });
    // re-render charts if they exist
    if (typeof updateChartColors === 'function') updateChartColors();
  }

  function init() {
    const saved = localStorage.getItem(KEY) || 'dark';
    apply(saved);

    // React to OS preference change when "system" is selected
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      if ((localStorage.getItem(KEY) || 'dark') === 'system') apply('system');
    });
  }

  function set(pref) {
    localStorage.setItem(KEY, pref);
    apply(pref);
  }

  return { init, set, current: () => localStorage.getItem(KEY) || 'dark' };
})();

/* =================================================================
   SIDEBAR HAMBURGER  (mobile)
   ================================================================= */
function initSidebar() {
  const hamburger = document.getElementById('hamburger');
  const sidebar   = document.getElementById('sidebar');
  const overlay   = document.getElementById('sidebarOverlay');
  if (!hamburger || !sidebar) return;

  function open()  { sidebar.classList.add('open');  overlay.classList.add('show');  }
  function close() { sidebar.classList.remove('open'); overlay.classList.remove('show'); }

  hamburger.addEventListener('click', () => sidebar.classList.contains('open') ? close() : open());
  overlay.addEventListener('click', close);
  document.addEventListener('keydown', e => e.key === 'Escape' && close());
}

/* =================================================================
   THEME BUTTON WIRING
   ================================================================= */
function initThemeButtons() {
  document.querySelectorAll('.theme-btn').forEach(btn => {
    btn.addEventListener('click', () => ThemeManager.set(btn.dataset.theme));
  });
}

/* =================================================================
   ALERTS AUTO-DISMISS
   ================================================================= */
function initAlerts() {
  document.querySelectorAll('.alert').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity .5s ease, transform .5s ease';
      el.style.opacity = '0';
      el.style.transform = 'translateY(-6px)';
      setTimeout(() => el.closest('.alert-box')?.remove(), 500);
    }, 5000);
  });
}

/* =================================================================
   PASSWORD TOGGLE
   ================================================================= */
function togglePassword() {
  const input = document.getElementById('password');
  const icon  = document.getElementById('eye-icon');
  if (!input) return;
  if (input.type === 'password') {
    input.type = 'text';
    icon.innerHTML = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/>';
  } else {
    input.type = 'password';
    icon.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>';
  }
}

/* =================================================================
   REPORTS PAGE — Date presets & KPI data generation
   ================================================================= */
const ReportsData = (() => {
  // Generates deterministic-ish pseudo data for a date range
  function seed(n) { return ((n * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff; }

  function genDailyData(fromDate, toDate) {
    const days = [];
    const labels = [];
    const visits = [];
    const revenue = [];
    let d = new Date(fromDate);
    const end = new Date(toDate);
    let i = 0;
    while (d <= end) {
      labels.push(d.toLocaleDateString('pt-BR', { day:'2-digit', month:'2-digit' }));
      const s = seed(d.getTime() / 86400000 + 1);
      visits.push(Math.floor(300 + s * 1200));
      revenue.push(Math.floor(1000 + seed(i + 77) * 5000));
      d = new Date(d.getTime() + 86400000);
      i++;
    }
    return { labels, visits, revenue };
  }

  function genKPIs(fromDate, toDate) {
    const days = Math.max(1, Math.round((toDate - fromDate) / 86400000));
    const s = seed(days);
    return {
      visits:  (Math.floor(1200 * days * (0.5 + s * 0.8))).toLocaleString('pt-BR'),
      revenue: 'R$ ' + (Math.floor(350 * days * (0.5 + seed(days+3) * 0.8))).toLocaleString('pt-BR'),
      users:   (Math.floor(400 * days * (0.3 + seed(days+7) * 0.5))).toLocaleString('pt-BR'),
      conv:    (3.5 + seed(days + 11) * 2.5).toFixed(1) + '%',
      visitsDelta: (seed(days+1) > 0.4 ? '+' : '-') + Math.floor(seed(days+2)*15+1) + '%',
      revenueDelta:(seed(days+4) > 0.4 ? '+' : '-') + Math.floor(seed(days+5)*12+1) + '%',
      usersDelta:  (seed(days+8) > 0.5 ? '+' : '-') + Math.floor(seed(days+9)*8+1) + '%',
      convDelta:   (seed(days+12)> 0.5 ? '+' : '-') + (seed(days+13)*1.5).toFixed(1) + '%',
    };
  }

  return { genDailyData, genKPIs };
})();

/* =================================================================
   CHART.JS CHARTS  (only on reports page)
   ================================================================= */
let chartLine, chartDonut, chartBar, chartRadar;

function getChartColors() {
  const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
  return {
    text:    isDark ? '#9090bb' : '#52527a',
    grid:    isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.07)',
    tooltip: isDark ? '#10101c' : '#ffffff',
    accent:  '#6c63ff',
    green:   isDark ? '#22c55e' : '#16a34a',
    blue:    isDark ? '#38bdf8' : '#0284c7',
    orange:  isDark ? '#fb923c' : '#ea580c',
    red:     isDark ? '#f87171' : '#dc2626',
  };
}

function buildCharts(from, to) {
  if (!document.getElementById('chartLine')) return;

  const C   = getChartColors();
  const data = ReportsData.genDailyData(from, to);

  // Downsample labels to max 12 points for readability
  const step = Math.max(1, Math.ceil(data.labels.length / 12));
  const labels  = data.labels.filter((_, i) => i % step === 0);
  const visits  = data.visits.filter((_,  i) => i % step === 0);
  const revenue = data.revenue.filter((_,i) => i % step === 0);

  const baseOpts = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: C.tooltip,
        titleColor: C.text,
        bodyColor: C.text,
        borderColor: C.grid,
        borderWidth: 1,
        padding: 10,
        cornerRadius: 8,
      }
    }
  };

  /* ---- Line chart ---- */
  if (chartLine) chartLine.destroy();
  chartLine = new Chart(document.getElementById('chartLine'), {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Visitas',
          data: visits,
          borderColor: '#6c63ff',
          backgroundColor: 'rgba(108,99,255,0.12)',
          borderWidth: 2.5,
          fill: true,
          tension: 0.4,
          pointRadius: 3,
          pointHoverRadius: 6,
          pointBackgroundColor: '#6c63ff',
        },
        {
          label: 'Receita',
          data: revenue,
          borderColor: C.green,
          backgroundColor: 'rgba(34,197,94,0.08)',
          borderWidth: 2.5,
          fill: true,
          tension: 0.4,
          pointRadius: 3,
          pointHoverRadius: 6,
          pointBackgroundColor: C.green,
        }
      ]
    },
    options: {
      ...baseOpts,
      scales: {
        x: {
          ticks: { color: C.text, font: { size: 11 }, maxRotation: 45 },
          grid:  { color: C.grid },
          border:{ color: C.grid }
        },
        y: {
          ticks: { color: C.text, font: { size: 11 } },
          grid:  { color: C.grid },
          border:{ color: C.grid }
        }
      }
    }
  });

  /* ---- Donut chart ---- */
  const donutColors = ['#6c63ff','#22c55e','#38bdf8','#fb923c','#f87171'];
  const donutLabels = ['Orgânico','Direto','Social','E-mail','Pago'];
  const donutPcts   = [38, 27, 18, 11, 6];

  if (chartDonut) chartDonut.destroy();
  chartDonut = new Chart(document.getElementById('chartDonut'), {
    type: 'doughnut',
    data: {
      labels: donutLabels,
      datasets: [{
        data: donutPcts,
        backgroundColor: donutColors,
        borderColor: document.documentElement.getAttribute('data-theme') !== 'light' ? '#10101c' : '#fff',
        borderWidth: 3,
        hoverOffset: 8,
      }]
    },
    options: {
      ...baseOpts,
      cutout: '72%',
      plugins: {
        ...baseOpts.plugins,
        tooltip: {
          ...baseOpts.plugins.tooltip,
          callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed}%` }
        }
      }
    }
  });

  // Build donut legend
  const legend = document.getElementById('donutLegend');
  if (legend) {
    legend.innerHTML = donutLabels.map((l, i) =>
      `<div class="donut-legend-item">
        <div class="donut-legend-dot" style="background:${donutColors[i]}"></div>
        <span class="donut-legend-label">${l}</span>
        <span class="donut-legend-pct">${donutPcts[i]}%</span>
      </div>`
    ).join('');
  }

  /* ---- Bar chart ---- */
  const barLabels = ['Eletrônicos','Roupas','Casa','Livros','Esporte','Outros'];
  const barData   = [42, 28, 18, 14, 22, 10].map(v => v + Math.floor(Math.random()*15));
  const barData2  = [35, 22, 14, 18, 17,  8].map(v => v + Math.floor(Math.random()*12));

  if (chartBar) chartBar.destroy();
  chartBar = new Chart(document.getElementById('chartBar'), {
    type: 'bar',
    data: {
      labels: barLabels,
      datasets: [
        {
          label: 'Este período',
          data: barData,
          backgroundColor: 'rgba(108,99,255,0.75)',
          borderRadius: 6,
          borderSkipped: false,
        },
        {
          label: 'Anterior',
          data: barData2,
          backgroundColor: 'rgba(167,139,250,0.35)',
          borderRadius: 6,
          borderSkipped: false,
        }
      ]
    },
    options: {
      ...baseOpts,
      plugins: {
        ...baseOpts.plugins,
        legend: {
          display: true,
          labels: { color: C.text, font: { size: 11 }, boxWidth: 12, boxHeight: 12, borderRadius: 3 }
        }
      },
      scales: {
        x: {
          ticks: { color: C.text, font: { size: 11 } },
          grid:  { display: false },
          border:{ color: C.grid }
        },
        y: {
          ticks: { color: C.text, font: { size: 11 } },
          grid:  { color: C.grid },
          border:{ color: C.grid }
        }
      }
    }
  });

  /* ---- Radar chart ---- */
  const radarLabels = ['Conversão','Retenção','Satisfação','Velocidade','Qualidade','Suporte'];
  const radarMeta   = [80, 75, 85, 70, 90, 80];
  const radarReal   = [72, 68, 88, 65, 85, 74].map(v => v + Math.floor(Math.random()*10));

  if (chartRadar) chartRadar.destroy();
  chartRadar = new Chart(document.getElementById('chartRadar'), {
    type: 'radar',
    data: {
      labels: radarLabels,
      datasets: [
        {
          label: 'Meta',
          data: radarMeta,
          borderColor: 'rgba(108,99,255,0.8)',
          backgroundColor: 'rgba(108,99,255,0.12)',
          borderWidth: 2,
          pointBackgroundColor: '#6c63ff',
          pointRadius: 4,
        },
        {
          label: 'Realizado',
          data: radarReal,
          borderColor: 'rgba(34,197,94,0.8)',
          backgroundColor: 'rgba(34,197,94,0.1)',
          borderWidth: 2,
          pointBackgroundColor: C.green,
          pointRadius: 4,
        }
      ]
    },
    options: {
      ...baseOpts,
      plugins: {
        ...baseOpts.plugins,
        legend: {
          display: true,
          labels: { color: C.text, font: { size: 11 }, boxWidth: 12, boxHeight: 12 }
        }
      },
      scales: {
        r: {
          ticks:       { display: false },
          grid:        { color: C.grid },
          angleLines:  { color: C.grid },
          pointLabels: { color: C.text, font: { size: 11 } }
        }
      }
    }
  });
}

function updateChartColors() {
  // Just rebuild charts with current colors if they exist
  const from = window._currentFrom;
  const to   = window._currentTo;
  if (from && to) buildCharts(from, to);
}

function updateKPIs(from, to) {
  const kpis = ReportsData.genKPIs(from, to);
  const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
  set('kpiVisits',      kpis.visits);
  set('kpiRevenue',     kpis.revenue);
  set('kpiUsers',       kpis.users);
  set('kpiConv',        kpis.conv);
  set('kpiVisitsDelta', kpis.visitsDelta);
  set('kpiRevenueDelta',kpis.revenueDelta);
  set('kpiUsersDelta',  kpis.usersDelta);
  set('kpiConvDelta',   kpis.convDelta);

  // Update trend arrow classes
  [['kpiVisitsDelta','kpiVisits'],['kpiRevenueDelta','kpiRevenue'],['kpiUsersDelta','kpiUsers'],['kpiConvDelta','kpiConv']].forEach(([deltaId]) => {
    const el = document.getElementById(deltaId);
    if (!el) return;
    const parent = el.closest('.kpi-trend');
    if (!parent) return;
    const isUp = el.textContent.startsWith('+');
    parent.className = 'kpi-trend ' + (isUp ? 'kpi-trend-up' : 'kpi-trend-down');
    const svg = parent.querySelector('svg polyline');
    if (svg) svg.setAttribute('points', isUp ? '18 15 12 9 6 15' : '6 9 12 15 18 9');
  });
}

/* =================================================================
   DATE FILTER LOGIC
   ================================================================= */
function initDateFilter() {
  const inputFrom  = document.getElementById('dateFrom');
  const inputTo    = document.getElementById('dateTo');
  const applyBtn   = document.getElementById('applyFilter');
  const presetBtns = document.querySelectorAll('.preset-btn');
  if (!inputFrom) return; // not on reports page

  function setPreset(days) {
    const to   = new Date();
    const from = new Date(to.getTime() - (days - 1) * 86400000);
    inputFrom.value = from.toISOString().slice(0, 10);
    inputTo.value   = to.toISOString().slice(0, 10);
    presetBtns.forEach(b => b.classList.toggle('active', +b.dataset.preset === days));
    applyFilter();
  }

  function applyFilter() {
    const from = new Date(inputFrom.value + 'T00:00:00');
    const to   = new Date(inputTo.value   + 'T23:59:59');
    if (isNaN(from) || isNaN(to) || from > to) return;
    window._currentFrom = from;
    window._currentTo   = to;
    updateKPIs(from, to);
    buildCharts(from, to);
  }

  presetBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      presetBtns.forEach(b => b.classList.remove('active'));
      setPreset(+btn.dataset.preset);
    });
  });

  applyBtn.addEventListener('click', () => {
    presetBtns.forEach(b => b.classList.remove('active'));
    applyFilter();
  });

  inputFrom.addEventListener('change', () => presetBtns.forEach(b => b.classList.remove('active')));
  inputTo.addEventListener('change',   () => presetBtns.forEach(b => b.classList.remove('active')));

  // Initial load: 7 days
  setPreset(7);
}

/* =================================================================
   INIT
   ================================================================= */
document.addEventListener('DOMContentLoaded', () => {
  ThemeManager.init();
  initThemeButtons();
  initSidebar();
  initAlerts();
  initDateFilter();

  // Input focus effects
  document.querySelectorAll('.form-group input').forEach(input => {
    input.addEventListener('focus', () => input.closest('.form-group')?.classList.add('focused'));
    input.addEventListener('blur',  () => input.closest('.form-group')?.classList.remove('focused'));
  });
});
