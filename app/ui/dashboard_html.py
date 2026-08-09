DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StanlOS Financial & Control Console</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-dark: #0B0E14;
            --bg-card: #151921;
            --bg-input: #0E121A;
            --border: #1E2330;
            --border-hover: #2E3547;
            
            --text-main: #F3F4F6;
            --text-muted: #9CA3AF;
            --text-subtle: #6B7280;
            
            --primary-blue: #2563EB;
            --primary-blue-hover: #1D4ED8;
            --accent-green: #10B981;
            --accent-red: #EF4444;
            --accent-amber: #F59E0B;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', sans-serif;
            border-radius: 4px; /* Professional subtle rounded borders */
        }

        body {
            background-color: var(--bg-dark);
            color: var(--text-main);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* LOGIN MODAL */
        #login-modal {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: #06080C;
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .login-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            padding: 40px;
            width: 100%;
            max-width: 400px;
        }

        .login-card h2 {
            font-size: 1.4rem;
            font-weight: 700;
            color: var(--text-main);
            margin-bottom: 6px;
        }

        .login-card p {
            color: var(--text-muted);
            font-size: 0.85rem;
            margin-bottom: 24px;
        }

        .form-group {
            margin-bottom: 18px;
        }

        .form-group label {
            display: block;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-muted);
            margin-bottom: 6px;
        }

        .form-input, select, textarea {
            width: 100%;
            background: var(--bg-input);
            border: 1px solid var(--border);
            padding: 12px 14px;
            color: var(--text-main);
            font-size: 0.9rem;
            outline: none;
            min-height: 42px;
            transition: border-color 0.15s ease;
        }

        .form-input:focus, select:focus, textarea:focus {
            border-color: var(--primary-blue);
        }

        .btn-primary {
            width: 100%;
            background: var(--primary-blue);
            border: 1px solid var(--primary-blue);
            padding: 12px;
            color: #FFFFFF;
            font-weight: 600;
            font-size: 0.9rem;
            min-height: 42px;
            cursor: pointer;
            transition: background 0.15s ease;
        }

        .btn-primary:hover {
            background: var(--primary-blue-hover);
        }

        .btn-secondary {
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-main);
            padding: 10px 16px;
            font-size: 0.85rem;
            font-weight: 500;
            min-height: 42px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .btn-secondary:hover {
            border-color: var(--border-hover);
            background: #1A202C;
        }

        /* LAYOUT */
        .app-container {
            display: flex;
            min-height: 100vh;
        }

        /* SIDEBAR */
        .sidebar {
            width: 250px;
            background: var(--bg-card);
            border-right: 1px solid var(--border);
            padding: 24px 0;
            display: flex;
            flex-direction: column;
        }

        .brand-logo {
            padding: 0 24px;
            margin-bottom: 28px;
        }

        .brand-title {
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: -0.3px;
        }

        .brand-sub {
            font-size: 0.72rem;
            color: var(--text-subtle);
            font-family: 'Fira Code', monospace;
            margin-top: 2px;
        }

        .nav-menu {
            list-style: none;
            display: flex;
            flex-direction: column;
        }

        .nav-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 24px;
            color: var(--text-muted);
            font-size: 0.88rem;
            font-weight: 500;
            cursor: pointer;
            border-left: 3px solid transparent;
            min-height: 42px;
            transition: all 0.15s ease;
        }

        .nav-section-title {
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--text-subtle);
            padding: 16px 24px 6px 24px;
        }

        .nav-item:hover {
            color: var(--text-main);
            background: #1A202C;
        }

        .nav-item.active {
            color: var(--text-main);
            background: #1A202C;
            border-left-color: var(--primary-blue);
        }

        /* MAIN CONTENT */
        .main-content {
            flex: 1;
            padding: 32px;
            background: var(--bg-dark);
            overflow-y: auto;
        }

        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 20px;
            margin-bottom: 28px;
            border-bottom: 1px solid var(--border);
        }

        .mobile-header-bar {
            display: none;
            justify-content: space-between;
            align-items: center;
            padding: 16px 20px;
            background: var(--bg-card);
            border-bottom: 1px solid var(--border);
        }

        .page-title h1 {
            font-size: 1.4rem;
            font-weight: 700;
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: #061811;
            border: 1px solid var(--accent-green);
            color: var(--accent-green);
            padding: 4px 10px;
            font-size: 0.75rem;
            font-weight: 600;
            font-family: 'Fira Code', monospace;
        }

        /* STATS CARDS */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 28px;
        }

        .stat-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            padding: 20px;
        }

        .stat-label {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-muted);
            margin-bottom: 8px;
        }

        .stat-value {
            font-size: 1.7rem;
            font-weight: 700;
            font-family: 'Fira Code', monospace;
        }

        /* FINANCIAL DASHBOARD GRAPH CARDS */
        .chart-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            padding: 24px;
            margin-bottom: 24px;
        }

        .chart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .chart-title {
            font-size: 1.05rem;
            font-weight: 600;
        }

        /* TAB PANELS */
        .tab-panel {
            display: none;
        }
        .tab-panel.active {
            display: block;
        }

        /* CHAT CONTAINER */
        .chat-container {
            background: var(--bg-card);
            border: 1px solid var(--border);
            height: 550px;
            display: flex;
            flex-direction: column;
        }

        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 14px;
            background: var(--bg-dark);
        }

        .msg-bubble {
            max-width: 85%;
            padding: 12px 16px;
            font-size: 0.9rem;
            line-height: 1.5;
            border: 1px solid var(--border);
        }

        .msg-user {
            align-self: flex-end;
            background: var(--primary-blue);
            border-color: var(--primary-blue);
            color: #FFFFFF;
        }

        .msg-bot {
            align-self: flex-start;
            background: var(--bg-card);
            color: var(--text-main);
        }

        .chat-input-area {
            display: flex;
            gap: 10px;
            padding: 16px;
            background: var(--bg-card);
            border-top: 1px solid var(--border);
        }

        /* TABLES & WRAPPERS */
        .table-wrapper {
            background: var(--bg-card);
            border: 1px solid var(--border);
            padding: 20px;
            margin-bottom: 24px;
            overflow-x: auto;
        }

        .data-table {
            width: 100%;
            border-collapse: collapse;
            min-width: 500px;
        }

        .data-table th, .data-table td {
            padding: 12px 14px;
            text-align: left;
            border-bottom: 1px solid var(--border);
            font-size: 0.85rem;
        }

        .data-table th {
            color: var(--text-muted);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.72rem;
            letter-spacing: 0.5px;
        }

        .tag {
            padding: 2px 8px;
            font-size: 0.72rem;
            font-weight: 600;
            font-family: 'Fira Code', monospace;
            border: 1px solid transparent;
        }
        .tag-expense { border-color: var(--accent-red); color: var(--accent-red); background: #1C0F13; }
        .tag-income { border-color: var(--accent-green); color: var(--accent-green); background: #081C15; }

        .progress-bar-bg {
            background: var(--bg-dark);
            height: 8px;
            width: 100%;
            overflow: hidden;
            margin-top: 6px;
        }

        .progress-bar-fill {
            background: var(--primary-blue);
            height: 100%;
        }

        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        .form-grid-inline {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 10px;
            margin-bottom: 16px;
        }

        .hidden { display: none !important; }

        @media (max-width: 768px) {
            .app-container { flex-direction: column; }
            .sidebar { width: 100%; border-right: none; border-bottom: 1px solid var(--border); padding: 12px 0; display: none; }
            .sidebar.mobile-open { display: flex; }
            .mobile-header-bar { display: flex; }
            .main-content { padding: 16px; }
            .top-bar { flex-direction: column; align-items: flex-start; gap: 12px; }
            .grid-2 { grid-template-columns: 1fr; }
            .stats-grid { grid-template-columns: 1fr 1fr; }
        }
    </style>
</head>
<body>

    <!-- AUTHENTICATION OVERLAY -->
    <div id="login-modal">
        <div class="login-card">
            <h2>StanlOS Console</h2>
            <p>Administrator Sign In</p>
            
            <div class="form-group">
                <label>Username / Email</label>
                <input type="text" id="login-username" class="form-input" placeholder="admin@stanlos.app">
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" id="login-password" class="form-input" placeholder="••••••••">
            </div>
            <button class="btn-primary" onclick="doLogin()">Log In to Console</button>
            <div id="login-err" style="color: var(--accent-red); font-size: 0.8rem; margin-top: 12px;"></div>
        </div>
    </div>

    <!-- MOBILE HEADER BAR -->
    <div class="mobile-header-bar">
        <div>
            <div class="brand-title">StanlOS</div>
            <div class="brand-sub">CONTROL CENTER V2.0</div>
        </div>
        <button class="btn-secondary" onclick="toggleMobileMenu()"><i class="fa-solid fa-bars"></i> Menu</button>
    </div>

    <!-- MAIN APP WRAPPER -->
    <div class="app-container">
        
        <!-- SIDEBAR -->
        <aside class="sidebar" id="app-sidebar">
            <div class="brand-logo">
                <div class="brand-title">StanlOS</div>
                <div class="brand-sub">FINANCIAL & SYSTEM CONSOLE</div>
            </div>
            
            <ul class="nav-menu">
                <div class="nav-section-title">Financial & Analytics</div>
                <li class="nav-item active" onclick="switchTab('finance', this)"><i class="fa-solid fa-credit-card"></i> Finance & MPESA</li>
                <li class="nav-item" onclick="switchTab('investments', this)"><i class="fa-solid fa-chart-pie"></i> Portfolio & Investments</li>
                <li class="nav-item" onclick="switchTab('overview', this)"><i class="fa-solid fa-chart-line"></i> System Overview</li>

                <div class="nav-section-title">Intelligence & AI</div>
                <li class="nav-item" onclick="switchTab('agent', this)"><i class="fa-solid fa-terminal"></i> AI Agent Chat</li>
                <li class="nav-item" onclick="switchTab('memory', this)"><i class="fa-solid fa-database"></i> Memory & RAG</li>
                <li class="nav-item" onclick="switchTab('contacts', this)"><i class="fa-solid fa-users"></i> CRM Contacts</li>
                <li class="nav-item" onclick="switchTab('userbot', this)"><i class="fa-solid fa-paper-plane"></i> Userbot Controller</li>

                <div class="nav-section-title">Utilities & Workload</div>
                <li class="nav-item" onclick="switchTab('gamification', this)"><i class="fa-solid fa-trophy"></i> Gamification & XP</li>
                <li class="nav-item" onclick="switchTab('media', this)"><i class="fa-solid fa-download"></i> Media & TikTok Hub</li>
                <li class="nav-item" onclick="switchTab('tools', this)"><i class="fa-solid fa-wrench"></i> Tools & Utilities</li>
                <li class="nav-item" onclick="switchTab('tasks', this)"><i class="fa-solid fa-check-square"></i> Tasks Board</li>
                <li class="nav-item" onclick="switchTab('apps', this)"><i class="fa-solid fa-cubes"></i> Connected Apps</li>

                <div class="nav-section-title">System Admin</div>
                <li class="nav-item" onclick="switchTab('settings', this)"><i class="fa-solid fa-sliders"></i> System Config</li>
            </ul>

            <div style="margin-top: auto; padding: 16px 24px 0;">
                <button class="btn-secondary" style="width: 100%; text-align: center;" onclick="doLogout()">Logout</button>
            </div>
        </aside>

        <!-- MAIN VIEW -->
        <main class="main-content">
            
            <!-- TOP BAR -->
            <div class="top-bar">
                <div class="page-title">
                    <h1 id="tab-header-title">Financial Control & Analytics</h1>
                </div>
                <div style="display: flex; gap: 16px; align-items: center;">
                    <div class="status-badge" id="bot-main-badge">SYSTEM ONLINE</div>
                    <div style="font-size: 0.85rem; color: var(--text-muted);" id="user-badge">Stanley (Admin)</div>
                </div>
            </div>

            <!-- FINANCE TAB (DEFAULT CORE FOCUS) -->
            <div id="tab-finance" class="tab-panel active">
                
                <!-- FINANCIAL SUMMARY METRICS -->
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">Net Balance</div>
                        <div class="stat-value" id="fin-net">KES 0.00</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Total Income</div>
                        <div class="stat-value" style="color: var(--accent-green);" id="fin-income">KES 0.00</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Total Expense</div>
                        <div class="stat-value" style="color: var(--accent-red);" id="fin-expense">KES 0.00</div>
                    </div>
                </div>

                <!-- SPENDING TRENDS & BREAKDOWN GRAPH -->
                <div class="grid-2">
                    <div class="chart-card">
                        <div class="chart-header">
                            <div class="chart-title">Income vs Expense Trends</div>
                            <span style="font-size:0.75rem; color:var(--text-muted); font-family:'Fira Code', monospace;">Real-time</span>
                        </div>
                        <div style="height: 240px; position: relative;">
                            <canvas id="financeChart"></canvas>
                        </div>
                    </div>

                    <div class="table-wrapper">
                        <div class="chart-header">
                            <div class="chart-title">Category Spending Breakdown</div>
                        </div>
                        <div id="cat-breakdown-container" style="display:flex; flex-direction:column; gap:16px;">
                            <div style="color:var(--text-muted); font-size:0.85rem;">Loading spending categories...</div>
                        </div>
                    </div>
                </div>

                <!-- VENDOR REASONS & SMS TESTER -->
                <div class="grid-2">
                    <div class="table-wrapper">
                        <h3 style="font-size: 1.05rem; margin-bottom: 16px;">Top Expense Reasons & Vendors</h3>
                        <div id="top-vendors-container" style="display:flex; flex-direction:column; gap:12px;">
                            <div style="color:var(--text-muted); font-size:0.85rem;">Loading vendors...</div>
                        </div>
                    </div>

                    <div class="table-wrapper">
                        <h3 style="font-size: 1.05rem; margin-bottom: 12px;">Log Transaction / SMS Webhook Parser</h3>
                        <div class="form-group">
                            <label>Paste MPESA / Bank SMS</label>
                            <textarea id="sms-raw-input" class="form-input" rows="3" placeholder="UH6H11X3U4 Confirmed. Ksh60.00 paid to THE SWEET SPOT HOTEL..."></textarea>
                        </div>
                        <button class="btn-primary" onclick="testSmsParse()">Process & Log SMS</button>
                        <div id="sms-parse-out" style="font-size: 0.8rem; margin-top: 10px; font-family:'Fira Code', monospace; color: var(--primary-blue);"></div>
                    </div>
                </div>

                <!-- TRANSACTION HISTORY SEARCH & TABLE -->
                <div class="table-wrapper">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; flex-wrap:wrap; gap:12px;">
                        <h3 style="font-size: 1.05rem;">Transaction Ledger</h3>
                        <div style="display:flex; gap:10px; width:100%; max-width:320px;">
                            <input type="text" id="txn-search" class="form-input" placeholder="Search transaction code or vendor..." onkeyup="filterTransactions()">
                        </div>
                    </div>

                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Transaction Code</th>
                                <th>Amount</th>
                                <th>Vendor / Recipient</th>
                                <th>Category</th>
                                <th>Type</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody id="txn-table-body">
                            <tr><td colspan="6" style="text-align:center; color:var(--text-muted);">Loading transactions...</td></tr>
                        </tbody>
                    </table>
                </div>

            </div>

            <!-- INVESTMENTS TAB -->
            <div id="tab-investments" class="tab-panel">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">Total Net Worth</div>
                        <div class="stat-value" style="color: var(--primary-blue);" id="inv-total">KES 0.00</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Total MMF Balance</div>
                        <div class="stat-value" style="color: var(--accent-green);" id="inv-mmf">KES 0.00</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Total Stock Value</div>
                        <div class="stat-value" style="color: var(--accent-amber);" id="inv-stock">KES 0.00</div>
                    </div>
                </div>

                <div class="grid-2">
                    <!-- MMF Section -->
                    <div class="table-wrapper">
                        <h3 style="font-size: 1.05rem; margin-bottom: 16px;">Money Market Funds</h3>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Fund Name</th>
                                    <th>Balance</th>
                                    <th>Yield %</th>
                                    <th>Daily Interest</th>
                                </tr>
                            </thead>
                            <tbody id="mmf-table-body">
                                <tr><td colspan="4" style="text-align:center; color:var(--text-muted);">Loading MMF data...</td></tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- Stocks Section -->
                    <div class="table-wrapper">
                        <h3 style="font-size: 1.05rem; margin-bottom: 16px;">NSE Stock Holdings</h3>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Ticker</th>
                                    <th>Shares</th>
                                    <th>Price</th>
                                    <th>Total Value</th>
                                </tr>
                            </thead>
                            <tbody id="stock-table-body">
                                <tr><td colspan="4" style="text-align:center; color:var(--text-muted);">Loading Stock data...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- OVERVIEW TAB -->
            <div id="tab-overview" class="tab-panel">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">CPU Utilization</div>
                        <div class="stat-value" id="stat-cpu">0.0%</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">RAM Usage</div>
                        <div class="stat-value" id="stat-ram">0.0%</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Logged Transactions</div>
                        <div class="stat-value" id="stat-txns">0</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Pending Tasks</div>
                        <div class="stat-value" id="stat-tasks">0</div>
                    </div>
                </div>

                <div class="table-wrapper">
                    <h3 style="font-size: 1.05rem; margin-bottom: 8px;">Quick Autonomous Actions</h3>
                    <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 16px;">Execute ReAct AI Agent commands directly.</p>
                    <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                        <button class="btn-secondary" onclick="quickAction('Log KES 500 for coffee')">Log Expense</button>
                        <button class="btn-secondary" onclick="quickAction('What is my financial summary?')">Check Financial Summary</button>
                    </div>
                </div>
            </div>

            <!-- AGENT CHAT TAB -->
            <div id="tab-agent" class="tab-panel">
                <div class="chat-container">
                    <div class="chat-messages" id="chat-box">
                        <div class="msg-bubble msg-bot">StanlOS Agent initialized. Ready to receive commands.</div>
                    </div>
                    <div class="chat-input-area">
                        <input type="text" id="chat-input" class="form-input" placeholder="Type instruction..." onkeydown="if(event.key==='Enter') sendAgentMessage()">
                        <button class="btn-primary" style="width: auto; padding: 0 20px;" onclick="sendAgentMessage()">Execute</button>
                    </div>
                </div>
            </div>

            <!-- USERBOT CONTROLLER TAB -->
            <div id="tab-userbot" class="tab-panel">
                <div class="grid-2">
                    <div class="table-wrapper">
                        <h3 style="font-size: 1.05rem; margin-bottom: 8px;">Userbot Status & Configuration</h3>
                        <div style="font-family:'Fira Code', monospace; font-size:0.85rem; display:flex; flex-direction:column; gap:8px; margin-top:12px;">
                            <div>Status: <span id="ub-status-text" style="color:var(--accent-red);">Checking...</span></div>
                            <div>Session String Configured: <span id="ub-session-text">No</span></div>
                        </div>
                    </div>

                    <div class="table-wrapper">
                        <h3 style="font-size: 1.05rem; margin-bottom: 12px;">Send Direct Message as Userbot</h3>
                        <div class="form-group">
                            <label>Recipient (@username or Phone)</label>
                            <input type="text" id="ub-recipient" class="form-input" placeholder="@username">
                        </div>
                        <div class="form-group">
                            <label>Message Content</label>
                            <textarea id="ub-msg" class="form-input" rows="3" placeholder="Message text..."></textarea>
                        </div>
                        <button class="btn-primary" onclick="sendUserbotMsg()">Send Message</button>
                        <div id="ub-send-res" style="font-size: 0.8rem; margin-top: 10px; font-family:'Fira Code', monospace;"></div>
                    </div>
                </div>
            </div>

            <!-- MEDIA TAB -->
            <div id="tab-media" class="tab-panel">
                <div class="grid-2">
                    <div class="table-wrapper">
                        <h3 style="font-size: 1.05rem; margin-bottom: 12px;">YouTube Song Search</h3>
                        <div style="display: flex; gap: 10px;">
                            <input type="text" id="yt-search-query" class="form-input" placeholder="Song query e.g. Alan Walker Faded..." onkeydown="if(event.key==='Enter') searchYouTube()">
                            <button class="btn-primary" style="width: auto; padding: 0 20px;" onclick="searchYouTube()">Search</button>
                        </div>
                        <div id="yt-results" style="margin-top: 16px; display: flex; flex-direction: column; gap: 10px;"></div>
                    </div>

                    <div class="table-wrapper">
                        <h3 style="font-size: 1.05rem; margin-bottom: 12px;">TikTok, Instagram, Twitter Audio Extract</h3>
                        <div class="form-group">
                            <label>Paste Media URL</label>
                            <input type="text" id="media-dl-url" class="form-input" placeholder="https://vm.tiktok.com/... or https://instagram.com/p/...">
                        </div>
                        <button class="btn-primary" onclick="downloadMediaStream()">Extract Audio Stream</button>
                        <div id="media-dl-res" style="font-size: 0.8rem; margin-top: 12px; font-family:'Fira Code', monospace;"></div>
                    </div>
                </div>
            </div>

            <!-- CRM TAB -->
            <div id="tab-contacts" class="tab-panel">
                <div class="table-wrapper">
                    <h3 style="font-size: 1.05rem; margin-bottom: 16px;">CRM Contacts</h3>
                    
                    <div class="form-grid-inline">
                        <input type="text" id="c-name" class="form-input" placeholder="Name">
                        <input type="text" id="c-company" class="form-input" placeholder="Company">
                        <input type="text" id="c-phone" class="form-input" placeholder="Phone">
                        <input type="text" id="c-email" class="form-input" placeholder="Email">
                        <input type="text" id="c-summary" class="form-input" placeholder="Context summary">
                    </div>
                    <button class="btn-primary" style="margin-bottom: 16px;" onclick="addContact()">Add Contact</button>

                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Company</th>
                                <th>Phone</th>
                                <th>Email</th>
                                <th>Score</th>
                            </tr>
                        </thead>
                        <tbody id="contacts-table-body">
                            <tr><td colspan="5" style="text-align:center; color:var(--text-muted);">Loading contacts...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- TASKS TAB -->
            <div id="tab-tasks" class="tab-panel">
                <div class="table-wrapper">
                    <h3 style="font-size: 1.05rem; margin-bottom: 16px;">Tasks Board</h3>
                    
                    <div class="form-grid-inline">
                        <input type="text" id="t-title" class="form-input" placeholder="Task Title">
                        <input type="text" id="t-desc" class="form-input" placeholder="Description">
                        <select id="t-prio" class="form-input">
                            <option value="1">Priority 1 (High)</option>
                            <option value="2">Priority 2</option>
                            <option value="3" selected>Priority 3 (Normal)</option>
                        </select>
                    </div>
                    <button class="btn-primary" style="margin-bottom: 16px;" onclick="addTask()">Create Task</button>

                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Priority</th>
                                <th>Status</th>
                                <th>Created</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody id="tasks-table-body">
                            <tr><td colspan="5" style="text-align:center; color:var(--text-muted);">Loading tasks...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- GAMIFICATION TAB -->
            <div id="tab-gamification" class="tab-panel">
                <div class="grid-2">
                    <div class="table-wrapper">
                        <h3 style="font-size: 1.05rem; margin-bottom: 16px;">Admin Gamification Profile</h3>
                        <div style="background:var(--bg-dark); padding:20px; border:1px solid var(--border); text-align:center; margin-bottom:16px;">
                            <div style="font-size:3rem; margin-bottom:10px;">🏆</div>
                            <h2 id="g-name" style="font-size:1.4rem; margin-bottom:5px;">Admin</h2>
                            <div style="color:var(--text-muted); font-size:0.9rem; margin-bottom:15px;">Level <span id="g-level" style="color:var(--accent-amber); font-weight:bold;">1</span></div>
                            <div style="font-size:2rem; font-weight:bold; font-family:'Fira Code', monospace; color:var(--primary-blue);" id="g-points">0 PTS</div>
                        </div>
                        <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:var(--text-muted); margin-bottom:5px;">
                            <span>Progress to Next Level</span>
                            <span id="g-next-tier">0 / 100 PTS</span>
                        </div>
                        <div class="progress-bar-bg" style="height:12px;">
                            <div class="progress-bar-fill" id="g-progress" style="width: 0%; background:var(--accent-amber);"></div>
                        </div>
                    </div>

                    <div class="table-wrapper">
                        <h3 style="font-size: 1.05rem; margin-bottom: 16px;">Global Leaderboard</h3>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Rank</th>
                                    <th>Player</th>
                                    <th>Score</th>
                                </tr>
                            </thead>
                            <tbody id="leaderboard-table-body">
                                <tr><td colspan="3" style="text-align:center; color:var(--text-muted);">Loading leaderboard...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- APPS TAB -->
            <div id="tab-apps" class="tab-panel">
                <div class="table-wrapper">
                    <h3 style="font-size: 1.05rem; margin-bottom: 16px;">Connected Integrations</h3>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>App ID</th>
                                <th>Auth Type</th>
                                <th>Status</th>
                                <th>Connected On</th>
                            </tr>
                        </thead>
                        <tbody id="apps-table-body">
                            <tr><td colspan="4" style="text-align:center; color:var(--text-muted);">Loading apps...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- MEMORY TAB -->
            <div id="tab-memory" class="tab-panel">
                <div class="grid-2">
                    <div class="table-wrapper">
                        <h3 style="font-size: 1.05rem; margin-bottom: 16px;">System Memory & Facts</h3>
                        
                        <div class="form-grid-inline">
                            <input type="text" id="m-key" class="form-input" placeholder="Fact Key e.g. favorite_food">
                            <input type="text" id="m-val" class="form-input" placeholder="Fact Value e.g. Pizza">
                        </div>
                        <button class="btn-primary" style="margin-bottom: 16px;" onclick="addMemory()">Store Memory</button>

                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Key</th>
                                    <th>Value</th>
                                    <th>Date</th>
                                </tr>
                            </thead>
                            <tbody id="memory-table-body">
                                <tr><td colspan="3" style="text-align:center; color:var(--text-muted);">Loading memories...</td></tr>
                            </tbody>
                        </table>
                    </div>

                    <div class="table-wrapper">
                        <h3 style="font-size: 1.05rem; margin-bottom: 16px;">RAG Documents</h3>
                        <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:16px;">Files and scraped web pages indexed by the AI for semantic search.</p>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>File Name</th>
                                    <th>Type</th>
                                    <th>Indexed On</th>
                                </tr>
                            </thead>
                            <tbody id="documents-table-body">
                                <tr><td colspan="3" style="text-align:center; color:var(--text-muted);">Loading documents...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- TOOLS TAB -->
            <div id="tab-tools" class="tab-panel">
                <div class="grid-2">
                    <div class="table-wrapper">
                        <h3 style="font-size: 1.05rem; margin-bottom: 12px;">Currency & FX Converter</h3>
                        <div class="form-group">
                            <label>Amount</label>
                            <input type="number" id="fx-amt" class="form-input" value="100">
                        </div>
                        <div class="form-grid-inline">
                            <div>
                                <label style="font-size:0.7rem; color:var(--text-muted);">From</label>
                                <select id="fx-from" class="form-input">
                                    <option value="USD" selected>USD</option>
                                    <option value="KES">KES</option>
                                    <option value="EUR">EUR</option>
                                    <option value="GBP">GBP</option>
                                </select>
                            </div>
                            <div>
                                <label style="font-size:0.7rem; color:var(--text-muted);">To</label>
                                <select id="fx-to" class="form-input">
                                    <option value="KES" selected>KES</option>
                                    <option value="USD">USD</option>
                                    <option value="EUR">EUR</option>
                                    <option value="TZS">TZS</option>
                                </select>
                            </div>
                        </div>
                        <button class="btn-primary" onclick="convertFx()">Convert FX</button>
                        <div id="fx-res" style="margin-top:12px; font-family:'Fira Code', monospace; font-size:0.85rem; color:var(--accent-green);"></div>
                    </div>

                    <div class="table-wrapper">
                        <h3 style="font-size: 1.05rem; margin-bottom: 12px;">Crypto Market Lookup</h3>
                        <div class="form-group">
                            <label>Symbol</label>
                            <select id="crypto-sym" class="form-input">
                                <option value="BTC" selected>Bitcoin (BTC)</option>
                                <option value="ETH">Ethereum (ETH)</option>
                                <option value="SOL">Solana (SOL)</option>
                                <option value="USDT">Tether (USDT)</option>
                            </select>
                        </div>
                        <button class="btn-primary" onclick="fetchCryptoPrice()">Check Price</button>
                        <div id="crypto-res" style="margin-top:12px; font-family:'Fira Code', monospace; font-size:0.85rem; color:var(--primary-blue);"></div>
                    </div>
                </div>

                <div class="grid-2">
                    <div class="table-wrapper">
                        <h3 style="font-size: 1.05rem; margin-bottom: 12px;">AI Text Translator</h3>
                        <div class="form-group">
                            <label>Text to Translate</label>
                            <textarea id="trans-text" class="form-input" rows="3" placeholder="Hello, welcome to StanlOS..."></textarea>
                        </div>
                        <div class="form-group">
                            <label>Target Language</label>
                            <input type="text" id="trans-lang" class="form-input" value="Swahili">
                        </div>
                        <button class="btn-primary" onclick="translateAiText()">Translate</button>
                        <div id="trans-res" style="margin-top:12px; font-size:0.9rem; background:var(--bg-dark); padding:12px; border:1px solid var(--border);"></div>
                    </div>

                    <div class="table-wrapper">
                        <h3 style="font-size: 1.05rem; margin-bottom: 12px;">Wikipedia Summary Search</h3>
                        <div class="form-group">
                            <label>Concept / Entity</label>
                            <input type="text" id="wiki-query" class="form-input" placeholder="Artificial Intelligence">
                        </div>
                        <button class="btn-primary" onclick="searchWiki()">Lookup Wikipedia</button>
                        <div id="wiki-res" style="margin-top:12px; font-size:0.85rem; color:var(--text-muted);"></div>
                    </div>
                </div>
            </div>

            <!-- SETTINGS TAB -->
            <div id="tab-settings" class="tab-panel">
                <div class="grid-2">
                    <div class="table-wrapper">
                        <h3 style="font-size: 1.05rem; margin-bottom: 12px;">System Configuration</h3>
                        <div style="font-family:'Fira Code', monospace; font-size:0.85rem; color:var(--text-muted); display:flex; flex-direction:column; gap:8px;">
                            <div>Engine: FastAPI / Gunicorn UvicornWorker</div>
                            <div>Telegram Bot: @stanlosbot</div>
                            <div>AI Model: Cloudflare Llama 3.1 8B</div>
                            <div>Database: SQLite Cloud Persistent Address</div>
                        </div>
                    </div>

                    <div class="table-wrapper">
                        <h3 style="font-size: 1.05rem; margin-bottom: 12px;">Admin Maintenance Operations</h3>
                        <div style="display:flex; gap:10px; flex-wrap:wrap; margin-bottom:12px;">
                            <button class="btn-secondary" onclick="adminVacuum()">Optimize SQLite Cloud DB</button>
                            <button class="btn-secondary" onclick="adminPurgeCache()">Purge Temp Storage Cache</button>
                        </div>
                        <div id="admin-maint-res" style="font-family:'Fira Code', monospace; font-size:0.85rem; color:var(--primary-blue);"></div>
                    </div>
                </div>
            </div>

        </main>
    </div>

    <script>
        let allTransactionsCache = [];
        let financeChartObj = null;

        function toggleMobileMenu() {
            const sidebar = document.getElementById('app-sidebar');
            sidebar.classList.toggle('mobile-open');
        }

        function doLogin() {
            const u = document.getElementById('login-username').value;
            const p = document.getElementById('login-password').value;
            
            fetch('/api/auth/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: u, password: p})
            })
            .then(res => res.json())
            .then(data => {
                if(data.success) {
                    localStorage.setItem('stanlos_token', data.token);
                    document.getElementById('login-modal').classList.add('hidden');
                    loadFinance();
                } else {
                    document.getElementById('login-err').innerText = data.detail || 'Invalid username or password.';
                }
            });
        }

        function doLogout() {
            localStorage.removeItem('stanlos_token');
            location.reload();
        }

        function switchTab(name, el) {
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
            el.classList.add('active');
            document.getElementById('tab-' + name).classList.add('active');
            document.getElementById('tab-header-title').innerText = el.innerText.trim();
            
            const sidebar = document.getElementById('app-sidebar');
            sidebar.classList.remove('mobile-open');

            if(name === 'finance') loadFinance();
            if(name === 'overview') loadStats();
            if(name === 'userbot') loadUserbotStatus();
            if(name === 'contacts') loadContacts();
            if(name === 'tasks') loadTasks();
            if(name === 'memory') { loadMemory(); loadDocuments(); }
            if(name === 'gamification') loadGamification();
            if(name === 'apps') loadApps();
        }

        function loadGamification() {
            fetch('/api/gamification/profile')
            .then(r => r.json())
            .then(d => {
                document.getElementById('g-name').innerText = d.name;
                document.getElementById('g-level').innerText = d.level;
                document.getElementById('g-points').innerText = d.points + ' PTS';
                document.getElementById('g-next-tier').innerText = d.points + ' / ' + d.next_tier_pts + ' PTS';
                document.getElementById('g-progress').style.width = d.progress_pct + '%';
            });

            fetch('/api/gamification/leaderboard')
            .then(r => r.json())
            .then(d => {
                let html = '';
                d.leaderboard.forEach(l => {
                    html += `<tr>
                        <td><b>#${l.rank}</b></td>
                        <td>${l.name}</td>
                        <td><code style="color:var(--primary-blue);">${l.points} PTS</code></td>
                    </tr>`;
                });
                document.getElementById('leaderboard-table-body').innerHTML = html || '<tr><td colspan="3">No players found</td></tr>';
            });
        }

        function loadApps() {
            fetch('/api/apps')
            .then(r => r.json())
            .then(d => {
                let html = '';
                d.forEach(a => {
                    html += `<tr>
                        <td><b>${a.app_id}</b></td>
                        <td>${a.auth_type || 'None'}</td>
                        <td><span class="status-badge" style="border:none; padding:2px 6px;">${a.status}</span></td>
                        <td>${a.created_at}</td>
                    </tr>`;
                });
                document.getElementById('apps-table-body').innerHTML = html || '<tr><td colspan="4" style="text-align:center;">No apps connected</td></tr>';
            });
        }

        function loadDocuments() {
            fetch('/api/documents')
            .then(r => r.json())
            .then(d => {
                let html = '';
                d.forEach(doc => {
                    html += `<tr>
                        <td><b>${doc.file_name}</b></td>
                        <td><span class="tag tag-expense" style="border-color:var(--primary-blue); color:var(--primary-blue);">${doc.file_type}</span></td>
                        <td>${doc.created_at}</td>
                    </tr>`;
                });
                document.getElementById('documents-table-body').innerHTML = html || '<tr><td colspan="3" style="text-align:center;">No documents uploaded</td></tr>';
            });
        }

        function loadFinance() {
            // Load Finance Summary
            fetch('/api/finance/summary')
            .then(r => r.json())
            .then(d => {
                document.getElementById('fin-income').innerText = 'KES ' + d.total_income.toLocaleString();
                document.getElementById('fin-expense').innerText = 'KES ' + d.total_expense.toLocaleString();
                document.getElementById('fin-net').innerText = 'KES ' + d.net_balance.toLocaleString();
                
                allTransactionsCache = d.recent_transactions;
                renderTransactionTable(allTransactionsCache);
            });

            // Load Finance Analytics
            fetch('/api/finance/analytics')
            .then(r => r.json())
            .then(d => {
                // Render Chart
                renderFinanceChart(d.chart);

                // Render Category Breakdown Progress Bars
                let catHtml = '';
                if(d.categories && d.categories.length > 0) {
                    d.categories.forEach(c => {
                        catHtml += `<div>
                            <div style="display:flex; justify-content:space-between; font-size:0.85rem;">
                                <span><b>${c.category}</b> (${c.count} txns)</span>
                                <span>KES ${c.amount.toLocaleString()} (${c.percentage}%)</span>
                            </div>
                            <div class="progress-bar-bg">
                                <div class="progress-bar-fill" style="width: ${Math.min(c.percentage, 100)}%;"></div>
                            </div>
                        </div>`;
                    });
                } else {
                    catHtml = '<div style="color:var(--text-muted); font-size:0.85rem;">No category data recorded</div>';
                }
                document.getElementById('cat-breakdown-container').innerHTML = catHtml;

                // Render Top Vendors
                let vendorHtml = '';
                if(d.top_vendors && d.top_vendors.length > 0) {
                    d.top_vendors.forEach(v => {
                        vendorHtml += `<div style="display:flex; justify-content:space-between; font-size:0.85rem; padding:8px 0; border-bottom:1px solid var(--border);">
                            <span><b>${v.vendor}</b></span>
                            <span style="font-family:'Fira Code', monospace; color:var(--accent-red);">KES ${v.amount.toLocaleString()}</span>
                        </div>`;
                    });
                } else {
                    vendorHtml = '<div style="color:var(--text-muted); font-size:0.85rem;">No vendor data recorded</div>';
                }
                document.getElementById('top-vendors-container').innerHTML = vendorHtml;
            });
        }

        function renderTransactionTable(txns) {
            let html = '';
            if(txns && txns.length > 0) {
                txns.forEach(t => {
                    html += `<tr>
                        <td><code>${t.code}</code></td>
                        <td>KES ${t.amount.toLocaleString()}</td>
                        <td>${t.vendor}</td>
                        <td>${t.category}</td>
                        <td><span class="tag ${t.type==='income'?'tag-income':'tag-expense'}">${t.type}</span></td>
                        <td>${t.date}</td>
                    </tr>`;
                });
            } else {
                html = '<tr><td colspan="6" style="text-align:center; color:var(--text-muted);">No transactions match your search</td></tr>';
            }
            document.getElementById('txn-table-body').innerHTML = html;
        }

        function filterTransactions() {
            const q = document.getElementById('txn-search').value.toLowerCase().trim();
            if(!q) {
                renderTransactionTable(allTransactionsCache);
                return;
            }
            const filtered = allTransactionsCache.filter(t => 
                t.code.toLowerCase().includes(q) || 
                t.vendor.toLowerCase().includes(q) || 
                t.category.toLowerCase().includes(q)
            );
            renderTransactionTable(filtered);
        }

        function renderFinanceChart(chartData) {
            const ctx = document.getElementById('financeChart').getContext('2d');
            if(financeChartObj) {
                financeChartObj.destroy();
            }
            financeChartObj = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: chartData.dates,
                    datasets: [
                        {
                            label: 'Income (KES)',
                            data: chartData.income,
                            backgroundColor: '#10B981',
                            borderColor: '#10B981',
                            borderWidth: 1
                        },
                        {
                            label: 'Expense (KES)',
                            data: chartData.expense,
                            backgroundColor: '#EF4444',
                            borderColor: '#EF4444',
                            borderWidth: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { grid: { color: '#1E2330' }, ticks: { color: '#9CA3AF' } },
                        y: { grid: { color: '#1E2330' }, ticks: { color: '#9CA3AF' } }
                    },
                    plugins: {
                        legend: { labels: { color: '#F3F4F6' } }
                    }
                }
            });
        }

        function testSmsParse() {
            const txt = document.getElementById('sms-raw-input').value.trim();
            if(!txt) return;
            
            document.getElementById('sms-parse-out').innerText = 'Processing SMS...';
            fetch('/api/finance/parse_sms', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({sms_text: txt})
            })
            .then(r => r.json())
            .then(d => {
                document.getElementById('sms-parse-out').innerText = JSON.stringify(d.result, null, 2);
                loadFinance();
            });
        }

        function loadStats() {
            fetch('/api/dashboard/stats')
            .then(r => r.json())
            .then(d => {
                document.getElementById('stat-cpu').innerText = d.cpu + '%';
                document.getElementById('stat-ram').innerText = d.ram + '%';
                document.getElementById('stat-txns').innerText = d.transactions_count;
                document.getElementById('stat-tasks').innerText = d.pending_tasks;
            });
        }

        function loadUserbotStatus() {
            fetch('/api/userbot/status')
            .then(r => r.json())
            .then(d => {
                const el = document.getElementById('ub-status-text');
                el.innerText = d.is_running ? 'RUNNING' : 'STOPPED';
                el.style.color = d.is_running ? 'var(--accent-green)' : 'var(--accent-red)';
                document.getElementById('ub-session-text').innerText = d.has_session_string ? 'Yes' : 'No';
            });
        }

        function sendUserbotMsg() {
            const rec = document.getElementById('ub-recipient').value.trim();
            const msg = document.getElementById('ub-msg').value.trim();
            if(!rec || !msg) return;
            
            document.getElementById('ub-send-res').innerText = 'Sending message...';
            
            fetch('/api/userbot/send', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({recipient: rec, message: msg})
            })
            .then(r => r.json())
            .then(d => {
                document.getElementById('ub-send-res').innerText = d.result || d.error;
            });
        }

        function downloadMediaStream() {
            const url = document.getElementById('media-dl-url').value.trim();
            if(!url) return;
            
            document.getElementById('media-dl-res').innerText = 'Downloading media stream...';
            
            fetch('/api/media/download', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({url: url})
            })
            .then(r => r.json())
            .then(d => {
                if(d.success) {
                    document.getElementById('media-dl-res').innerText = `Downloaded: ${d.title} (${d.artist})`;
                } else {
                    document.getElementById('media-dl-res').innerText = `Error: ${d.filepath}`;
                }
            });
        }

        function loadContacts() {
            fetch('/api/contacts')
            .then(r => r.json())
            .then(d => {
                let html = '';
                d.forEach(c => {
                    html += `<tr>
                        <td><b>${c.name}</b></td>
                        <td>${c.company}</td>
                        <td>${c.phone}</td>
                        <td>${c.email}</td>
                        <td>${c.score}</td>
                    </tr>`;
                });
                document.getElementById('contacts-table-body').innerHTML = html || '<tr><td colspan="5">No contacts found</td></tr>';
            });
        }

        function addContact() {
            const n = document.getElementById('c-name').value.trim();
            const comp = document.getElementById('c-company').value.trim();
            const p = document.getElementById('c-phone').value.trim();
            const e = document.getElementById('c-email').value.trim();
            const sum = document.getElementById('c-summary').value.trim();
            if(!n) return;
            
            fetch('/api/contacts/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name: n, company: comp, phone: p, email: e, context_summary: sum})
            }).then(() => loadContacts());
        }

        function loadTasks() {
            fetch('/api/tasks')
            .then(r => r.json())
            .then(d => {
                let html = '';
                d.forEach(t => {
                    html += `<tr>
                        <td><b>${t.title}</b></td>
                        <td>Priority ${t.priority}</td>
                        <td>${t.status}</td>
                        <td>${t.created_at}</td>
                        <td><button onclick="toggleTask(${t.id})" class="btn-secondary">Toggle</button></td>
                    </tr>`;
                });
                document.getElementById('tasks-table-body').innerHTML = html || '<tr><td colspan="5">No tasks found</td></tr>';
            });
        }

        function addTask() {
            const title = document.getElementById('t-title').value.trim();
            const desc = document.getElementById('t-desc').value.trim();
            const prio = parseInt(document.getElementById('t-prio').value);
            if(!title) return;
            
            fetch('/api/tasks/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({title: title, description: desc, priority: prio})
            }).then(() => loadTasks());
        }

        function toggleTask(id) {
            fetch('/api/tasks/toggle', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({task_id: id})
            }).then(() => loadTasks());
        }

        function loadMemory() {
            fetch('/api/memories')
            .then(r => r.json())
            .then(d => {
                let html = '';
                d.forEach(m => {
                    html += `<tr>
                        <td><code>${m.fact_key}</code></td>
                        <td>${m.fact_value}</td>
                        <td>${m.created_at}</td>
                    </tr>`;
                });
                document.getElementById('memory-table-body').innerHTML = html || '<tr><td colspan="3">No memories found</td></tr>';
            });
        }

        function addMemory() {
            const k = document.getElementById('m-key').value.trim();
            const v = document.getElementById('m-val').value.trim();
            if(!k || !v) return;
            
            fetch('/api/memories/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({fact_key: k, fact_value: v})
            }).then(() => loadMemory());
        }

        function sendAgentMessage() {
            const input = document.getElementById('chat-input');
            const msg = input.value.trim();
            if(!msg) return;
            
            const box = document.getElementById('chat-box');
            box.innerHTML += `<div class="msg-bubble msg-user">${msg}</div>`;
            input.value = '';
            box.scrollTop = box.scrollHeight;
            
            fetch('/api/agent/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: msg})
            })
            .then(r => r.json())
            .then(d => {
                box.innerHTML += `<div class="msg-bubble msg-bot">${d.response}</div>`;
                box.scrollTop = box.scrollHeight;
            });
        }

        function quickAction(msg) {
            switchTab('agent', document.querySelectorAll('.nav-item')[2]);
            document.getElementById('chat-input').value = msg;
            sendAgentMessage();
        }

        function searchYouTube() {
            const q = document.getElementById('yt-search-query').value.trim();
            if(!q) return;
            
            const res = document.getElementById('yt-results');
            res.innerHTML = '<div style="color:var(--text-muted);">Searching YouTube...</div>';
            
            fetch('/api/media/search', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query: q})
            })
            .then(r => r.json())
            .then(d => {
                let html = '';
                d.results.forEach(t => {
                    html += `<div style="background:var(--bg-dark); border:1px solid var(--border); padding:14px; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <div style="font-weight:600;">${t.title}</div>
                            <div style="font-size:0.8rem; color:var(--text-muted);">${t.uploader} • ${t.duration_string}</div>
                        </div>
                        <a href="${t.webpage_url}" target="_blank" class="btn-secondary" style="text-decoration:none;">View Link</a>
                    </div>`;
                });
                res.innerHTML = html || 'No tracks found.';
            });
        }

        function convertFx() {
            const amt = parseFloat(document.getElementById('fx-amt').value);
            const fc = document.getElementById('fx-from').value;
            const tc = document.getElementById('fx-to').value;
            fetch('/api/tools/convert_currency', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({amount: amt, from_currency: fc, to_currency: tc})
            })
            .then(r => r.json())
            .then(d => { document.getElementById('fx-res').innerText = d.result; });
        }

        function fetchCryptoPrice() {
            const sym = document.getElementById('crypto-sym').value;
            fetch('/api/tools/crypto_price', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({symbol: sym})
            })
            .then(r => r.json())
            .then(d => { document.getElementById('crypto-res').innerText = d.result; });
        }

        function translateAiText() {
            const txt = document.getElementById('trans-text').value.trim();
            const lang = document.getElementById('trans-lang').value.trim();
            if(!txt) return;
            document.getElementById('trans-res').innerText = 'Translating...';
            fetch('/api/tools/translate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text: txt, target_language: lang})
            })
            .then(r => r.json())
            .then(d => { document.getElementById('trans-res').innerText = d.result; });
        }

        function searchWiki() {
            const q = document.getElementById('wiki-query').value.trim();
            if(!q) return;
            document.getElementById('wiki-res').innerText = 'Searching Wikipedia...';
            fetch('/api/tools/wiki', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query: q})
            })
            .then(r => r.json())
            .then(d => { document.getElementById('wiki-res').innerText = d.result; });
        }

        function adminVacuum() {
            document.getElementById('admin-maint-res').innerText = 'Optimizing database indices...';
            fetch('/api/admin/vacuum', { method: 'POST' })
            .then(r => r.json())
            .then(d => { document.getElementById('admin-maint-res').innerText = d.message || d.error; });
        }

        function adminPurgeCache() {
            document.getElementById('admin-maint-res').innerText = 'Purging cache...';
            fetch('/api/admin/purge_cache', { method: 'POST' })
            .then(r => r.json())
            .then(d => { document.getElementById('admin-maint-res').innerText = d.message; });
        }

        // Auto load finance on startup
        if(localStorage.getItem('stanlos_token')) {
            document.getElementById('login-modal').classList.add('hidden');
            loadFinance();
        }
    </script>
</body>
</html>
"""
