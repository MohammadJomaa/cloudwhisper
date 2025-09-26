#!/usr/bin/env python3
"""
CloudWhisper MCP Server - AWS cloud services integration
"""

import json
import sys
import structlog
from typing import Dict, Any, Optional

# Handle imports for both module and standalone execution
try:
    from ..aws_integration.aws_client import AWSClient
except ImportError:
    # When running as standalone script
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    try:
        from src.aws_integration.aws_client import AWSClient
    except ImportError:
        from aws_integration.aws_client import AWSClient

# Configure logger to not output to stdout when running as subprocess
if len(sys.argv) > 1 and sys.argv[1] == "--subprocess":
    # When running as subprocess, disable all logging
    import logging
    logging.getLogger().setLevel(logging.CRITICAL)
    # Create a dummy logger that does nothing
    logger = type('DummyLogger', (), {'info': lambda self, x: None, 'error': lambda self, x: None, 'dummy': True})()
else:
    logger = structlog.get_logger(__name__)

class CloudWhisperMCPServer:
    """CloudWhisper MCP server for AWS cloud services."""
    
    def __init__(self):
        """Initialize the CloudWhisper MCP server."""
        self.current_account = "default"
        self.aws_client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize AWS client."""
        try:
            # Initialize AWS client
            self.aws_client = AWSClient(account_id=self.current_account)
            
            if not hasattr(logger, 'info'):  # Only log if not in subprocess mode
                pass  # Skip logging in subprocess mode
            else:
                logger.info("AWS MCP server initialized")
            
        except Exception as e:
            if not hasattr(logger, 'error'):  # Only log if not in subprocess mode
                pass  # Skip logging in subprocess mode
            else:
                logger.error(f"Error initializing AWS client: {e}")
    
    def get_current_client(self):
        """Get the current AWS client."""
        return self.aws_client
    
    def switch_provider(self, provider: str) -> Dict[str, Any]:
        """Switch to a different cloud provider (AWS only)."""
        try:
            if provider.lower() == "aws":
                logger.info(f"Switched to AWS provider")
                return {"success": True, "provider": "aws"}
            else:
                return {"success": False, "error": f"Only AWS provider is supported, got: {provider}"}
        except Exception as e:
            logger.error(f"Error switching provider: {e}")
            return {"success": False, "error": str(e)}
    
    def switch_account(self, account_id: str) -> Dict[str, Any]:
        """Switch to a different AWS account."""
        try:
            client = self.get_current_client()
            if client and client.switch_account(account_id):
                self.current_account = account_id
                return {"success": True, "account": account_id}
            else:
                return {"success": False, "error": f"Failed to switch to AWS account {account_id}"}
        except Exception as e:
            logger.error(f"Error switching account: {e}")
            return {"success": False, "error": str(e)}
    
    def list_providers(self) -> Dict[str, Any]:
        """List available cloud providers (AWS only)."""
        try:
            providers = [
                {"id": "aws", "name": "Amazon Web Services", "description": "AWS cloud services"}
            ]
            return {"success": True, "providers": providers, "current": "aws"}
        except Exception as e:
            logger.error(f"Error listing providers: {e}")
            return {"success": False, "error": str(e)}
    
    def list_accounts(self) -> Dict[str, Any]:
        """List all available AWS accounts."""
        try:
            client = self.get_current_client()
            if client:
                accounts = client.list_available_accounts()
                current_account_info = client.get_account_info()
                return {
                    "success": True,
                    "accounts": accounts,
                    "current_account": current_account_info
                }
            else:
                return {"success": False, "error": "No AWS client available"}
        except Exception as e:
            logger.error(f"Error listing accounts: {e}")
            return {"success": False, "error": str(e)}
    
    def list_instances(self) -> str:
        """List EC2 instances."""
        try:
            client = self.get_current_client()
            if client:
                result = client.list_instances()
                return json.dumps(result)
            else:
                return json.dumps({"success": False, "error": "No AWS client available"})
        except Exception as e:
            logger.error(f"Error listing instances: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    def list_storage_buckets(self) -> str:
        """List S3 buckets."""
        try:
            client = self.get_current_client()
            if client:
                result = client.list_storage_buckets()
                return json.dumps(result)
            else:
                return json.dumps({"success": False, "error": "No AWS client available"})
        except Exception as e:
            logger.error(f"Error listing storage buckets: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    def get_monitoring_alerts(self) -> str:
        """Get CloudWatch alarms."""
        try:
            client = self.get_current_client()
            if client:
                result = client.get_monitoring_alerts()
                return json.dumps(result)
            else:
                return json.dumps({"success": False, "error": "No AWS client available"})
        except Exception as e:
            logger.error(f"Error getting monitoring alerts: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    def get_current_provider(self) -> Dict[str, Any]:
        """Get current AWS provider information."""
        try:
            client = self.get_current_client()
            if client:
                account_info = client.get_account_info()
                return {
                    "success": True,
                    "provider": "aws",
                    "account": self.current_account,
                    "account_info": account_info
                }
            else:
                return {"success": False, "error": "No AWS client available"}
        except Exception as e:
            logger.error(f"Error getting current provider: {e}")
            return {"success": False, "error": str(e)}
    
    def run(self):
        """Run the MCP server."""
        try:
            while True:
                try:
                    # Read request from stdin
                    request_line = input()
                    if not request_line:
                        continue
                    
                    request = json.loads(request_line)
                    
                    # Handle the request
                    response = self._handle_request(request)
                    
                    # Send response to stdout
                    print(json.dumps(response))
                    sys.stdout.flush()
                    
                except EOFError:
                    break
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(f"Error processing request: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id", 1),
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        }
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()
                    
        except Exception as e:
            logger.error(f"Server error: {e}")
    
    def _handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request."""
        try:
            method = request.get("method", "")
            params = request.get("params", {})
            request_id = request.get("id", 1)
            
            if method == "initialize":
                return self._handle_initialize(request_id)
            elif method == "tools/list":
                return self._handle_tools_list(request_id)
            elif method == "tools/call":
                return self._handle_tools_call(request_id, params)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id", 1),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    def _handle_initialize(self, request_id: int) -> Dict[str, Any]:
        """Handle initialization request."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "CloudWhisper MCP Server",
                    "version": "1.0.0"
                }
            }
        }
    
    def _handle_tools_list(self, request_id: int) -> Dict[str, Any]:
        """Handle tools list request."""
        tools = [
            {
                "name": "switch_provider",
                "description": "Switch to a different cloud provider (aws only)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "provider": {
                            "type": "string",
                            "description": "Cloud provider to switch to (aws only)"
                        }
                    },
                    "required": ["provider"]
                }
            },
            {
                "name": "switch_account",
                "description": "Switch to a different AWS account",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "account_id": {
                            "type": "string",
                            "description": "AWS Account ID to switch to"
                        }
                    },
                    "required": ["account_id"]
                }
            },
            {
                "name": "list_providers",
                "description": "List available cloud providers (AWS only)",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "list_accounts",
                "description": "List all available AWS accounts",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_current_provider",
                "description": "Get current AWS provider and account information",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "list_instances",
                "description": "List EC2 instances",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "list_storage_buckets",
                "description": "List S3 buckets",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_monitoring_alerts",
                "description": "Get CloudWatch alarms",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools
            }
        }
    
    def _handle_tools_call(self, request_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool call request."""
        try:
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            
            if tool_name == "switch_provider":
                provider = arguments.get("provider", "")
                result = self.switch_provider(provider)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result)
                            }
                        ]
                    }
                }
            
            elif tool_name == "switch_account":
                account_id = arguments.get("account_id", "")
                result = self.switch_account(account_id)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result)
                            }
                        ]
                    }
                }
            
            elif tool_name == "list_providers":
                result = self.list_providers()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result)
                            }
                        ]
                    }
                }
            
            elif tool_name == "list_accounts":
                result = self.list_accounts()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result)
                            }
                        ]
                    }
                }
            
            elif tool_name == "get_current_provider":
                result = self.get_current_provider()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result)
                            }
                        ]
                    }
                }
            
            elif tool_name == "list_instances":
                result_text = self.list_instances()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result_text
                            }
                        ]
                    }
                }
            
            elif tool_name == "list_storage_buckets":
                result_text = self.list_storage_buckets()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result_text
                            }
                        ]
                    }
                }
            
            elif tool_name == "get_monitoring_alerts":
                result_text = self.get_monitoring_alerts()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result_text
                            }
                        ]
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Tool not found: {tool_name}"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error handling tool call: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }

def main():
    """Main function to run the CloudWhisper MCP server."""
    try:
        server = CloudWhisperMCPServer()
        server.run()
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == "__main__":
    main() 