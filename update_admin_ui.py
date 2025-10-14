#!/usr/bin/env python3
"""
Script to add tab-based navigation and API key management to admin.html
This preserves all existing bot functionality and adds the API key section
"""

# Read the current admin.html
with open('app/static/admin.html', 'r') as f:
    content = f.read()

# Find where to insert tabs CSS (after existing styles, before </style>)
tabs_css = """
        /* Tabs */
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #ddd;
        }

        .tab {
            padding: 12px 24px;
            background: none;
            border: none;
            border-bottom: 3px solid transparent;
            cursor: pointer;
            font-size: 15px;
            font-weight: 500;
            color: #666;
            transition: all 0.2s;
        }

        .tab:hover {
            color: #0066CC;
        }

        .tab.active {
            color: #0066CC;
            border-bottom-color: #0066CC;
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        /* API Key specific styles */
        .api-key-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }

        .api-key-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .api-key-card h3 {
            font-size: 18px;
            margin-bottom: 10px;
        }

        .api-key-card .masked-key {
            font-family: 'Courier New', monospace;
            font-size: 12px;
            color: #666;
            background: #f5f5f5;
            padding: 8px;
            border-radius: 4px;
            margin: 10px 0;
        }

        .api-key-actions {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }

        .api-key-actions button {
            flex: 1;
            padding: 8px;
            font-size: 13px;
        }

        .api-key-option {
            margin: 15px 0;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 6px;
        }

        .api-key-option label {
            display: flex;
            align-items: center;
            gap: 10px;
            cursor: pointer;
            font-weight: 500;
        }

        .api-key-option input[type="radio"] {
            width: auto;
        }

        .api-key-option .option-content {
            margin-top: 10px;
            margin-left: 30px;
        }

        .api-key-option.selected {
            border-color: #0066CC;
            background: #f0f7ff;
        }
"""

# Insert tabs CSS before </style>
content = content.replace('    </style>', tabs_css + '    </style>')

# Update the header to include tabs
old_header = '''        <header>
            <h1>🤖 AI Bot Builder</h1>
            <button class="btn btn-primary" onclick="openCreateModal()">+ Create New Bot</button>
        </header>

        <div id="error-message" class="error" style="display: none;"></div>
        <div id="bots-container" class="bot-grid"></div>'''

new_header = '''        <header>
            <h1>🤖 AI Bot Builder</h1>
            <div id="header-actions">
                <button class="btn btn-primary" onclick="openCreateModal()">+ Create New Bot</button>
            </div>
        </header>

        <div class="tabs">
            <button class="tab active" onclick="switchTab('bots')">Bots</button>
            <button class="tab" onclick="switchTab('api-keys')">API Keys</button>
        </div>

        <div id="error-message" class="error" style="display: none;"></div>

        <!-- Bots Tab -->
        <div id="bots-tab" class="tab-content active">
            <div id="bots-container" class="bot-grid"></div>
        </div>

        <!-- API Keys Tab -->
        <div id="api-keys-tab" class="tab-content">
            <div style="margin-bottom: 20px;">
                <button class="btn btn-primary" onclick="openApiKeyModal()">+ Add API Key</button>
            </div>
            <div id="api-keys-container" class="api-key-grid"></div>
        </div>'''

content = content.replace(old_header, new_header)

# Add API key modal before the embed modal
api_key_modal = '''
    <!-- API Key Create/Edit Modal -->
    <div id="api-key-modal" class="modal">
        <div class="modal-content">
            <h2 id="api-key-modal-title">Add API Key</h2>
            <form id="api-key-form">
                <div class="form-group">
                    <label>Key Name *</label>
                    <input type="text" id="api-key-name" placeholder="e.g., Production Anthropic Key" required>
                    <small>A friendly name to identify this API key</small>
                </div>

                <div class="form-group">
                    <label>Provider *</label>
                    <select id="api-key-provider" required>
                        <option value="anthropic">Anthropic (Claude)</option>
                        <option value="openai">OpenAI (GPT)</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>API Key *</label>
                    <input type="password" id="api-key-value" placeholder="sk-ant-... or sk-..." required>
                    <small>Your actual API key from the provider</small>
                </div>

                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">Save API Key</button>
                    <button type="button" class="btn btn-secondary" onclick="closeApiKeyModal()">Cancel</button>
                </div>
            </form>
        </div>
    </div>

'''

# Find the embed modal and insert API key modal before it
embed_modal_start = '    <!-- Embed Code Modal -->'
content = content.replace(embed_modal_start, api_key_modal + embed_modal_start)

