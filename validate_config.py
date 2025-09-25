#!/usr/bin/env python3
"""
CloudWhisper Configuration Validation Script
Validates that all required configuration is present before starting the application.
"""

import os
import sys
import yaml
from pathlib import Path

def check_environment_variables():
    """Check if required environment variables are set."""
    required_vars = {
        'OPENAI_API_KEY': 'OpenAI API key for ChatGPT integration',
        'ANTHROPIC_API_KEY': 'Anthropic API key for Claude integration',
        'AWS_ACCESS_KEY_ID': 'AWS Access Key ID',
        'AWS_SECRET_ACCESS_KEY': 'AWS Secret Access Key',
        'AWS_DEFAULT_REGION': 'AWS Default Region'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"  - {var}: {description}")
    
    return missing_vars

def check_config_files():
    """Check if configuration files exist and are properly configured."""
    config_files = {
        'src/config/ai_integration_config.yaml': 'AI integration configuration',
        'src/config/cloud_accounts.yaml': 'AWS accounts configuration'
    }
    
    missing_files = []
    for file_path, description in config_files.items():
        if not Path(file_path).exists():
            missing_files.append(f"  - {file_path}: {description}")
        else:
            # Check if file contains placeholder values
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    if 'YOUR_' in content or 'your-' in content:
                        print(f"⚠️  {file_path} contains placeholder values - please update with real credentials")
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
    
    return missing_files

def validate_ai_config():
    """Validate AI integration configuration."""
    config_path = 'src/config/ai_integration_config.yaml'
    if not Path(config_path).exists():
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        ai_config = config.get('ai_integration', {})
        
        # Check if at least one AI provider is configured
        chatgpt_configured = ai_config.get('chatgpt', {}).get('api_key', '').strip()
        claude_configured = ai_config.get('claude', {}).get('api_key', '').strip()
        
        if not chatgpt_configured and not claude_configured:
            print("❌ No AI providers configured in ai_integration_config.yaml")
            return False
        
        if chatgpt_configured and 'YOUR_' in chatgpt_configured:
            print("⚠️  ChatGPT API key appears to be a placeholder")
            return False
            
        if claude_configured and 'YOUR_' in claude_configured:
            print("⚠️  Claude API key appears to be a placeholder")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating AI config: {e}")
        return False

def validate_aws_config():
    """Validate AWS accounts configuration."""
    config_path = 'src/config/cloud_accounts.yaml'
    if not Path(config_path).exists():
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        aws_accounts = config.get('aws_accounts', {})
        if not aws_accounts:
            print("❌ No AWS accounts configured")
            return False
        
        for account_id, account_config in aws_accounts.items():
            access_key = account_config.get('access_key', '')
            secret_key = account_config.get('secret_key', '')
            
            if 'YOUR_' in access_key or 'YOUR_' in secret_key:
                print(f"⚠️  AWS account '{account_id}' contains placeholder credentials")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating AWS config: {e}")
        return False

def main():
    """Main validation function."""
    print("🔍 CloudWhisper Configuration Validation")
    print("=" * 50)
    
    # Check environment variables first
    print("\n📋 Checking environment variables...")
    missing_env_vars = check_environment_variables()
    env_vars_complete = len(missing_env_vars) == 0
    
    if env_vars_complete:
        print("✅ All required environment variables are set")
        print("🎉 Configuration validation passed!")
        print("✅ You can now start CloudWhisper (using environment variables)")
        return 0
    else:
        print("⚠️  Missing environment variables:")
        for var in missing_env_vars:
            print(var)
        print("\n💡 You can either:")
        print("   1. Set the missing environment variables, OR")
        print("   2. Use configuration files (see below)")
    
    # Check configuration files (only if env vars are not complete)
    print("\n📁 Checking configuration files...")
    missing_files = check_config_files()
    if missing_files:
        print("❌ Missing configuration files:")
        for file in missing_files:
            print(file)
        print("\n💡 Run './setup_config.sh' to create configuration files")
    else:
        print("✅ All configuration files exist")
    
    # Validate AI configuration (only if env vars are not complete)
    if not env_vars_complete:
        print("\n🤖 Validating AI configuration...")
        if validate_ai_config():
            print("✅ AI configuration is valid")
        else:
            print("❌ AI configuration needs attention")
    
    # Validate AWS configuration (only if env vars are not complete)
    if not env_vars_complete:
        print("\n☁️  Validating AWS configuration...")
        if validate_aws_config():
            print("✅ AWS configuration is valid")
        else:
            print("❌ AWS configuration needs attention")
    
    # Summary
    print("\n" + "=" * 50)
    if env_vars_complete:
        print("🎉 Configuration validation passed!")
        print("✅ You can now start CloudWhisper")
        return 0
    elif not missing_files:
        print("🎉 Configuration validation passed!")
        print("✅ You can now start CloudWhisper (using configuration files)")
        return 0
    else:
        print("❌ Configuration validation failed!")
        print("💡 Please fix the issues above before starting CloudWhisper")
        return 1

if __name__ == "__main__":
    sys.exit(main())
