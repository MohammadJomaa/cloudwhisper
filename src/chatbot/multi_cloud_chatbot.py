#!/usr/bin/env python3
"""
AWS AI Chatbot - Focused on AWS cloud services
"""

import json
import subprocess
import time
import yaml
import os
import sys
import openai
import anthropic
from typing import Dict, Any, Optional, List
from datetime import datetime

class AWSChatbot:
    """AWS-focused AI-powered chatbot for AWS environment queries."""
    
    def __init__(self, config_path: str = "src/config/ai_integration_config.yaml"):
        """Initialize the AWS AI chatbot."""
        self.config = self._load_config(config_path)
        self.server_process = None
        self.server_ready = False
        self.conversation_history = []
        self.ai_client = None
        self.ai_type = None
        self.current_account = "default"
        
        # Initialize AI client
        self._init_ai_client()
        
        # Start MCP server automatically
        self.start_mcp_server()
        
        print("🌟 CloudWhisper - AI-Powered AWS Chatbot")
        print("=" * 60)
        print("Ask me anything about your AWS infrastructure!")
        print("I'll whisper intelligent insights and recommendations.")
        print("Type 'help' for commands, 'quit' to exit")
        print("=" * 60)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"⚠️  Config file {config_path} not found, using defaults")
            return {}
        except yaml.YAMLError as e:
            print(f"❌ Error parsing config file: {e}")
            return {}
    
    def _init_ai_client(self):
        """Initialize AI client (Claude or ChatGPT)."""
        # Try ChatGPT first
        chatgpt_key = self._get_api_key('chatgpt')
        if chatgpt_key and chatgpt_key != "sk-your-openai-key":
            try:
                self.ai_client = openai.OpenAI(api_key=chatgpt_key)
                self.ai_type = "chatgpt"
                print("✅ Connected to ChatGPT")
                return
            except Exception as e:
                print(f"⚠️  ChatGPT connection failed: {e}")
        
        # Try Claude
        claude_key = self._get_api_key('claude')
        if claude_key and claude_key != "sk-ant-api03-YOUR-REAL-ANTHROPIC-KEY-HERE":
            try:
                self.ai_client = anthropic.Anthropic(api_key=claude_key)
                self.ai_type = "claude"
                print("✅ Connected to Claude")
                return
            except Exception as e:
                print(f"⚠️  Claude connection failed: {e}")
        
        print("⚠️  No AI API keys found. Using basic analysis mode.")
        self.ai_type = "basic"
    
    def _get_api_key(self, ai_type: str) -> str:
        """Get API key from config or environment variable."""
        # Try config file first
        if self.config and 'ai_integration' in self.config:
            config_key = self.config['ai_integration'].get(ai_type, {}).get('api_key', '')
            if config_key and config_key.strip():
                return config_key.strip()
        
        # Fall back to environment variable
        env_var_map = {
            'claude': 'ANTHROPIC_API_KEY',
            'chatgpt': 'OPENAI_API_KEY'
        }
        
        env_var = env_var_map.get(ai_type)
        if env_var:
            return os.getenv(env_var, '')
        
        return ''
    
    def start_mcp_server(self) -> bool:
        """Start the AWS MCP server."""
        try:
            print("🚀 Starting AWS MCP server...")
            
            # Start the MCP server process
            server_path = "src/mcp_server/multi_cloud_mcp_server.py"
            self.server_process = subprocess.Popen(
                [sys.executable, server_path, "--subprocess"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,  # Redirect stderr to avoid log interference
                text=True,
                bufsize=1
            )
            
            # Wait a moment for server to start
            time.sleep(2)
            
            # Test the server
            if self.server_process.poll() is None:
                self.server_ready = True
                print("✅ AWS MCP server started successfully")
                return True
            else:
                print("❌ Failed to start MCP server")
                return False
                
        except Exception as e:
            print(f"❌ Error starting MCP server: {e}")
            return False
    
    def stop_mcp_server(self):
        """Stop the MCP server process."""
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                print("🛑 MCP server stopped")
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                print("🛑 MCP server force killed")
            except Exception as e:
                print(f"⚠️  Error stopping MCP server: {e}")
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Optional[str]:
        """Call a tool on the MCP server."""
        if not self.server_ready or not self.server_process:
            return None
        
        try:
            # Create the tool call request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments or {}
                }
            }
            
            # Send request to server
            self.server_process.stdin.write(json.dumps(request) + "\n")
            self.server_process.stdin.flush()
            
            # Read response
            response_line = self.server_process.stdout.readline()
            if response_line:
                response = json.loads(response_line)
                if "result" in response and "content" in response["result"]:
                    return response["result"]["content"][0]["text"]
            
            return None
            
        except Exception as e:
            print(f"❌ Error calling tool {tool_name}: {e}")
            return None
    
    def get_cloud_data(self) -> Dict[str, Any]:
        """Get comprehensive cloud data from the MCP server."""
        try:
            # Check if server is ready, restart if needed
            if not self.server_ready:
                print("🔄 Restarting MCP server...")
                self.start_mcp_server()
                time.sleep(2)
            
            # Get instances
            instances_result = self.call_tool("list_instances")
            try:
                instances_data = json.loads(instances_result) if instances_result else {"success": False, "error": "Failed to get instances data"}
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing instances JSON: {e}")
                instances_data = {"success": False, "error": f"JSON parsing error: {e}"}
            
            # Get storage buckets
            storage_result = self.call_tool("list_storage_buckets")
            try:
                storage_data = json.loads(storage_result) if storage_result else {"success": False, "error": "Failed to get storage data"}
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing storage JSON: {e}")
                storage_data = {"success": False, "error": f"JSON parsing error: {e}"}
            
            # Get monitoring alerts
            alerts_result = self.call_tool("get_monitoring_alerts")
            try:
                alerts_data = json.loads(alerts_result) if alerts_result else {"success": False, "error": "Failed to get alerts data"}
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing alerts JSON: {e}")
                alerts_data = {"success": False, "error": f"JSON parsing error: {e}"}
            
            return {
                "instances": instances_data,
                "storage": storage_data,
                "alerts": alerts_data,
                "provider": "aws",
                "account": self.current_account,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error getting cloud data: {e}")
            return {"error": str(e)}
    
    def switch_provider(self, provider: str) -> bool:
        """Switch to a different cloud provider (AWS only)."""
        if provider.lower() == "aws":
            print("✅ Already using AWS provider")
            return True
        else:
            print(f"❌ Only AWS provider is supported, got: {provider}")
            return False
    
    def switch_account(self, account_id: str) -> bool:
        """Switch to a different account in the current provider."""
        try:
            result = self.call_tool("switch_account", {"account_id": account_id})
            if result:
                response = json.loads(result)
                if response.get("success"):
                    self.current_account = account_id
                    print(f"✅ Switched to account: {account_id}")
                    return True
                else:
                    print(f"❌ Failed to switch account: {response.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Failed to switch account: No response from server")
                return False
        except Exception as e:
            print(f"❌ Error switching account: {e}")
            return False
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get information about the current account."""
        try:
            result = self.call_tool("list_accounts")
            if result:
                response = json.loads(result)
                if response.get("success") and response.get("current_account"):
                    return response["current_account"]
            return {"error": "Failed to get account info"}
        except Exception as e:
            return {"error": str(e)}
    
    def list_available_accounts(self) -> List[Dict[str, Any]]:
        """List all available accounts for the current provider."""
        try:
            result = self.call_tool("list_accounts")
            if result:
                response = json.loads(result)
                if response.get("success"):
                    return response.get("accounts", [])
                else:
                    print(f"❌ Failed to list accounts: {response.get('error', 'Unknown error')}")
                    return []
            else:
                print("❌ Failed to list accounts: No response from server")
                return []
        except Exception as e:
            print(f"❌ Error listing accounts: {e}")
            return []
    
    def ask_ai(self, question: str, cloud_data: Dict[str, Any]) -> str:
        """Ask AI about the cloud data."""
        try:
            if self.ai_type == "basic":
                return self._basic_analysis(question, cloud_data)
            
            # Prepare context for AI
            context = self._prepare_ai_context(cloud_data)
            
            # Ask AI
            if self.ai_type == "chatgpt":
                return self._ask_chatgpt(question, context)
            elif self.ai_type == "claude":
                return self._ask_claude(question, context)
            else:
                return self._basic_analysis(question, cloud_data)
                
        except Exception as e:
            print(f"❌ Error asking AI: {e}")
            return f"❌ Error: {str(e)}"
    
    def _prepare_ai_context(self, cloud_data: Dict[str, Any]) -> str:
        """Prepare context for AI analysis."""
        try:
            context_parts = []
            
            # Add provider and account info
            context_parts.append(f"Cloud Provider: {cloud_data.get('provider', 'Unknown')}")
            context_parts.append(f"Account: {cloud_data.get('account', 'Unknown')}")
            context_parts.append(f"Timestamp: {cloud_data.get('timestamp', 'Unknown')}")
            context_parts.append("")
            
            # Add instances data
            instances_data = cloud_data.get("instances", {})
            if instances_data.get("success"):
                instances = instances_data.get("instances", [])
                context_parts.append(f"## Compute Instances ({len(instances)} total)")
                context_parts.append(f"- Running: {instances_data.get('running_count', 0)}")
                context_parts.append(f"- Stopped: {instances_data.get('stopped_count', 0)}")
                
                for i, instance in enumerate(instances[:5]):  # Limit to first 5 for context
                    context_parts.append(f"### Instance {i+1}")
                    context_parts.append(f"- ID: {instance.get('instance_id', 'N/A')}")
                    context_parts.append(f"- Name: {instance.get('name', 'N/A')}")
                    context_parts.append(f"- Type: {instance.get('instance_type', 'N/A')}")
                    context_parts.append(f"- Status: {instance.get('status', 'N/A')}")
                    context_parts.append(f"- Region: {instance.get('region', 'N/A')}")
                    
                    # Add network interface information (IP addresses)
                    network_interfaces = instance.get('network_interfaces', [])
                    if network_interfaces:
                        for j, ni in enumerate(network_interfaces):
                            context_parts.append(f"- Network Interface {j+1}:")
                            context_parts.append(f"  - Private IP: {ni.get('private_ip', 'N/A')}")
                            context_parts.append(f"  - Public IP: {ni.get('public_ip', 'N/A')}")
                            context_parts.append(f"  - VPC ID: {ni.get('vpc_id', 'N/A')}")
                            context_parts.append(f"  - Subnet ID: {ni.get('subnet_id', 'N/A')}")
                            context_parts.append(f"  - Security Groups: {', '.join(ni.get('security_groups', []))}")
            else:
                context_parts.append("## Compute Instances: Error retrieving data")
                context_parts.append(f"Error: {instances_data.get('error', 'Unknown error')}")
            
            context_parts.append("")
            
            # Add storage data
            storage_data = cloud_data.get("storage", {})
            if storage_data.get("success"):
                buckets = storage_data.get("buckets", [])
                context_parts.append(f"## Storage Buckets ({len(buckets)} total)")
                context_parts.append(f"- Total Size: {storage_data.get('total_size_gb', 0)} GB")
                context_parts.append(f"- Total Objects: {storage_data.get('total_objects', 0)}")
                context_parts.append(f"- Encrypted: {storage_data.get('encrypted_buckets', 0)}")
                context_parts.append(f"- Versioned: {storage_data.get('versioned_buckets', 0)}")
                
                for i, bucket in enumerate(buckets[:5]):  # Limit to first 5 for context
                    context_parts.append(f"### Bucket {i+1}")
                    context_parts.append(f"- Name: {bucket.get('name', 'N/A')}")
                    context_parts.append(f"- Size: {bucket.get('size_gb', 0)} GB")
                    context_parts.append(f"- Objects: {bucket.get('object_count', 0)}")
                    context_parts.append(f"- Encryption: {bucket.get('encryption', 'N/A')}")
            else:
                context_parts.append("## Storage Buckets: Error retrieving data")
                context_parts.append(f"Error: {storage_data.get('error', 'Unknown error')}")
            
            context_parts.append("")
            
            # Add alerts data
            alerts_data = cloud_data.get("alerts", {})
            if alerts_data.get("success"):
                alerts = alerts_data.get("alerts", [])
                context_parts.append(f"## Monitoring Alerts ({len(alerts)} total)")
                context_parts.append(f"- Enabled: {alerts_data.get('enabled_alerts', 0)}")
                context_parts.append(f"- Disabled: {alerts_data.get('disabled_alerts', 0)}")
                
                for i, alert in enumerate(alerts[:5]):  # Limit to first 5 for context
                    context_parts.append(f"### Alert {i+1}")
                    context_parts.append(f"- Name: {alert.get('name', 'N/A')}")
                    context_parts.append(f"- Display Name: {alert.get('display_name', 'N/A')}")
                    context_parts.append(f"- Enabled: {alert.get('enabled', 'N/A')}")
                    context_parts.append(f"- Severity: {alert.get('severity', 'N/A')}")
            else:
                context_parts.append("## Monitoring Alerts: Error retrieving data")
                context_parts.append(f"Error: {alerts_data.get('error', 'Unknown error')}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            return f"Error preparing context: {str(e)}"
    
    def _ask_chatgpt(self, question: str, context: str) -> str:
        """Ask ChatGPT about the cloud data."""
        try:
            system_prompt = f"""You are an expert cloud infrastructure analyst. You have access to detailed information about a cloud environment.

CRITICAL FORMATTING REQUIREMENTS:
• ALWAYS use bullet points (•) for lists
• ALWAYS use numbered lists (1., 2., 3.) for steps
• ALWAYS use **bold** for important terms and metrics
• ALWAYS use ## for main headings and ### for subheadings
• ALWAYS add line breaks between sections (use \n\n)
• NEVER put all information in one long paragraph
• ALWAYS break information into logical sections
• ALWAYS use emojis for visual appeal (🖥️, 📊, 💰, 🔒, 🚀, etc.)
• ALWAYS use proper spacing and indentation
• ALWAYS use horizontal rules (---) to separate major sections
• ALWAYS use code formatting (`code`) for technical terms

EXAMPLE OF GOOD FORMATTING:
🖥️ **Cloud Infrastructure Analysis**

## 📊 Summary
• **Total Instances:** 5
• **Running:** 3
• **Stopped:** 2
• **Provider:** AWS
• **Region:** us-east-1

---

## 🖥️ Instance Details
### Instance #1
• **ID:** `i-1234567890`
• **Type:** `t3.micro`
• **Status:** running
• **Region:** us-east-1a

### Instance #2
• **ID:** `i-0987654321`
• **Type:** `t3.small`
• **Status:** stopped
• **Region:** us-east-1b

---

## 💰 Cost Analysis
• **Estimated Monthly Cost:** $45.67
• **Recommendations:** Consider reserved instances
• **Potential Savings:** $12.34/month

---

## 🔒 Security Recommendations
1. **Enable CloudTrail** for audit logging
2. **Review IAM policies** for least privilege
3. **Enable encryption** for all storage buckets

Cloud Environment Context:
{context}

User Question: {question}

Please provide a comprehensive, well-formatted analysis based on the cloud data provided. Use proper formatting with headings, bullet points, numbered lists, and emojis for better readability."""
            
            response = self.ai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"❌ Error asking ChatGPT: {str(e)}"
    
    def _ask_claude(self, question: str, context: str) -> str:
        """Ask Claude about the cloud data."""
        try:
            system_prompt = f"""You are an expert cloud infrastructure analyst. You have access to detailed information about a cloud environment.

CRITICAL FORMATTING REQUIREMENTS:
• ALWAYS use bullet points (•) for lists
• ALWAYS use numbered lists (1., 2., 3.) for steps
• ALWAYS use **bold** for important terms and metrics
• ALWAYS use ## for main headings and ### for subheadings
• ALWAYS add line breaks between sections (use \n\n)
• NEVER put all information in one long paragraph
• ALWAYS break information into logical sections
• ALWAYS use emojis for visual appeal (🖥️, 📊, 💰, 🔒, 🚀, etc.)
• ALWAYS use proper spacing and indentation
• ALWAYS use horizontal rules (---) to separate major sections
• ALWAYS use code formatting (`code`) for technical terms

EXAMPLE OF GOOD FORMATTING:
🖥️ **Cloud Infrastructure Analysis**

## 📊 Summary
• **Total Instances:** 5
• **Running:** 3
• **Stopped:** 2
• **Provider:** AWS
• **Region:** us-east-1

---

## 🖥️ Instance Details
### Instance #1
• **ID:** `i-1234567890`
• **Type:** `t3.micro`
• **Status:** running
• **Region:** us-east-1a

### Instance #2
• **ID:** `i-0987654321`
• **Type:** `t3.small`
• **Status:** stopped
• **Region:** us-east-1b

---

## 💰 Cost Analysis
• **Estimated Monthly Cost:** $45.67
• **Recommendations:** Consider reserved instances
• **Potential Savings:** $12.34/month

---

## 🔒 Security Recommendations
1. **Enable CloudTrail** for audit logging
2. **Review IAM policies** for least privilege
3. **Enable encryption** for all storage buckets

Cloud Environment Context:
{context}

User Question: {question}

Please provide a comprehensive, well-formatted analysis based on the cloud data provided. Use proper formatting with headings, bullet points, numbered lists, and emojis for better readability."""
            
            response = self.ai_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": question}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"❌ Error asking Claude: {str(e)}"
    
    def _basic_analysis(self, question: str, cloud_data: Dict[str, Any]) -> str:
        """Basic analysis without AI."""
        try:
            provider = cloud_data.get("provider", "Unknown")
            account = cloud_data.get("account", "Unknown")
            
            instances_data = cloud_data.get("instances", {})
            storage_data = cloud_data.get("storage", {})
            alerts_data = cloud_data.get("alerts", {})
            
            analysis = f"🖥️ **{provider.upper()} Infrastructure Analysis**\n\n"
            analysis += f"## 📊 Summary\n"
            analysis += f"• **Provider:** {provider.upper()}\n"
            analysis += f"• **Account:** {account}\n"
            
            if instances_data.get("success"):
                instances = instances_data.get("instances", [])
                analysis += f"• **Total Instances:** {len(instances)}\n"
                analysis += f"• **Running:** {instances_data.get('running_count', 0)}\n"
                analysis += f"• **Stopped:** {instances_data.get('stopped_count', 0)}\n"
            else:
                analysis += f"• **Instances:** Error retrieving data\n"
            
            if storage_data.get("success"):
                buckets = storage_data.get("buckets", [])
                analysis += f"• **Storage Buckets:** {len(buckets)}\n"
                analysis += f"• **Total Size:** {storage_data.get('total_size_gb', 0)} GB\n"
            else:
                analysis += f"• **Storage:** Error retrieving data\n"
            
            if alerts_data.get("success"):
                alerts = alerts_data.get("alerts", [])
                analysis += f"• **Monitoring Alerts:** {len(alerts)}\n"
                analysis += f"• **Enabled:** {alerts_data.get('enabled_alerts', 0)}\n"
            else:
                analysis += f"• **Alerts:** Error retrieving data\n"
            
            analysis += f"\n---\n\n"
            analysis += f"## 💡 Recommendations\n"
            analysis += f"• Review instance usage and consider stopping unused instances\n"
            analysis += f"• Check storage bucket permissions and encryption\n"
            analysis += f"• Monitor alert policies and ensure critical alerts are enabled\n"
            analysis += f"• Consider cost optimization strategies\n"
            analysis += f"• Implement proper tagging for better resource management\n"
            
            analysis += f"\n---\n\n"
            analysis += f"## 🔒 Security Checklist\n"
            analysis += f"1. **Enable CloudTrail** for audit logging\n"
            analysis += f"2. **Review IAM policies** for least privilege access\n"
            analysis += f"3. **Enable encryption** for all storage buckets\n"
            analysis += f"4. **Set up monitoring** for critical resources\n"
            analysis += f"5. **Regular security audits** of your infrastructure\n"
            
            return analysis
            
        except Exception as e:
            return f"❌ Error in basic analysis: {str(e)}"
    
    def run(self):
        """Run the CloudWhisper chatbot."""
        try:
            while True:
                try:
                    # Get user input
                    user_input = input("\n🤖 You: ").strip()
                    
                    if user_input.lower() in ['quit', 'exit', 'bye']:
                        print("👋 Goodbye!")
                        break
                    elif user_input.lower() == 'help':
                        self.show_help()
                        continue
                    elif user_input.lower() == 'data':
                        self.show_data()
                        continue
                    elif user_input.lower() == 'history':
                        self.show_history()
                        continue
                    elif user_input.lower().startswith('switch provider'):
                        print("❌ Only AWS provider is supported")
                        continue
                    elif user_input.lower().startswith('switch account'):
                        parts = user_input.split()
                        if len(parts) >= 3:
                            account = parts[2]
                            self.switch_account(account)
                        continue
                    
                    # Add to conversation history
                    self.conversation_history.append({"role": "user", "content": user_input})
                    
                    # Get cloud data
                    print("🔄 Getting cloud data and analyzing with AI...")
                    cloud_data = self.get_cloud_data()
                    
                    # Ask AI
                    ai_response = self.ask_ai(user_input, cloud_data)
                    
                    # Add AI response to history
                    self.conversation_history.append({"role": "assistant", "content": ai_response})
                    
                    # Display response
                    print(f"\n🤖 AI Bot: {ai_response}")
                    
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
                    continue
                    
        finally:
            self.stop_mcp_server()
    
    def show_help(self):
        """Show help information."""
        help_text = """
🌟 **CloudWhisper Help**

**Commands:**
• help - Show this help message
• data - Show current cloud data
• history - Show conversation history
• quit/exit/bye - Exit the chatbot

**AWS Management:**
• switch account <account_id> - Switch AWS account

**Example Questions:**
• "How many EC2 instances do I have?"
• "What's the cost of my AWS infrastructure?"
• "Show me my S3 buckets"
• "What security issues do I have?"
• "How can I optimize AWS costs?"

**Supported AWS Services:**
• EC2 (Compute instances)
• S3 (Storage buckets)
• CloudWatch (Monitoring and alerts)
        """
        print(help_text)
    
    def show_data(self):
        """Show current cloud data."""
        try:
            cloud_data = self.get_cloud_data()
            print(f"\n📊 **Current Cloud Data**")
            print(f"Provider: {cloud_data.get('provider', 'Unknown')}")
            print(f"Account: {cloud_data.get('account', 'Unknown')}")
            print(f"Timestamp: {cloud_data.get('timestamp', 'Unknown')}")
            
            instances_data = cloud_data.get("instances", {})
            if instances_data.get("success"):
                print(f"\n🖥️ **Instances:** {len(instances_data.get('instances', []))}")
            else:
                print(f"\n🖥️ **Instances:** Error")
            
            storage_data = cloud_data.get("storage", {})
            if storage_data.get("success"):
                print(f"📦 **Storage Buckets:** {len(storage_data.get('buckets', []))}")
            else:
                print(f"📦 **Storage Buckets:** Error")
            
            alerts_data = cloud_data.get("alerts", {})
            if alerts_data.get("success"):
                print(f"🔔 **Alerts:** {len(alerts_data.get('alerts', []))}")
            else:
                print(f"🔔 **Alerts:** Error")
                
        except Exception as e:
            print(f"❌ Error showing data: {e}")
    
    def show_history(self):
        """Show conversation history."""
        if not self.conversation_history:
            print("📝 No conversation history yet.")
            return
        
        print("\n📝 **Conversation History:**")
        for i, message in enumerate(self.conversation_history[-10:], 1):  # Show last 10 messages
            role = "You" if message["role"] == "user" else "AI"
            content = message["content"][:100] + "..." if len(message["content"]) > 100 else message["content"]
            print(f"{i}. {role}: {content}")

def main():
    """Main function to run the AWS chatbot."""
    try:
        chatbot = AWSChatbot()
        chatbot.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 