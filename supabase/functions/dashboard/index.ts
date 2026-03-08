// Supabase Edge Function - Flyer Industries Dashboard
// Deploy with: supabase functions deploy dashboard

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'

const DASHBOARD_HTML = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Flyer Industries Dashboard</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #12141c;
      --surface: #1a1d27;
      --surface-2: #222636;
      --border: rgba(255,255,255,.08);
      --text: #e8eaf0;
      --text-muted: #8b90a0;
      --text-faint: #5a5f72;
      --primary: #5ba0d9;
      --primary-dim: rgba(91,160,217,.15);
      --green: #5B8A5E;
      --red: #C45B3B;
      --orange: #C46B3B;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Inter', sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
    }
    .app { display: flex; min-height: 100vh; }
    .sidebar {
      width: 260px;
      background: var(--surface);
      border-right: 1px solid var(--border);
      position: fixed;
      height: 100vh;
      display: flex;
      flex-direction: column;
      z-index: 100;
    }
    .sidebar-header {
      padding: 20px 16px;
      border-bottom: 1px solid var(--border);
    }
    .logo {
      font-family: 'Inter', sans-serif;
      font-size: 20px;
      font-weight: 800;
      font-style: italic;
      letter-spacing: 1px;
      text-transform: uppercase;
      background: linear-gradient(180deg, #fff 0%, #c0c0c0 50%, #808080 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .nav-section {
      padding: 20px 12px;
      flex: 1;
      overflow-y: auto;
    }
    .nav-label {
      font-size: 10px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: .08em;
      color: var(--text-faint);
      padding: 0 8px 8px;
    }
    .nav-btn {
      display: flex;
      align-items: center;
      gap: 10px;
      width: 100%;
      padding: 10px 12px;
      border-radius: 6px;
      font-size: 13px;
      color: var(--text-muted);
      background: none;
      border: none;
      cursor: pointer;
      transition: all 0.2s;
      margin-bottom: 2px;
    }
    .nav-btn:hover {
      background: var(--surface-2);
      color: var(--text);
    }
    .nav-btn.active {
      background: var(--primary-dim);
      color: var(--primary);
    }
    .main {
      flex: 1;
      margin-left: 260px;
      padding: 32px;
      min-height: 100vh;
    }
    .view { display: none; }
    .view.active { display: block; animation: fadeIn 0.3s ease; }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .header { margin-bottom: 28px; }
    .header h1 { font-size: 26px; font-weight: 600; margin-bottom: 4px; }
    .header p { color: var(--text-muted); font-size: 14px; }
    .card-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
      gap: 16px;
      margin-bottom: 28px;
    }
    .card {
      background: var(--surface-2);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 20px;
      cursor: pointer;
      transition: all 0.2s;
      position: relative;
    }
    .card:hover {
      border-color: rgba(255,255,255,.12);
      box-shadow: 0 4px 20px rgba(0,0,0,.3);
    }
    .card-badge {
      position: absolute;
      top: 12px;
      right: 12px;
      font-size: 10px;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 20px;
      background: var(--primary-dim);
      color: var(--primary);
    }
    .card-icon {
      width: 40px;
      height: 40px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      margin-bottom: 12px;
    }
    .card h3 { font-size: 15px; font-weight: 600; margin-bottom: 4px; }
    .card p { font-size: 12px; color: var(--text-muted); }
    .card-crafted { border-left: 3px solid var(--orange); }
    .card-crafted .card-icon { background: rgba(196,107,59,.1); }
    .card-ascend { border-left: 3px solid var(--green); }
    .card-ascend .card-icon { background: rgba(91,138,94,.1); }
    .card-taxmate { border-left: 3px solid var(--primary); }
    .card-taxmate .card-icon { background: var(--primary-dim); }
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin-bottom: 28px;
    }
    .stat {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 14px 16px;
    }
    .stat-label {
      font-size: 11px;
      color: var(--text-faint);
      text-transform: uppercase;
      letter-spacing: .04em;
      margin-bottom: 4px;
    }
    .stat-value { font-size: 20px; font-weight: 600; }
    .section {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 20px;
    }
    .section h2 { font-size: 15px; font-weight: 600; margin-bottom: 16px; }
    .list-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px;
      background: var(--surface-2);
      border: 1px solid var(--border);
      border-radius: 6px;
      margin-bottom: 8px;
      cursor: pointer;
      transition: all 0.2s;
    }
    .list-item:hover { background: var(--surface); }
    .list-icon {
      width: 36px;
      height: 36px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
    }
    .list-content { flex: 1; }
    .list-content h4 { font-size: 13px; font-weight: 600; margin-bottom: 2px; }
    .list-content p { font-size: 11px; color: var(--text-faint); }
    .badge {
      font-size: 9px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 20px;
    }
    .badge-green { background: rgba(91,138,94,.15); color: var(--green); }
    .badge-orange { background: rgba(196,107,59,.15); color: var(--orange); }
    .badge-red { background: rgba(196,91,59,.15); color: var(--red); }
    .back-btn {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      background: none;
      border: none;
      color: var(--text-muted);
      font-size: 13px;
      cursor: pointer;
      padding: 4px 0;
      margin-bottom: 16px;
      font-family: inherit;
    }
    .back-btn:hover { color: var(--primary); }
    .page-title { font-size: 22px; font-weight: 600; margin-bottom: 8px; }
    .page-sub { color: var(--text-muted); font-size: 14px; margin-bottom: 20px; }
    .tabs {
      display: flex;
      gap: 4px;
      border-bottom: 1px solid var(--border);
      margin-bottom: 20px;
    }
    .tab {
      padding: 10px 16px;
      font-size: 13px;
      font-weight: 500;
      color: var(--text-muted);
      background: none;
      border: none;
      border-bottom: 2px solid transparent;
      cursor: pointer;
      font-family: inherit;
      transition: all 0.2s;
    }
    .tab:hover { color: var(--text); }
    .tab.active { color: var(--primary); border-bottom-color: var(--primary); }
    .tab-content { display: none; }
    .tab-content.active { display: block; }
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin-bottom: 20px;
    }
    .kpi {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 16px;
    }
    .kpi-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;
    }
    .kpi-label {
      font-size: 10px;
      font-weight: 600;
      text-transform: uppercase;
      color: var(--text-faint);
    }
    .kpi-value { font-size: 22px; font-weight: 700; }
    .kpi-delta { font-size: 11px; font-weight: 600; }
    .kpi-delta.up { color: var(--green); }
    .kpi-delta.down { color: var(--red); }
    @media (max-width: 900px) {
      .sidebar { transform: translateX(-100%); }
      .sidebar.open { transform: translateX(0); }
      .main { margin-left: 0; padding: 80px 16px 100px; }
      .card-grid { grid-template-columns: 1fr; }
      .stats-grid { grid-template-columns: repeat(2, 1fr); }
      .kpi-grid { grid-template-columns: repeat(2, 1fr); }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside class="sidebar" id="sidebar">
      <div class="sidebar-header">
        <div class="logo">FLYER /</div>
      </div>
      <nav class="nav-section">
        <div class="nav-label">Businesses</div>
        <button class="nav-btn active" data-view="dashboard">
          <i class="fas fa-home"></i> Dashboard
        </button>
        <button class="nav-btn" data-view="crafted">
          <i class="fas fa-coffee"></i> Crafted
        </button>
        <button class="nav-btn" data-view="ascend">
          <i class="fas fa-building"></i> Ascend Estate
        </button>
        <div class="nav-label" style="margin-top: 20px;">Documents</div>
        <button class="nav-btn" data-view="pdfs">
          <i class="fas fa-file-pdf"></i> PDF Reports
        </button>
      </nav>
    </aside>

    <main class="main">
      <!-- Dashboard View -->
      <div class="view active" id="view-dashboard">
        <div class="header">
          <h1>Welcome, Tony!</h1>
          <p>Flyer Industries Command Center</p>
        </div>

        <div class="card-grid">
          <div class="card card-crafted" data-nav="crafted">
            <div class="card-icon">☕</div>
            <span class="card-badge">Active</span>
            <h3>Crafted</h3>
            <p>Coffee Shop — Berawa, Bali</p>
          </div>
          <div class="card card-ascend" data-nav="ascend">
            <div class="card-icon">🏡</div>
            <span class="card-badge">Active</span>
            <h3>Ascend Estate</h3>
            <p>Villa Management — Bali</p>
          </div>
          <div class="card card-taxmate" data-nav="taxmate">
            <div class="card-icon">📋</div>
            <span class="card-badge">Setup</span>
            <h3>TaxMate</h3>
            <p>Tax Services — Australia</p>
          </div>
        </div>

        <div class="stats-grid">
          <div class="stat">
            <div class="stat-label">Monthly Revenue</div>
            <div class="stat-value">IDR 24.9M</div>
          </div>
          <div class="stat">
            <div class="stat-label">Transactions</div>
            <div class="stat-value">240</div>
          </div>
          <div class="stat">
            <div class="stat-label">Active Projects</div>
            <div class="stat-value">2</div>
          </div>
          <div class="stat">
            <div class="stat-label">Properties</div>
            <div class="stat-value">3</div>
          </div>
        </div>

        <div class="section">
          <h2>Active Alerts</h2>
          <div class="list-item" data-nav="crafted">
            <div class="list-icon" style="background: rgba(196,91,59,.1); color: var(--red);">⚠️</div>
            <div class="list-content">
              <h4>Food Cost Variance</h4>
              <p>Banana consumption +60% over tolerance</p>
            </div>
            <span class="badge badge-red">Action</span>
          </div>
          <div class="list-item" data-nav="crafted">
            <div class="list-icon" style="background: rgba(196,107,59,.1); color: var(--orange);">📊</div>
            <div class="list-content">
              <h4>Mokapos Baseline</h4>
              <p>Monthly revenue data needs import</p>
            </div>
            <span class="badge badge-orange">Pending</span>
          </div>
        </div>
      </div>

      <!-- Crafted View -->
      <div class="view" id="view-crafted">
        <button class="back-btn" id="backFromCrafted">← Back</button>
        <h1 class="page-title">Crafted Coffee Shop</h1>
        <p class="page-sub">Berawa, Bali — Coffee Shop Operations</p>

        <div class="tabs">
          <button class="tab active" data-tab="crafted-kpi">Dashboard</button>
          <button class="tab" data-tab="crafted-tasks">Tasks</button>
          <button class="tab" data-tab="crafted-docs">Documents</button>
        </div>

        <div class="tab-content active" id="crafted-kpi">
          <div class="kpi-grid">
            <div class="kpi">
              <div class="kpi-header">
                <span class="kpi-label">Monthly Revenue</span>
              </div>
              <div class="kpi-value" style="color: var(--orange);">IDR 24.9M</div>
              <div class="kpi-delta up">↑ 12.5%</div>
            </div>
            <div class="kpi">
              <div class="kpi-header">
                <span class="kpi-label">Gross Margin</span>
              </div>
              <div class="kpi-value">47.8%</div>
              <div class="kpi-delta up">↑ 2.1%</div>
            </div>
            <div class="kpi">
              <div class="kpi-header">
                <span class="kpi-label">Food Cost</span>
              </div>
              <div class="kpi-value" style="color: var(--red);">32.4%</div>
              <div class="kpi-delta down">↑ 5.2%</div>
            </div>
            <div class="kpi">
              <div class="kpi-header">
                <span class="kpi-label">Transactions</span>
              </div>
              <div class="kpi-value">240</div>
              <div class="kpi-delta up">↑ 8.3%</div>
            </div>
          </div>

          <div class="section">
            <h2>February Performance</h2>
            <div style="display: flex; gap: 24px; padding: 16px; background: var(--surface-2); border-radius: 6px;">
              <div style="text-align: center;">
                <div style="font-size: 10px; color: var(--text-faint); text-transform: uppercase;">Revenue</div>
                <div style="font-size: 24px; font-weight: 700; color: var(--orange);">84.7%</div>
              </div>
              <div style="width: 1px; background: var(--border);"></div>
              <div style="text-align: center;">
                <div style="font-size: 10px; color: var(--text-faint); text-transform: uppercase;">Food Cost</div>
                <div style="font-size: 24px; font-weight: 700;">28.3%</div>
              </div>
            </div>
          </div>
        </div>

        <div class="tab-content" id="crafted-tasks">
          <div class="section">
            <h2>Daily Checklist</h2>
            <div style="padding: 12px 0; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 12px;">
              <div style="width: 20px; height: 20px; border-radius: 50%; background: var(--green); display: flex; align-items: center; justify-content: center; color: #fff; font-size: 11px;">✓</div>
              <span style="color: var(--text-muted); text-decoration: line-through;">Check Mokapos sales data</span>
            </div>
            <div style="padding: 12px 0; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 12px;">
              <div style="width: 20px; height: 20px; border-radius: 50%; border: 2px solid var(--border); cursor: pointer;"></div>
              <span>Review food cost variance</span>
              <span class="badge badge-red" style="margin-left: auto;">Urgent</span>
            </div>
          </div>
        </div>

        <div class="tab-content" id="crafted-docs">
          <div class="section">
            <h2>Documents</h2>
            <div class="list-item">
              <div class="list-icon" style="background: rgba(196,91,59,.1); color: var(--red);">📄</div>
              <div class="list-content">
                <h4>Daily Report - March 2026</h4>
                <p>Financial summary & analysis</p>
              </div>
              <span class="badge badge-orange">PDF</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Ascend View -->
      <div class="view" id="view-ascend">
        <button class="back-btn" id="backFromAscend">← Back</button>
        <h1 class="page-title">Ascend Estate</h1>
        <p class="page-sub">Villa Management & Real Estate</p>

        <div class="section">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
            <div>
              <div style="font-size: 18px; font-weight: 600;">Villa Panamera</div>
              <div style="font-size: 11px; color: var(--green); font-weight: 600; text-transform: uppercase;">Villa — Canggu</div>
            </div>
            <span class="badge badge-green">Active</span>
          </div>
          <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;">
            <div>
              <div style="font-size: 10px; color: var(--text-faint); text-transform: uppercase;">Bedrooms</div>
              <div>4</div>
            </div>
            <div>
              <div style="font-size: 10px; color: var(--text-faint); text-transform: uppercase;">Manager</div>
              <div>Be Bali Group</div>
            </div>
            <div>
              <div style="font-size: 10px; color: var(--text-faint); text-transform: uppercase;">Petty Cash</div>
              <div style="color: var(--green);">IDR 2.03M</div>
            </div>
          </div>
        </div>
      </div>

      <!-- PDF Reports View -->
      <div class="view" id="view-pdfs">
        <button class="back-btn" id="backFromPdfs">← Back</button>
        <h1 class="page-title">PDF Reports</h1>
        <p class="page-sub">Generated reports available for download</p>

        <div class="section">
          <h2>Available Reports</h2>
          <div class="list-item">
            <div class="list-icon" style="background: rgba(196,91,59,.1); color: var(--red);">📄</div>
            <div class="list-content">
              <h4>Daily Financial Report</h4>
              <p>Generated: Today • 11:00 PM</p>
            </div>
            <span class="badge badge-orange">PDF</span>
          </div>
          <div class="list-item">
            <div class="list-icon" style="background: rgba(196,91,59,.1); color: var(--red);">📄</div>
            <div class="list-content">
              <h4>Monthly Summary</h4>
              <p>Period: Feb 21 - Mar 7</p>
            </div>
            <span class="badge badge-orange">PDF</span>
          </div>
        </div>
      </div>

      <!-- TaxMate View -->
      <div class="view" id="view-taxmate">
        <button class="back-btn" id="backFromTaxmate">← Back</button>
        <h1 class="page-title">TaxMate</h1>
        <p class="page-sub">Tax Services for Australian Clients</p>
        <div style="padding: 40px; text-align: center; color: var(--text-faint);">
          Setup required — configuration pending
        </div>
      </div>
    </main>
  </div>

  <script>
    // Supabase configuration
    const SUPABASE_URL = 'https://kidbbtdnhtncxtaqqgcp.supabase.co';
    const SUPABASE_KEY = 'sb_publishable_9tYmqkG3w3UWYToiuzzoSw_KNib98xb';

    // Initialize Supabase
    let supabase;
    try {
      supabase = supabaseJs.createClient(SUPABASE_URL, SUPABASE_KEY);
    } catch(e) {
      console.log('Supabase client ready');
    }

    // Navigation function
    function navigateTo(viewName) {
      console.log('Navigating to:', viewName);

      // Hide all views
      document.querySelectorAll('.view').forEach(function(v) {
        v.classList.remove('active');
      });

      // Show target view
      const target = document.getElementById('view-' + viewName);
      if (target) {
        target.classList.add('active');
        window.scrollTo(0, 0);
      }

      // Update nav buttons
      document.querySelectorAll('.nav-btn').forEach(function(btn) {
        btn.classList.remove('active');
        if (btn.dataset.view === viewName) {
          btn.classList.add('active');
        }
      });

      // Save to localStorage
      try {
        localStorage.setItem('currentView', viewName);
      } catch(e) {}
    }

    // Tab switching
    function switchTab(tabBtn, tabId) {
      // Update tabs
      tabBtn.parentElement.querySelectorAll('.tab').forEach(function(t) {
        t.classList.remove('active');
      });
      tabBtn.classList.add('active');

      // Update content
      document.querySelectorAll('.tab-content').forEach(function(c) {
        c.classList.remove('active');
      });
      const content = document.getElementById(tabId);
      if (content) content.classList.add('active');
    }

    // Setup event listeners when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
      console.log('Dashboard loaded, setting up navigation');

      // Sidebar nav buttons
      document.querySelectorAll('.nav-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
          const view = this.dataset.view;
          if (view) navigateTo(view);
        });
      });

      // Dashboard cards
      document.querySelectorAll('[data-nav]').forEach(function(el) {
        el.addEventListener('click', function() {
          const view = this.dataset.nav;
          if (view) navigateTo(view);
        });
      });

      // Back buttons
      const backButtons = {
        'backFromCrafted': 'dashboard',
        'backFromAscend': 'dashboard',
        'backFromPdfs': 'dashboard',
        'backFromTaxmate': 'dashboard'
      };

      Object.keys(backButtons).forEach(function(id) {
        const btn = document.getElementById(id);
        if (btn) {
          btn.addEventListener('click', function() {
            navigateTo(backButtons[id]);
          });
        }
      });

      // Tab buttons
      document.querySelectorAll('.tab').forEach(function(tab) {
        tab.addEventListener('click', function() {
          const tabId = this.dataset.tab;
          if (tabId) switchTab(this, tabId);
        });
      });

      // Restore last view
      try {
        const saved = localStorage.getItem('currentView');
        if (saved && saved !== 'dashboard') {
          navigateTo(saved);
        }
      } catch(e) {}

      console.log('Navigation setup complete');
    });
  </script>
  <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
</body>
</html>`;

serve(async (req) => {
  return new Response(DASHBOARD_HTML, {
    headers: { 
      'Content-Type': 'text/html',
      'Cache-Control': 'no-cache'
    },
  })
})
