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
            border-radius: 0 !important; /* Square corners */
            box-shadow: none !important;  /* No glowy elements */
            text-shadow: none !important;
        }

        body {
            background-color: var(--bg-black);
            color: var(--text-white);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* LOGIN MODAL */
        #login-modal {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: #000000;
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .login-card {
            background: var(--bg-panel);
            border: 1px solid var(--border);
            padding: 36px 32px;
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
            color: var(--text-white);
            font-size: 0.9rem;
            outline: none;
            min-height: 44px;
            transition: border-color 0.15s ease;
        }

        .form-input:focus, select:focus, textarea:focus {
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
            min-height: 44px;
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
            padding: 10px 16px;
            font-size: 0.85rem;
            font-weight: 500;
            min-height: 44px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
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
            width: 250px;
            background: var(--bg-panel);
            border-right: 1px solid var(--border);
            padding: 24px 0;
            display: flex;
            flex-direction: column;
            transition: all 0.3s ease;
        }

        .brand-logo {
            padding: 0 24px;
            margin-bottom: 28px;
            display: flex;
            justify-content: space-between;
            align-items: center;
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
            padding: 14px 24px;
            color: var(--text-muted);
            font-size: 0.88rem;
            font-weight: 500;
            cursor: pointer;
            border-left: 3px solid transparent;
            min-height: 44px;
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
            gap: 16px;
        }

        .mobile-header-bar {
            display: none;
            justify-content: space-between;
            align-items: center;
            padding: 16px 20px;
            background: var(--bg-panel);
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
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
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

        /* DATA TABLES & FORMS */
        .table-wrapper {
            background: var(--bg-panel);
            border: 1px solid var(--border);
            padding: 20px;
            margin-bottom: 24px;
            overflow-x: auto; /* Enable touch scrolling for tables on mobile */
        }

        .data-table {
            width: 100%;
            border-collapse: collapse;
            min-width: 500px; /* Ensures readable columns */
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

        /* RESPONSIVE MOBILE BREAKPOINTS */
        @media (max-width: 768px) {
            .app-container {
                flex-direction: column;
            }
            .sidebar {
                width: 100%;
                border-right: none;
                border-bottom: 1px solid var(--border);
                padding: 12px 0;
                display: none; /* Toggled by menu button */
            }
            .sidebar.mobile-open {
                display: flex;
            }
            .mobile-header-bar {
                display: flex;
            }
            .main-content {
                padding: 16px;
            }
            .top-bar {
                flex-direction: column;
                align-items: flex-start;
                gap: 12px;
            }
            .grid-2 {
                grid-template-columns: 1fr;
            }
            .stats-grid {
                grid-template-columns: 1fr 1fr;
            }
            .chat-container {
                height: 450px;
            }
            .form-grid-inline {
                grid-template-columns: 1fr;
            }
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
            <div class="brand-logo" style="display:none;" id="sidebar-logo-mobile">
                <div class="brand-title">Navigation</div>
            </div>
            
            <ul class="nav-menu">
                <li class="nav-item active" onclick="switchTab('overview', this)"><i class="fa-solid fa-chart-line"></i> Overview</li>
                <li class="nav-item" onclick="switchTab('agent', this)"><i class="fa-solid fa-terminal"></i> AI Agent Chat</li>
                <li class="nav-item" onclick="switchTab('userbot', this)"><i class="fa-solid fa-paper-plane"></i> Userbot Controller</li>
                <li class="nav-item" onclick="switchTab('finance', this)"><i class="fa-solid fa-credit-card"></i> Finance & MPESA</li>
                <li class="nav-item" onclick="switchTab('media', this)"><i class="fa-solid fa-download"></i> Media & TikTok Hub</li>
                <li class="nav-item" onclick="switchTab('contacts', this)"><i class="fa-solid fa-users"></i> CRM Contacts</li>
                <li class="nav-item" onclick="switchTab('tasks', this)"><i class="fa-solid fa-check-square"></i> Tasks Board</li>
                <li class="nav-item" onclick="switchTab('memory', this)"><i class="fa-solid fa-database"></i> Memory & RAG</li>
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
                    <h1 id="tab-header-title">Dashboard Overview</h1>
                </div>
                <div style="display: flex; gap: 16px; align-items: center; width: 100%; justify-content: space-between;">
                    <div class="status-badge" id="bot-main-badge">ONLINE</div>
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
                        <h3 style="font-size: 1.1rem; margin-bottom: 8px;">Userbot Status & Configuration</h3>
                        <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 16px;">MTProto Pyrogram Userbot status on cloud server.</p>
                        <div style="font-family:'Fira Code', monospace; font-size:0.85rem; display:flex; flex-direction:column; gap:8px;">
                            <div>Status: <span id="ub-status-text" style="color:var(--accent-red);">Checking...</span></div>
                            <div>Session String Configured: <span id="ub-session-text">No</span></div>
                        </div>
                    </div>

                    <div class="table-wrapper">
                        <h3 style="font-size: 1.1rem; margin-bottom: 12px;">Send Direct Message as Userbot</h3>
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

                <div class="grid-2">
                    <div class="table-wrapper">
                        <h3 style="font-size: 1.1rem; margin-bottom: 12px;">Log New Transaction</h3>
                        <div class="form-group">
                            <label>Amount (KES)</label>
                            <input type="number" id="fin-add-amount" class="form-input" placeholder="500">
                        </div>
                        <div class="form-group">
                            <label>Vendor / Recipient</label>
                            <input type="text" id="fin-add-vendor" class="form-input" placeholder="Supermarket">
                        </div>
                        <div class="form-group">
                            <label>Category</label>
                            <input type="text" id="fin-add-cat" class="form-input" placeholder="Food">
                        </div>
                        <div class="form-group">
                            <label>Type</label>
                            <select id="fin-add-type" class="form-input">
                                <option value="expense">Expense</option>
                                <option value="income">Income</option>
                            </select>
                        </div>
                        <button class="btn-primary" onclick="submitFinanceLog()">Log Transaction</button>
                    </div>

                    <div class="table-wrapper">
                        <h3 style="font-size: 1.1rem; margin-bottom: 12px;">SMS Parser Simulator</h3>
                        <div class="form-group">
                            <label>Paste Raw MPESA / Bank SMS</label>
                            <textarea id="sms-raw-input" class="form-input" rows="5" placeholder="SDF897123 Confirmed. Ksh500 sent to John Doe..."></textarea>
                        </div>
                        <button class="btn-secondary" style="width:100%; text-align:center;" onclick="testSmsParse()">Parse SMS</button>
                        <div id="sms-parse-out" style="font-size: 0.8rem; margin-top: 10px; font-family:'Fira Code', monospace; color: var(--accent-blue);"></div>
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
                <div class="grid-2">
                    <div class="table-wrapper">
                        <h3 style="font-size: 1.1rem; margin-bottom: 12px;">YouTube Song Search</h3>
                        <div style="display: flex; gap: 10px;">
                            <input type="text" id="yt-search-query" class="form-input" placeholder="Song query e.g. Alan Walker Faded..." onkeydown="if(event.key==='Enter') searchYouTube()">
                            <button class="btn-primary" style="width: auto; padding: 0 20px;" onclick="searchYouTube()">Search</button>
                        </div>
                        <div id="yt-results" style="margin-top: 16px; display: flex; flex-direction: column; gap: 10px;"></div>
                    </div>

                    <div class="table-wrapper">
                        <h3 style="font-size: 1.1rem; margin-bottom: 12px;">TikTok, Instagram, Twitter Audio Extract</h3>
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
                    <h3 style="font-size: 1.1rem; margin-bottom: 16px;">CRM Contacts</h3>
                    
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
                    <h3 style="font-size: 1.1rem; margin-bottom: 16px;">Tasks Board</h3>
                    
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

            <!-- MEMORY TAB -->
            <div id="tab-memory" class="tab-panel">
                <div class="table-wrapper">
                    <h3 style="font-size: 1.1rem; margin-bottom: 16px;">System Memory & Facts</h3>
                    
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
            
            // Close mobile menu after switching tab
            const sidebar = document.getElementById('app-sidebar');
            sidebar.classList.remove('mobile-open');

            if(name === 'userbot') loadUserbotStatus();
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

        function submitFinanceLog() {
            const amt = parseFloat(document.getElementById('fin-add-amount').value);
            const v = document.getElementById('fin-add-vendor').value.trim();
            const c = document.getElementById('fin-add-cat').value.trim();
            const t = document.getElementById('fin-add-type').value;
            if(!amt || !v) return;
            
            fetch('/api/finance/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({amount: amt, vendor: v, category: c || 'General', transaction_type: t})
            }).then(() => loadFinance());
        }

        function testSmsParse() {
            const txt = document.getElementById('sms-raw-input').value.trim();
            if(!txt) return;
            
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