# Add JavaScript functions for API keys before the closing </script> tag
api_key_js = '''
        // ========================================
        // API KEY MANAGEMENT
        // ========================================

        let currentApiKeyId = null;

        function switchTab(tabName) {
            // Update tab buttons
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            event.target.classList.add('active');

            // Update tab content
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            document.getElementById(tabName + '-tab').classList.add('active');

            // Update header actions
            const headerActions = document.getElementById('header-actions');
            if (tabName === 'bots') {
                headerActions.innerHTML = '<button class="btn btn-primary" onclick="openCreateModal()">+ Create New Bot</button>';
                loadBots();
            } else if (tabName === 'api-keys') {
                headerActions.innerHTML = '<button class="btn btn-primary" onclick="openApiKeyModal()">+ Add API Key</button>';
                loadApiKeys();
            }
        }

        async function loadApiKeys() {
            try {
                const response = await fetch(`${API_BASE}/api/api-keys`);
                const apiKeys = await response.json();

                const container = document.getElementById('api-keys-container');

                if (apiKeys.length === 0) {
                    container.innerHTML = '<div class="loading">No API keys yet. Click "+ Add API Key" to create one.</div>';
                    return;
                }

                container.innerHTML = apiKeys.map(key => `
                    <div class="api-key-card">
                        <h3>${key.name}</h3>
                        <div class="bot-meta">
                            <span class="badge badge-provider">${key.provider}</span>
                        </div>
                        <div class="masked-key">${key.api_key}</div>
                        <div class="api-key-actions">
                            <button class="btn btn-secondary" onclick="editApiKey('${key.id}')">Edit</button>
                            <button class="btn btn-danger" onclick="deleteApiKey('${key.id}', '${key.name}')">Delete</button>
                        </div>
                    </div>
                `).join('');
            } catch (error) {
                showError('Failed to load API keys: ' + error.message);
            }
        }

        function openApiKeyModal() {
            currentApiKeyId = null;
            document.getElementById('api-key-modal-title').textContent = 'Add API Key';
            document.getElementById('api-key-form').reset();
            document.getElementById('api-key-value').placeholder = 'sk-ant-... or sk-...';
            document.getElementById('api-key-modal').style.display = 'block';
        }

        function closeApiKeyModal() {
            document.getElementById('api-key-modal').style.display = 'none';
            currentApiKeyId = null;
        }

        async function editApiKey(keyId) {
            try {
                const response = await fetch(`${API_BASE}/api/api-keys/${keyId}`);
                const key = await response.json();

                currentApiKeyId = keyId;
                document.getElementById('api-key-modal-title').textContent = 'Edit API Key';
                document.getElementById('api-key-name').value = key.name;
                document.getElementById('api-key-provider').value = key.provider;
                document.getElementById('api-key-value').value = '';
                document.getElementById('api-key-value').placeholder = 'Leave blank to keep current key';

                document.getElementById('api-key-modal').style.display = 'block';
            } catch (error) {
                showError('Failed to load API key: ' + error.message);
            }
        }

        async function deleteApiKey(keyId, keyName) {
            if (!confirm(`Are you sure you want to delete "${keyName}"?\\n\\nNote: Bots using this key will fail until you assign them a new key.`)) return;

            try {
                const response = await fetch(`${API_BASE}/api/api-keys/${keyId}`, {
                    method: 'DELETE'
                });

                if (!response.ok) throw new Error('Failed to delete API key');
                loadApiKeys();
            } catch (error) {
                showError('Failed to delete API key: ' + error.message);
            }
        }

        // API Key form submission
        document.getElementById('api-key-form').addEventListener('submit', async (e) => {
            e.preventDefault();

            const keyData = {
                name: document.getElementById('api-key-name').value,
                provider: document.getElementById('api-key-provider').value,
            };

            // Only include api_key if user entered a value
            const apiKeyValue = document.getElementById('api-key-value').value.trim();
            if (apiKeyValue) {
                keyData.api_key = apiKeyValue;
            }

            try {
                const url = currentApiKeyId
                    ? `${API_BASE}/api/api-keys/${currentApiKeyId}`
                    : `${API_BASE}/api/api-keys`;

                const method = currentApiKeyId ? 'PUT' : 'POST';

                const response = await fetch(url, {
                    method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(keyData)
                });

                if (!response.ok) throw new Error('Failed to save API key');

                closeApiKeyModal();
                loadApiKeys();
            } catch (error) {
                showError('Failed to save API key: ' + error.message);
            }
        });

        // Close modals when clicking outside
        window.onclick = function(event) {
            if (event.target.classList.contains('modal')) {
                event.target.style.display = 'none';
            }
        };

'''

# Insert before the last </script> tag
content = content.replace('    </script>\n</body>', api_key_js + '    </script>\n</body>')

# Write the updated content
with open('app/static/admin.html', 'w') as f:
    f.write(content)

print("✅ Admin UI updated successfully!")
print("✅ Added tabs for Bots and API Keys")
print("✅ Added API key management interface")
print("✅ Next: Update bot form to use API key dropdown")
