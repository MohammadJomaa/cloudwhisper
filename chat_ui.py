#!/usr/bin/env python3
"""
CloudWhisper - AI-Powered AWS Chatbot Web UI
Built on Model Context Protocol (MCP) for seamless AI-cloud communication
"""

import os
import sys
import json
import threading
import time
import signal
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
import uuid
import yaml

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from chatbot.multi_cloud_chatbot import AWSChatbot

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cloudwhisper-secret-key-2024'

# Global chatbot instance
chatbot_manager = None

def signal_handler(signum, frame):
    """Handle shutdown signals to clean up resources."""
    print("\n🛑 Shutting down CloudWhisper Web UI...")
    if chatbot_manager:
        chatbot_manager.cleanup()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

class CloudWhisperManager:
    """Manages the CloudWhisper AI chatbot instance."""
    
    def __init__(self):
        self.chatbot = None
        self.is_initialized = False
        self.conversation_history = []
        self.current_account = "default"
        self.current_provider = "aws"  # AWS-only chatbot
    
    def initialize(self):
        """Initialize the chatbot."""
        try:
            self.chatbot = AWSChatbot()
            self.is_initialized = True
            return True
        except Exception as e:
            print(f"Error initializing chatbot: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources."""
        if self.chatbot:
            self.chatbot.stop_mcp_server()
    
    def switch_provider(self, provider):
        """Switch to a different cloud provider."""
        try:
            # Update the current provider
            self.current_provider = provider
            print(f"Switched to provider: {provider}")
            return True
        except Exception as e:
            print(f"Error switching provider: {e}")
            return False
    
    def switch_account(self, account_id):
        """Switch to a different account in the current provider."""
        try:
            # Update the current account
            self.current_account = account_id
            print(f"Switched to account: {account_id}")
            return True
        except Exception as e:
            print(f"Error switching account: {e}")
            return False
    
    def get_accounts(self):
        """Get available AWS accounts."""
        try:
            # Load accounts directly from config file
            config_path = "src/config/cloud_accounts.yaml"
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            
            accounts = []
            for account_id, account_data in config.get('aws_accounts', {}).items():
                accounts.append({
                    'id': account_id,
                    'name': account_data.get('name', account_id),
                    'region': account_data.get('region', 'Unknown'),
                    'description': account_data.get('description', '')
                })
            return accounts
        except Exception as e:
            print(f"Error getting accounts: {e}")
            return []
    
    def add_account(self, account_id, account_name, access_key, secret_key, region, description="", provider="aws"):
        """Add a new cloud account with direct credentials."""
        try:
            # Load current configuration
            config_path = "src/config/cloud_accounts.yaml"
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            
            # Ensure provider exists
            if provider not in config['cloud_providers']:
                config['cloud_providers'][provider] = {'accounts': {}}
            
            # Add new account
            config['cloud_providers'][provider]['accounts'][account_id] = {
                'name': account_name,
                'type': provider,
                'region': region,
                'access_key': access_key,
                'secret_key': secret_key,
                'description': description
            }
            
            # Save updated configuration
            with open(config_path, 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            
            return True
        except Exception as e:
            print(f"Error adding account: {e}")
            return False
    
    def remove_account(self, account_id, provider="aws"):
        """Remove a cloud account."""
        try:
            # Load current configuration
            config_path = "src/config/cloud_accounts.yaml"
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            
            # Remove account
            if provider in config['cloud_providers'] and account_id in config['cloud_providers'][provider]['accounts']:
                del config['cloud_providers'][provider]['accounts'][account_id]
                
                # Update default account if needed
                if config.get('default_account') == account_id and config.get('default_provider') == provider:
                    accounts = list(config['cloud_providers'][provider]['accounts'].keys())
                    if accounts:
                        config['default_account'] = accounts[0]
                    else:
                        config['default_account'] = 'default'
                
                # Save updated configuration
                with open(config_path, 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
                
                return True
            return False
        except Exception as e:
            print(f"Error removing account: {e}")
            return False
    
    def get_response(self, message):
        """Get response from the chatbot."""
        try:
            if not self.is_initialized or not self.chatbot:
                return {"success": False, "error": "Chatbot not initialized"}
            
            # Get cloud data and ask AI
            cloud_data = self.chatbot.get_cloud_data()
            response = self.chatbot.ask_ai(message, cloud_data)
            
            # Add to conversation history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user": message,
                "bot": response
            })
            
            return {"success": True, "response": response}
        except Exception as e:
            print(f"Error getting response: {e}")
            return {"success": False, "error": str(e)}

# Initialize chatbot manager
chatbot_manager = CloudWhisperManager()

@app.route('/')
def index():
    """Render the main page."""
    return render_template('chat.html')

@app.route('/api/status')
def get_status():
    """Get chatbot status."""
    return jsonify({
        "initialized": chatbot_manager.is_initialized,
        "provider": chatbot_manager.current_provider,
        "account": chatbot_manager.current_account
    })

@app.route('/api/initialize', methods=['POST'])
def initialize_chatbot():
    """Initialize the chatbot."""
    try:
        if chatbot_manager.initialize():
            return jsonify({"success": True, "message": "Chatbot initialized successfully"})
        else:
            return jsonify({"success": False, "message": "Failed to initialize chatbot"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({"success": False, "error": "No message provided"})
        
        response = chatbot_manager.get_response(message)
        return jsonify(response)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/history')
def get_history():
    """Get conversation history."""
    return jsonify({"history": chatbot_manager.conversation_history})

@app.route('/api/switch_provider', methods=['POST'])
def switch_provider():
    """Switch to a different cloud provider."""
    try:
        data = request.get_json()
        provider = data.get('provider', 'aws')
        
        if chatbot_manager.switch_provider(provider):
            return jsonify({"success": True, "provider": provider})
        else:
            return jsonify({"success": False, "error": "Failed to switch provider"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/switch_account', methods=['POST'])
def switch_account():
    """Switch to a different account in the current provider."""
    try:
        data = request.get_json()
        account_id = data.get('account_id', 'default')
        
        if chatbot_manager.switch_account(account_id):
            return jsonify({"success": True, "account": account_id})
        else:
            return jsonify({"success": False, "error": "Failed to switch account"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/accounts')
def list_accounts():
    """List available accounts for the current provider."""
    try:
        accounts = chatbot_manager.get_accounts()
        current_account_info = chatbot_manager.chatbot.get_account_info() if chatbot_manager.chatbot else {}
        
        return jsonify({
            "success": True,
            "accounts": accounts,
            "current_account": current_account_info
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/add_account', methods=['POST'])
def add_account():
    """Add a new cloud account."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'account_id', 'access_key', 'secret_key', 'region']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"success": False, "error": f"Missing required field: {field}"})
        
        # Add account
        success = chatbot_manager.add_account(
            account_id=data['account_id'],
            account_name=data['name'],
            access_key=data['access_key'],
            secret_key=data['secret_key'],
            region=data['region'],
            description=data.get('description', ''),
            provider=data.get('provider', 'aws')
        )
        
        if success:
            return jsonify({"success": True, "message": "Account added successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to add account"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/remove_account', methods=['POST'])
def remove_account():
    """Remove a cloud account."""
    try:
        data = request.get_json()
        account_id = data.get('account_id')
        provider = data.get('provider', 'aws')
        
        if not account_id:
            return jsonify({"success": False, "error": "Missing account_id"})
        
        # Don't allow removing the default account
        if account_id == 'default':
            return jsonify({"success": False, "error": "Cannot remove default account"})
        
        success = chatbot_manager.remove_account(account_id, provider)
        
        if success:
            return jsonify({"success": True, "message": "Account removed successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to remove account"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def create_html_template():
    """Create the HTML template file."""
    template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CloudWhisper - AI-Powered AWS Chatbot</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 100vh; }
        .container { max-width: 1400px; margin: 0 auto; height: 100vh; display: flex; background: white; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); overflow: hidden; }
        .sidebar { width: 350px; background: #2c3e50; color: white; padding: 20px; overflow-y: auto; }
        .main { flex: 1; display: flex; flex-direction: column; }
        .header { background: #f8f9fa; padding: 20px; border-bottom: 1px solid #dee2e6; }
        .messages { flex: 1; padding: 20px; overflow-y: auto; }
        .input-area { padding: 20px; border-top: 1px solid #dee2e6; }
        .message { margin-bottom: 15px; display: flex; gap: 10px; }
        .message.user { flex-direction: row-reverse; }
        .bubble { padding: 10px 15px; border-radius: 15px; max-width: 70%; white-space: pre-wrap; line-height: 1.6; }
        .user .bubble { background: #007bff; color: white; }
        .bot .bubble { background: #f8f9fa; color: #333; }
        .bot .bubble h3, .bot .bubble h4 { margin: 10px 0 5px 0; color: #2c3e50; }
        .bot .bubble ul, .bot .bubble ol { margin: 5px 0; padding-left: 20px; }
        .bot .bubble li { margin: 2px 0; }
        .bot .bubble strong { color: #2c3e50; font-weight: 600; }
        .input-group { display: flex; gap: 10px; }
        .chat-input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 20px; }
        .send-btn { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 20px; cursor: pointer; }
        .quick-btn { display: block; width: 100%; padding: 10px; margin: 5px 0; background: rgba(255,255,255,0.1); border: none; color: white; text-align: left; cursor: pointer; }
        .status { padding: 10px; background: rgba(255,255,255,0.1); border-radius: 5px; margin-bottom: 20px; }
        
        /* Cloud Provider Selector */
        .cloud-provider-selector { margin-bottom: 20px; }
        .cloud-provider-selector h3 { margin-bottom: 10px; color: #ecf0f1; }
        .provider-dropdown { width: 100%; padding: 8px; border-radius: 5px; border: none; background: rgba(255,255,255,0.9); color: #2c3e50; }
        .current-provider { margin-top: 5px; font-size: 12px; color: #bdc3c7; }
        
        /* Account Selector */
        .account-selector { margin-bottom: 20px; }
        .account-selector h3 { margin-bottom: 10px; color: #ecf0f1; }
        .account-dropdown { width: 100%; padding: 8px; border-radius: 5px; border: none; background: rgba(255,255,255,0.9); color: #2c3e50; }
        .current-account { margin-top: 5px; font-size: 12px; color: #bdc3c7; }
        .account-buttons { display: flex; gap: 5px; margin-top: 10px; }
        .add-account-btn, .delete-account-btn { flex: 1; padding: 5px 10px; border: none; border-radius: 5px; cursor: pointer; font-size: 12px; }
        .add-account-btn { background: #27ae60; color: white; }
        .delete-account-btn { background: #e74c3c; color: white; }
        
        /* Modal */
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); }
        .modal-content { background-color: white; margin: 15% auto; padding: 20px; border-radius: 10px; width: 80%; max-width: 500px; }
        .modal h2 { margin-bottom: 20px; color: #2c3e50; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; color: #2c3e50; font-weight: 600; }
        .form-group input, .form-group select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 5px; }
        .modal-buttons { display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px; }
        .modal-btn { padding: 8px 16px; border: none; border-radius: 5px; cursor: pointer; }
        .modal-btn.primary { background: #007bff; color: white; }
        .modal-btn.secondary { background: #6c757d; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h2><i class="fas fa-cloud"></i> CloudWhisper</h2>
            <div class="status" id="status">Status: Initializing...</div>
            
            <!-- Cloud Provider Selector -->
            <div class="cloud-provider-selector">
                <h3><i class="fas fa-cloud"></i> Cloud Provider</h3>
                <select class="provider-dropdown" id="providerDropdown" onchange="switchProvider()">
                    <option value="aws">AWS</option>
                    <option value="gcp">Google Cloud Platform</option>
                </select>
                <div class="current-provider" id="currentProvider">Current: AWS</div>
            </div>
            
            <!-- Account Selector -->
            <div class="account-selector">
                <h3><i class="fas fa-users"></i> Cloud Account</h3>
                <select class="account-dropdown" id="accountDropdown" onchange="switchAccount()">
                    <option value="default">Default Account</option>
                </select>
                <div class="current-account" id="currentAccount">Current: Default Account</div>
                <div class="account-buttons">
                    <button class="add-account-btn" onclick="openAddAccountModal()">
                        <i class="fas fa-plus"></i> Add
                    </button>
                    <button class="delete-account-btn" onclick="deleteCurrentAccount()">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
            
            <h3>Quick Actions</h3>
            <button class="quick-btn" onclick="sendQuick('How many instances do I have?')">Compute Instances</button>
            <button class="quick-btn" onclick="sendQuick('What storage buckets do I have?')">Storage Buckets</button>
            <button class="quick-btn" onclick="sendQuick('Show me my monitoring alerts')">Monitoring Alerts</button>
            <button class="quick-btn" onclick="sendQuick('How can I reduce costs?')">Cost Analysis</button>
            <button class="quick-btn" onclick="sendQuick('What security issues do I have?')">Security Analysis</button>
            <button class="quick-btn" onclick="initialize()">Initialize</button>
        </div>
        <div class="main">
            <div class="header">
                <h1>CloudWhisper - AI-Powered AWS Chatbot</h1>
                <p>Ask me anything about your AWS, GCP, or other cloud infrastructure</p>
            </div>
            <div class="messages" id="messages">
                <div class="message bot">
                    <div class="bubble">Welcome! Select your cloud provider and account, then click Initialize to start analyzing your cloud infrastructure.</div>
                </div>
            </div>
            <div class="input-area">
                <div class="input-group">
                    <input type="text" class="chat-input" id="input" placeholder="Ask me anything..." onkeypress="handleKey(event)">
                    <button class="send-btn" onclick="sendMessage()">Send</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Add Account Modal -->
    <div id="addAccountModal" class="modal">
        <div class="modal-content">
            <h2><i class="fas fa-plus"></i> Add Cloud Account</h2>
            <form id="addAccountForm">
                <div class="form-group">
                    <label for="accountName">Account Name:</label>
                    <input type="text" id="accountName" required>
                </div>
                <div class="form-group">
                    <label for="accountId">Account ID:</label>
                    <input type="text" id="accountId" required>
                </div>
                <div class="form-group">
                    <label for="accessKey">Access Key:</label>
                    <input type="text" id="accessKey" required>
                </div>
                <div class="form-group">
                    <label for="secretKey">Secret Key:</label>
                    <input type="password" id="secretKey" required>
                </div>
                <div class="form-group">
                    <label for="region">Region:</label>
                    <select id="region">
                        <option value="us-east-1">US East (N. Virginia)</option>
                        <option value="us-west-2">US West (Oregon)</option>
                        <option value="eu-west-1">Europe (Ireland)</option>
                        <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="description">Description:</label>
                    <input type="text" id="description">
                </div>
                <div class="modal-buttons">
                    <button type="button" class="modal-btn secondary" onclick="closeAddAccountModal()">Cancel</button>
                    <button type="submit" class="modal-btn primary">Add Account</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        let isInitialized = false;
        let currentProvider = 'aws';
        let currentAccount = 'default';

        async function initialize() {
            document.getElementById('status').textContent = 'Status: Initializing...';
            try {
                const response = await fetch('/api/initialize', { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                    isInitialized = true;
                    document.getElementById('status').textContent = 'Status: Connected';
                    addMessage('bot', '✅ CloudWhisper initialized! Ask me anything about your AWS infrastructure.');
                } else {
                    document.getElementById('status').textContent = 'Status: Failed';
                    addMessage('bot', '❌ Failed to initialize: ' + data.message);
                }
            } catch (error) {
                document.getElementById('status').textContent = 'Status: Error';
                addMessage('bot', '❌ Error: ' + error.message);
            }
        }

        async function switchProvider() {
            const provider = document.getElementById('providerDropdown').value;
            currentProvider = provider;
            document.getElementById('currentProvider').textContent = `Current: ${provider.toUpperCase()}`;
            
            try {
                const response = await fetch('/api/switch_provider', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ provider: provider })
                });
                const data = await response.json();
                if (data.success) {
                    addMessage('bot', `✅ Switched to ${provider.toUpperCase()} provider`);
                    loadAccounts();
                } else {
                    addMessage('bot', '❌ Failed to switch provider: ' + data.error);
                }
            } catch (error) {
                addMessage('bot', '❌ Error switching provider: ' + error.message);
            }
        }

        async function switchAccount() {
            const account = document.getElementById('accountDropdown').value;
            currentAccount = account;
            document.getElementById('currentAccount').textContent = `Current: ${account}`;
            
            try {
                const response = await fetch('/api/switch_account', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ account_id: account })
                });
                const data = await response.json();
                if (data.success) {
                    addMessage('bot', `✅ Switched to account: ${account}`);
                } else {
                    addMessage('bot', '❌ Failed to switch account: ' + data.error);
                }
            } catch (error) {
                addMessage('bot', '❌ Error switching account: ' + error.message);
            }
        }

        async function loadAccounts() {
            try {
                const response = await fetch('/api/accounts');
                const data = await response.json();
                if (data.success) {
                    const dropdown = document.getElementById('accountDropdown');
                    dropdown.innerHTML = '';
                    data.accounts.forEach(account => {
                        const option = document.createElement('option');
                        option.value = account.id;
                        option.textContent = account.name;
                        dropdown.appendChild(option);
                    });
                }
            } catch (error) {
                console.error('Error loading accounts:', error);
            }
        }

        function openAddAccountModal() {
            document.getElementById('addAccountModal').style.display = 'block';
        }

        function closeAddAccountModal() {
            document.getElementById('addAccountModal').style.display = 'none';
        }

        async function deleteCurrentAccount() {
            if (confirm('Are you sure you want to delete the current account?')) {
                try {
                    const response = await fetch('/api/remove_account', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ account_id: currentAccount })
                    });
                    const data = await response.json();
                    if (data.success) {
                        addMessage('bot', `✅ Account ${currentAccount} deleted`);
                        loadAccounts();
                    } else {
                        addMessage('bot', '❌ Failed to delete account: ' + data.error);
                    }
                } catch (error) {
                    addMessage('bot', '❌ Error deleting account: ' + error.message);
                }
            }
        }

        async function sendMessage() {
            const input = document.getElementById('input');
            const message = input.value.trim();
            if (!message) return;
            
            if (!isInitialized) {
                addMessage('bot', '⚠️ Please initialize the chatbot first.');
                return;
            }
            
            addMessage('user', message);
            input.value = '';
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                const data = await response.json();
                if (data.success) {
                    addMessage('bot', data.response);
                } else {
                    addMessage('bot', '❌ Error: ' + data.error);
                }
            } catch (error) {
                addMessage('bot', '❌ Error: ' + error.message);
            }
        }

        function sendQuick(message) {
            document.getElementById('input').value = message;
            sendMessage();
        }

        function addMessage(type, content) {
            const messages = document.getElementById('messages');
            const div = document.createElement('div');
            div.className = `message ${type}`;
            div.innerHTML = `<div class="bubble">${formatMessage(content)}</div>`;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }

        function formatMessage(content) {
            // Convert markdown-like formatting to HTML
            return content
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/^## (.*$)/gm, '<h3>$1</h3>')
                .replace(/^### (.*$)/gm, '<h4>$1</h4>')
                .replace(/^• (.*$)/gm, '<li>$1</li>')
                .replace(/^(\d+)\. (.*$)/gm, '<li>$2</li>')
                .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
                .replace(/\n/g, '<br>');
        }

        function handleKey(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        // Handle form submission for adding accounts
        document.getElementById('addAccountForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                name: document.getElementById('accountName').value,
                account_id: document.getElementById('accountId').value,
                access_key: document.getElementById('accessKey').value,
                secret_key: document.getElementById('secretKey').value,
                region: document.getElementById('region').value,
                description: document.getElementById('description').value,
                provider: currentProvider
            };
            
            try {
                const response = await fetch('/api/add_account', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                const data = await response.json();
                if (data.success) {
                    addMessage('bot', `✅ Account ${formData.name} added successfully`);
                    closeAddAccountModal();
                    loadAccounts();
                    // Clear form
                    document.getElementById('addAccountForm').reset();
                } else {
                    addMessage('bot', '❌ Failed to add account: ' + data.error);
                }
            } catch (error) {
                addMessage('bot', '❌ Error adding account: ' + error.message);
            }
        });

        // Load accounts on page load
        window.onload = function() {
            loadAccounts();
        };
    </script>
</body>
</html>'''
    
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Write the template file
    with open('templates/chat.html', 'w') as f:
        f.write(template_content)
    
    print("✅ HTML template created successfully!")

if __name__ == '__main__':
    # Create HTML template if it doesn't exist
    if not os.path.exists('templates/chat.html'):
        create_html_template()
    
    print("🚀 Starting CloudWhisper Web UI...")
    print("📱 Open your browser and go to: http://localhost:5001")
    print("🎯 Features:")
    print("   • Modern, responsive design")
    print("   • Real-time chat interface")
    print("   • Professional styling")
    print("   • Conversation history")
    print("   • AWS-focused with multi-account support")
    print("   • AI-powered cloud analysis")
    print("   • Account management")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5001, debug=True) 