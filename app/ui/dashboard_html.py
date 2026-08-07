DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StanlOS — Universal AI OS & Bot Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&family=Inter:wght@300;400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        :root {
            --bg-dark: #07090E;
            --bg-card: rgba(15, 23, 42, 0.75);
            --bg-card-hover: rgba(30, 41, 59, 0.85);
            --border-glass: rgba(255, 255, 255, 0.08);
            --border-accent: rgba(6, 182, 212, 0.3);
            
            --primary: #06B6D4;
            --primary-glow: rgba(6, 182, 212, 0.4);
            --indigo: #6366F1;
            --indigo-glow: rgba(99, 102, 241, 0.4);
            --emerald: #10B981;
            --rose: #F43F5E;
            --amber: #F59E0B;
            
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --text-subtle: #64748B;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', sans-serif;
        }

        body {
            background-color: var(--bg-dark);
            color: var(--text-main);
            min-height: 100vh;
            overflow-x: hidden;
            background-image: 
                radial-gradient(circle at 15% 20%, rgba(6, 182, 212, 0.12) 0%, transparent 40%),
                radial-gradient(circle at 85% 80%, rgba(99, 102, 241, 0.12) 0%, transparent 40%);
        }

        /* --- LOGIN MODAL OVERLAY --- */
        #login-modal {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(7, 9, 14, 0.92);
            backdrop-filter: blur(16px);
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.4s ease;
        }

        .login-card {
            background: var(--bg-card);
            border: 1px solid var(--border-glass);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7), 0 0 40px var(--primary-glow);
            border-radius: 24px;
            padding: 40px;
            width: 100%;
            max-width: 440px;
            text-align: center;
            position: relative;
        }

        .login-card h2 {
            font-family: 'Outfit', sans-serif;
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #FFF 0%, var(--primary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }

        .login-card p {
            color: var(--text-muted);
            font-size: 0.9rem;
            margin-bottom: 28px;
        }

        .form-group {
            margin-bottom: 20px;
            text-align: left;
        }

        .form-group label {
            display: block;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-muted);
            margin-bottom: 8px;
        }

        .form-input {
            width: 100%;
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid var(--border-glass);
            border-radius: 12px;
            padding: 14px 16px;
            color: #FFF;
            font-size: 0.95rem;
            outline: none;
            transition: all 0.3s ease;
        }

        .form-input:focus {
            border-color: var(--primary);
            box-shadow: 0 0 15px var(--primary-glow);
        }

        .btn-primary {
            width: 100%;
            background: linear-gradient(135deg, var(--primary) 0%, var(--indigo) 100%);
            border: none;
            border-radius: 12px;
            padding: 14px;
            color: #FFF;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 20px var(--primary-glow);
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px var(--primary-glow);
        }

        /* --- DASHBOARD LAYOUT --- */
        .app-container {
            display: flex;
            min-height: 100vh;
        }

        /* SIDEBAR */
        .sidebar {
            width: 260px;
            background: rgba(15, 23, 42, 0.6);
            border-right: 1px solid var(--border-glass);
            backdrop-filter: blur(12px);
            padding: 24px;
            display: flex;
            flex-direction: column;
        }

        .brand-logo {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 36px;
        }

        .brand-icon {
            width: 42px;
            height: 42px;
            border-radius: 12px;
            background: linear-gradient(135deg, var(--primary), var(--indigo));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3rem;
            box-shadow: 0 0 15px var(--primary-glow);
        }

        .brand-title {
            font-family: 'Outfit', sans-serif;
            font-size: 1.4rem;
            font-weight: 800;
            letter-spacing: -0.5px;
        }

        .nav-menu {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .nav-item {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 12px 16px;
            border-radius: 12px;
            color: var(--text-muted);
            font-weight: 500;
            cursor: pointer;
            transition: all 0.25s ease;
        }

        .nav-item:hover, .nav-item.active {
            color: #FFF;
            background: rgba(255, 255, 255, 0.05);
            border-left: 3px solid var(--primary);
        }

        .nav-item.active {
            background: linear-gradient(90deg, rgba(6, 182, 212, 0.15) 0%, transparent 100%);
        }

        /* MAIN CONTENT AREA */
        .main-content {
            flex: 1;
            padding: 32px;
            overflow-y: auto;
        }

        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 32px;
        }

        .page-title h1 {
            font-family: 'Outfit', sans-serif;
            font-size: 1.8rem;
            font-weight: 700;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: var(--emerald);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background: var(--emerald);
            border-radius: 50%;
            box-shadow: 0 0 10px var(--emerald);
        }

        /* GRID METRICS */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 32px;
        }

        .stat-card {
            background: var(--bg-card);
            border: 1px solid var(--border-glass);
            border-radius: 16px;
            padding: 20px;
            backdrop-filter: blur(12px);
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-3px);
            border-color: var(--border-accent);
        }

        .stat-label {
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-bottom: 8px;
        }

        .stat-value {
            font-family: 'Outfit', sans-serif;
            font-size: 1.8rem;
            font-weight: 700;
        }

        /* TAB PANELS */
        .tab-panel {
            display: none;
        }
        .tab-panel.active {
            display: block;
        }

        /* CHAT TERMINAL MODULE */
        .chat-container {
            background: var(--bg-card);
            border: 1px solid var(--border-glass);
            border-radius: 20px;
            height: 600px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .chat-messages {
            flex: 1;
            padding: 24px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .msg-bubble {
            max-width: 80%;
            padding: 14px 18px;
            border-radius: 16px;
            font-size: 0.95rem;
            line-height: 1.5;
        }

        .msg-user {
            align-self: flex-end;
            background: linear-gradient(135deg, var(--indigo) 0%, var(--primary) 100%);
            color: #FFF;
            border-bottom-right-radius: 4px;
        }

        .msg-bot {
            align-self: flex-start;
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid var(--border-glass);
            color: var(--text-main);
            border-bottom-left-radius: 4px;
        }

        .chat-input-area {
            display: flex;
            gap: 12px;
            padding: 16px;
            background: rgba(15, 23, 42, 0.9);
            border-top: 1px solid var(--border-glass);
        }

        /* TABLES */
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
        }

        .data-table th, .data-table td {
            padding: 14px 16px;
            text-align: left;
            border-bottom: 1px solid var(--border-glass);
            font-size: 0.9rem;
        }

        .data-table th {
            color: var(--text-muted);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.75rem;
        }

        .tag {
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;

        }
        .tag-expense { background: rgba(244, 63, 94, 0.15); color: var(--rose); }
        .tag-income { background: rgba(16, 185, 129, 0.15); color: var(--emerald); }

        .hidden { display: none !important; }
    </style>
</head>
<body>

    <!-- AUTHENTICATION OVERLAY -->
    <div id="login-modal">
        <div class="login-card">
            <div class="brand-icon" style="margin: 0 auto 16px; width:56px; height:56px; font-size:1.6rem;">⚡</div>
            <h2>StanlOS Dashboard</h2>
            <p>Enter your Administrator credentials to continue</p>
            
            <div class="form-group">
                <label>Username / Email</label>
                <input type="text" id="login-username" class="form-input" placeholder="admin" value="admin">
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" id="login-password" class="form-input" placeholder="••••••••" value="admin123">
            </div>
            <button class="btn-primary" onclick="doLogin()">Log In to Console</button>
            <div id="login-err" style="color: var(--rose); font-size: 0.85rem; margin-top: 12px;"></div>
        </div>
    </div>

    <!-- MAIN APP WRAPPER -->
    <div class="app-container">
        
        <!-- SIDEBAR -->
        <aside class="sidebar">
            <div class="brand-logo">
                <div class="brand-icon">⚡</div>
                <div class="brand-title">StanlOS <span style="color: var(--primary); font-size:0.8rem;">V2</span></div>
            </div>
            
            <ul class="nav-menu">
                <li class="nav-item active" onclick="switchTab('overview', this)"><i class="fa-solid fa-chart-pie"></i> Overview</li>
                <li class="nav-item" onclick="switchTab('agent', this)"><i class="fa-solid fa-robot"></i> AI Agent Chat</li>
                <li class="nav-item" onclick="switchTab('finance', this)"><i class="fa-solid fa-wallet"></i> Finance & MPESA</li>
                <li class="nav-item" onclick="switchTab('media', this)"><i class="fa-solid fa-music"></i> YouTube & Media</li>
                <li class="nav-item" onclick="switchTab('contacts', this)"><i class="fa-solid fa-address-book"></i> CRM Contacts</li>
                <li class="nav-item" onclick="switchTab('tasks', this)"><i class="fa-solid fa-list-check"></i> Tasks Board</li>
                <li class="nav-item" onclick="switchTab('memory', this)"><i class="fa-solid fa-brain"></i> Memory & RAG</li>
                <li class="nav-item" onclick="switchTab('settings', this)"><i class="fa-solid fa-gear"></i> System Config</li>
            </ul>

            <div style="margin-top: auto; padding-top: 20px; border-top: 1px solid var(--border-glass);">
                <button class="btn-primary" style="background: rgba(244, 63, 94, 0.2); color: var(--rose);" onclick="doLogout()">Logout</button>
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
                    <div class="status-pill"><div class="status-dot"></div> SYSTEM ONLINE</div>
                    <div style="font-size: 0.9rem; color: var(--text-muted);" id="user-badge">Stanley (Admin)</div>
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

                <div style="background: var(--bg-card); border: 1px solid var(--border-glass); border-radius: 20px; padding: 24px; margin-top: 24px;">
                    <h3>⚡ Quick Agent Actions</h3>
                    <p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 6px;">Trigger autonomous system workflows directly.</p>
                    <div style="display: flex; gap: 12px; margin-top: 16px;">
                        <button class="btn-primary" style="width: auto; padding: 10px 20px;" onclick="quickAction('Log KES 500 for coffee')">Log Expense</button>
                        <button class="btn-primary" style="width: auto; padding: 10px 20px; background: var(--indigo);" onclick="quickAction('What is my financial summary?')">Check Financial Summary</button>
                    </div>
                </div>
            </div>

            <!-- AGENT CHAT TAB -->
            <div id="tab-agent" class="tab-panel">
                <div class="chat-container">
                    <div class="chat-messages" id="chat-box">
                        <div class="msg-bubble msg-bot">Hello Stanley! I am StanlOS, your autonomous AI assistant. How can I help you manage your finances, tasks, or system today?</div>
                    </div>
                    <div class="chat-input-area">
                        <input type="text" id="chat-input" class="form-input" placeholder="Type a message or instruction..." onkeydown="if(event.key==='Enter') sendAgentMessage()">
                        <button class="btn-primary" style="width: auto; padding: 0 24px;" onclick="sendAgentMessage()">Send</button>
                    </div>
                </div>
            </div>

            <!-- FINANCE TAB -->
            <div id="tab-finance" class="tab-panel">
                <div style="display: flex; gap: 20px; margin-bottom: 24px;">
                    <div class="stat-card" style="flex:1;">
                        <div class="stat-label">Total Income</div>
                        <div class="stat-value" style="color: var(--emerald);" id="fin-income">KES 0.00</div>
                    </div>
                    <div class="stat-card" style="flex:1;">
                        <div class="stat-label">Total Expenses</div>
                        <div class="stat-value" style="color: var(--rose);" id="fin-expense">KES 0.00</div>
                    </div>
                    <div class="stat-card" style="flex:1;">
                        <div class="stat-label">Net Balance</div>
                        <div class="stat-value" id="fin-net">KES 0.00</div>
                    </div>
                </div>

                <div style="background: var(--bg-card); border: 1px solid var(--border-glass); border-radius: 20px; padding: 24px;">
                    <h3>Logged MPESA & Financial Transactions</h3>
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
                <div style="background: var(--bg-card); border: 1px solid var(--border-glass); border-radius: 20px; padding: 24px;">
                    <h3>YouTube Songs & Audio Downloader</h3>
                    <div style="display: flex; gap: 12px; margin-top: 16px;">
                        <input type="text" id="yt-search-query" class="form-input" placeholder="Search song title e.g. Alan Walker Faded..." onkeydown="if(event.key==='Enter') searchYouTube()">
                        <button class="btn-primary" style="width: auto; padding: 0 24px;" onclick="searchYouTube()">Search</button>
                    </div>
                    <div id="yt-results" style="margin-top: 24px; display: flex; flex-direction: column; gap: 12px;"></div>
                </div>
            </div>

            <!-- CRM TAB -->
            <div id="tab-contacts" class="tab-panel">
                <div style="background: var(--bg-card); border: 1px solid var(--border-glass); border-radius: 20px; padding: 24px;">
                    <h3>Network Intelligence & CRM</h3>
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
                <div style="background: var(--bg-card); border: 1px solid var(--border-glass); border-radius: 20px; padding: 24px;">
                    <h3>System Tasks & Workflow</h3>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Task Title</th>
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
                <div style="background: var(--bg-card); border: 1px solid var(--border-glass); border-radius: 20px; padding: 24px;">
                    <h3>Long-term Memory & User Facts</h3>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Fact Key</th>
                                <th>Fact Value</th>
                                <th>Stored Date</th>
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
                <div style="background: var(--bg-card); border: 1px solid var(--border-glass); border-radius: 20px; padding: 24px;">
                    <h3>System Configuration</h3>
                    <p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 6px;">Live Environment Configuration</p>
                    <div style="margin-top: 16px; font-family:'Fira Code', monospace; font-size:0.85rem; color:var(--primary);">
                        <div>• Engine: FastAPI + Gunicorn UvicornWorker</div>
                        <div>• Telegram Bot: @stanlosbot</div>
                        <div>• AI Provider: Cloudflare Workers AI (Llama 3.1 8B)</div>
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
                    document.getElementById('login-err').innerText = data.detail || 'Login failed.';
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
            document.getElementById('tab-header-title').innerText = el.innerText;
            
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
                document.getElementById('txn-table-body').innerHTML = html || '<tr><td colspan="6">No transactions found</td></tr>';
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
                        <td><button onclick="toggleTask(${t.id})" class="btn-primary" style="padding:4px 12px; font-size:0.75rem;">Toggle</button></td>
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
                    html += `<div style="background:rgba(30,41,59,0.5); padding:16px; border-radius:12px; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <div style="font-weight:600;">${t.title}</div>
                            <div style="font-size:0.8rem; color:var(--text-muted);">${t.uploader} • ${t.duration_string}</div>
                        </div>
                        <a href="${t.webpage_url}" target="_blank" class="btn-primary" style="width:auto; padding:8px 16px; text-decoration:none; font-size:0.85rem;">View Track</a>
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
