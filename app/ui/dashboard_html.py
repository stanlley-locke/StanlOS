DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StanlOS Console</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        :root {
            --bg-black: #09090B;
            --bg-panel: #18181B;
            --bg-input: #09090B;
            --border: #27272A;
            --border-hover: #3F3F46;
            
            --text-white: #FAFAFA;
            --text-muted: #A1A1AA;
            --text-subtle: #71717A;
            
            --accent-blue: #2563EB;
            --accent-blue-hover: #1D4ED8;
            --accent-green: #16A34A;
            --accent-red: #DC2626;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', sans-serif;
            border-radius: 0 !important; /* Square corners everywhere */
            box-shadow: none !important;  /* No glowy elements */
            text-shadow: none !important;
        }

        body {
            background-color: var(--bg-black);
            color: var(--text-white);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* LOGIN MODAL OVERLAY */
        #login-modal {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: #000000;
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .login-card {
            background: var(--bg-panel);
            border: 1px solid var(--border);
            padding: 40px;
            width: 100%;
            max-width: 400px;
        }

        .login-card h2 {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-white);
            margin-bottom: 6px;
        }

        .login-card p {
            color: var(--text-muted);
            font-size: 0.85rem;
            margin-bottom: 24px;
        }

        .credentials-notice {
            background: #09090B;
            border: 1px solid var(--border);
            padding: 12px;
            margin-bottom: 20px;
            font-family: 'Fira Code', monospace;
            font-size: 0.8rem;
            color: var(--accent-blue);
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

        .form-input {
            width: 100%;
            background: var(--bg-input);
            border: 1px solid var(--border);
            padding: 12px 14px;
            color: var(--text-white);
            font-size: 0.9rem;
            outline: none;
            transition: border-color 0.15s ease;
        }

        .form-input:focus {
            border-color: var(--accent-blue);
        }

        .btn-primary {
            width: 100%;
            background: var(--accent-blue);
            border: 1px solid var(--accent-blue);
            padding: 12px;
            color: #FFFFFF;
            font-weight: 600;
            font-size: 0.9rem;
            cursor: pointer;
            transition: background 0.15s ease;
        }

        .btn-primary:hover {
            background: var(--accent-blue-hover);
        }

        .btn-secondary {
            background: var(--bg-panel);
            border: 1px solid var(--border);
            color: var(--text-white);
            padding: 8px 16px;
            font-size: 0.85rem;
            font-weight: 500;
            cursor: pointer;
        }

        .btn-secondary:hover {
            border-color: var(--border-hover);
        }

        /* LAYOUT */
        .app-container {
            display: flex;
            min-height: 100vh;
        }

        /* SIDEBAR */
        .sidebar {
            width: 240px;
            background: var(--bg-panel);
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
            font-size: 1.2rem;
            font-weight: 700;
            letter-spacing: -0.3px;
        }

        .brand-sub {
            font-size: 0.75rem;
            color: var(--text-subtle);
            font-family: 'Fira Code', monospace;
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
            transition: all 0.15s ease;
        }

        .nav-item:hover {
            color: var(--text-white);
            background: #27272A;
        }

        .nav-item.active {
            color: var(--text-white);
            background: #27272A;
            border-left-color: var(--accent-blue);
        }

        /* MAIN CONTENT */
        .main-content {
            flex: 1;
            padding: 32px;
            background: var(--bg-black);
            overflow-y: auto;
        }

        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 24px;
            margin-bottom: 28px;
            border-bottom: 1px solid var(--border);
        }

        .page-title h1 {
            font-size: 1.5rem;
            font-weight: 700;
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #09090B;
            border: 1px solid var(--accent-green);
            color: var(--accent-green);
            padding: 4px 12px;
            font-size: 0.75rem;
            font-weight: 600;
            font-family: 'Fira Code', monospace;
        }

        /* STATS GRID */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 28px;
        }

        .stat-card {
            background: var(--bg-panel);
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
            font-size: 1.8rem;
            font-weight: 700;
            font-family: 'Fira Code', monospace;
        }

        /* TAB PANELS */
        .tab-panel {
            display: none;
        }
        .tab-panel.active {
            display: block;
        }

        /* CHAT MODULE */
        .chat-container {
            background: var(--bg-panel);
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
            background: var(--bg-black);
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
            background: var(--accent-blue);
            border-color: var(--accent-blue);
            color: #FFFFFF;
        }

        .msg-bot {
            align-self: flex-start;
            background: var(--bg-panel);
            color: var(--text-white);
        }

        .chat-input-area {
            display: flex;
            gap: 10px;
            padding: 16px;
            background: var(--bg-panel);
            border-top: 1px solid var(--border);
        }

        /* DATA TABLES */
        .table-wrapper {
            background: var(--bg-panel);
            border: 1px solid var(--border);
            padding: 20px;
        }

        .data-table {
            width: 100%;
            border-collapse: collapse;
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
        .tag-expense { border-color: var(--accent-red); color: var(--accent-red); }
        .tag-income { border-color: var(--accent-green); color: var(--accent-green); }

        .hidden { display: none !important; }
    </style>
</head>
<body>

    <!-- AUTHENTICATION OVERLAY -->
    <div id="login-modal">
        <div class="login-card">
            <h2>StanlOS Console</h2>
            <p>Administrator Sign In</p>
            
            <div class="credentials-notice">
                <div>Username: admin@stanlos.app</div>
                <div>Password: admin123</div>
            </div>
            
            <div class="form-group">
                <label>Username / Email</label>
                <input type="text" id="login-username" class="form-input" value="admin@stanlos.app">
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" id="login-password" class="form-input" value="admin123">
            </div>
            <button class="btn-primary" onclick="doLogin()">Log In to Console</button>
            <div id="login-err" style="color: var(--accent-red); font-size: 0.8rem; margin-top: 12px;"></div>
        </div>
    </div>

    <!-- MAIN APP WRAPPER -->
    <div class="app-container">
        
        <!-- SIDEBAR -->
        <aside class="sidebar">
            <div class="brand-logo">
                <div class="brand-title">StanlOS</div>
                <div class="brand-sub">CONTROL CENTER V2.0</div>
            </div>
            
            <ul class="nav-menu">
                <li class="nav-item active" onclick="switchTab('overview', this)"><i class="fa-solid fa-chart-line"></i> Overview</li>
                <li class="nav-item" onclick="switchTab('agent', this)"><i class="fa-solid fa-terminal"></i> AI Agent Chat</li>
                <li class="nav-item" onclick="switchTab('finance', this)"><i class="fa-solid fa-credit-card"></i> Finance & MPESA</li>
                <li class="nav-item" onclick="switchTab('media', this)"><i class="fa-solid fa-music"></i> YouTube & Media</li>
                <li class="nav-item" onclick="switchTab('contacts', this)"><i class="fa-solid fa-users"></i> CRM Contacts</li>
                <li class="nav-item" onclick="switchTab('tasks', this)"><i class="fa-solid fa-check-square"></i> Tasks Board</li>
                <li class="nav-item" onclick="switchTab('memory', this)"><i class="fa-solid fa-database"></i> Memory & RAG</li>
                <li class="nav-item" onclick="switchTab('settings', this)"><i class="fa-solid fa-sliders"></i> System Config</li>
            </ul>

            <div style="margin-top: auto; padding: 0 24px;">
                <button class="btn-secondary" style="width: 100%; text-align: center;" onclick="doLogout()">Logout</button>
            </div>
        </aside>

        <!-- MAIN VIEW -->
        <main class="main-content">
            
            <!-- TOP BAR -->
            <div class="top-bar">
                <div class="page-title">
                    <h1 id="tab-header-title">Dashboard Overview</h1>
                </div>
                <div style="display: flex; gap: 16px; align-items: center;">
                    <div class="status-badge">ONLINE</div>
                    <div style="font-size: 0.85rem; color: var(--text-muted);" id="user-badge">Stanley (Admin)</div>
                </div>
            </div>

            <!-- OVERVIEW TAB -->
            <div id="tab-overview" class="tab-panel active">
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
                    <h3 style="font-size: 1.1rem; margin-bottom: 8px;">Quick Actions</h3>
                    <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 16px;">Execute autonomous agent commands directly.</p>
                    <div style="display: flex; gap: 12px;">
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

            <!-- FINANCE TAB -->
            <div id="tab-finance" class="tab-panel">
                <div class="stats-grid" style="margin-bottom: 24px;">
                    <div class="stat-card">
                        <div class="stat-label">Total Income</div>
                        <div class="stat-value" style="color: var(--accent-green);" id="fin-income">KES 0.00</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Total Expense</div>
                        <div class="stat-value" style="color: var(--accent-red);" id="fin-expense">KES 0.00</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Net Balance</div>
                        <div class="stat-value" id="fin-net">KES 0.00</div>
                    </div>
                </div>

                <div class="table-wrapper">
                    <h3 style="font-size: 1.1rem; margin-bottom: 16px;">Transaction History</h3>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Code</th>
                                <th>Amount</th>
                                <th>Vendor</th>
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

            <!-- MEDIA TAB -->
            <div id="tab-media" class="tab-panel">
                <div class="table-wrapper">
                    <h3 style="font-size: 1.1rem; margin-bottom: 12px;">YouTube Media Search</h3>
                    <div style="display: flex; gap: 12px;">
                        <input type="text" id="yt-search-query" class="form-input" placeholder="Song query e.g. Alan Walker Faded..." onkeydown="if(event.key==='Enter') searchYouTube()">
                        <button class="btn-primary" style="width: auto; padding: 0 20px;" onclick="searchYouTube()">Search</button>
                    </div>
                    <div id="yt-results" style="margin-top: 20px; display: flex; flex-direction: column; gap: 10px;"></div>
                </div>
            </div>

            <!-- CRM TAB -->
            <div id="tab-contacts" class="tab-panel">
                <div class="table-wrapper">
                    <h3 style="font-size: 1.1rem; margin-bottom: 16px;">CRM Contacts</h3>
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
                    <h3 style="font-size: 1.1rem; margin-bottom: 16px;">Tasks Board</h3>
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

            <!-- MEMORY TAB -->
            <div id="tab-memory" class="tab-panel">
                <div class="table-wrapper">
                    <h3 style="font-size: 1.1rem; margin-bottom: 16px;">System Memory</h3>
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
            </div>

            <!-- SETTINGS TAB -->
            <div id="tab-settings" class="tab-panel">
                <div class="table-wrapper">
                    <h3 style="font-size: 1.1rem; margin-bottom: 12px;">System Configuration</h3>
                    <div style="font-family:'Fira Code', monospace; font-size:0.85rem; color:var(--text-muted); display:flex; flex-direction:column; gap:8px;">
                        <div>Engine: FastAPI / Gunicorn UvicornWorker</div>
                        <div>Telegram Bot: @stanlosbot</div>
                        <div>AI Model: Cloudflare Llama 3.1 8B</div>
                        <div>Database: SQLite Cloud / Local SQLite</div>
                    </div>
                </div>
            </div>

        </main>
    </div>

    <script>
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
                    loadStats();
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
            
            if(name === 'finance') loadFinance();
            if(name === 'contacts') loadContacts();
            if(name === 'tasks') loadTasks();
            if(name === 'memory') loadMemory();
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

        function loadFinance() {
            fetch('/api/finance/summary')
            .then(r => r.json())
            .then(d => {
                document.getElementById('fin-income').innerText = 'KES ' + d.total_income.toLocaleString();
                document.getElementById('fin-expense').innerText = 'KES ' + d.total_expense.toLocaleString();
                document.getElementById('fin-net').innerText = 'KES ' + d.net_balance.toLocaleString();
                
                let html = '';
                d.recent_transactions.forEach(t => {
                    html += `<tr>
                        <td><code>${t.code}</code></td>
                        <td>KES ${t.amount}</td>
                        <td>${t.vendor}</td>
                        <td>${t.category}</td>
                        <td><span class="tag ${t.type==='income'?'tag-income':'tag-expense'}">${t.type}</span></td>
                        <td>${t.date}</td>
                    </tr>`;
                });
                document.getElementById('txn-table-body').innerHTML = html || '<tr><td colspan="6">No transactions logged</td></tr>';
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
            switchTab('agent', document.querySelectorAll('.nav-item')[1]);
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
                    html += `<div style="background:var(--bg-black); border:1px solid var(--border); padding:14px; display:flex; justify-content:space-between; align-items:center;">
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

        // Auto check login session
        if(localStorage.getItem('stanlos_token')) {
            document.getElementById('login-modal').classList.add('hidden');
            loadStats();
        }
    </script>
</body>
</html>
"""
