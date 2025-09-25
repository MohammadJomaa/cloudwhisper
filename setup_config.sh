#!/bin/bash

# CloudWhisper Configuration Setup Script
# This script helps you set up configuration files securely

echo "🔒 Setting up CloudWhisper Configuration Files..."

# Check if config files already exist
if [ -f "src/config/ai_integration_config.yaml" ]; then
    echo "⚠️  ai_integration_config.yaml already exists. Backing up to ai_integration_config.yaml.backup"
    cp src/config/ai_integration_config.yaml src/config/ai_integration_config.yaml.backup
fi

if [ -f "src/config/cloud_accounts.yaml" ]; then
    echo "⚠️  cloud_accounts.yaml already exists. Backing up to cloud_accounts.yaml.backup"
    cp src/config/cloud_accounts.yaml src/config/cloud_accounts.yaml.backup
fi

# Copy template files
echo "📋 Creating configuration files from templates..."
cp src/config/ai_integration_config.yaml.template src/config/ai_integration_config.yaml
cp src/config/cloud_accounts.yaml.template src/config/cloud_accounts.yaml

echo ""
echo "✅ Configuration files created!"
echo ""
echo "🔧 Next steps:"
echo "1. Edit src/config/ai_integration_config.yaml with your AI API keys"
echo "2. Edit src/config/cloud_accounts.yaml with your AWS credentials"
echo "3. Never commit these files to Git (they're in .gitignore)"
echo ""
echo "🔒 Security reminders:"
echo "- Use environment variables when possible"
echo "- Never share your API keys"
echo "- Use AWS IAM roles for production"
echo "- Rotate your keys regularly"
echo ""
echo "📖 For more security tips, see CONTRIBUTING.md"
