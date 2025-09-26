# 🌟 CloudWhisper - AI-Powered AWS Infrastructure Chatbot

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![AWS](https://img.shields.io/badge/AWS-EC2%20%7C%20S3%20%7C%20CloudWatch-orange.svg)](https://aws.amazon.com)
[![AI](https://img.shields.io/badge/AI-ChatGPT%20%7C%20Claude-green.svg)](https://openai.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **CloudWhisper** is an intelligent AI-powered chatbot that whispers real-time insights and analysis of your AWS infrastructure. Ask questions about your EC2 instances, S3 buckets, CloudWatch alarms, and get AI-powered recommendations for optimization, security, and cost management.

## ✨ **Why CloudWhisper?**

- 🤖 **AI-Powered Analysis**: Get intelligent insights from ChatGPT or Claude
- 🌐 **Beautiful Web Interface**: Modern, responsive chat UI
- 🔄 **Multi-Account Support**: Manage multiple AWS accounts seamlessly
- 📊 **Real-Time Data**: Live AWS infrastructure monitoring
- 💬 **Natural Language**: Ask questions in plain English
- 🔒 **Secure**: Direct AWS credentials or profile support
- ⚡ **Fast**: Real-time responses with comprehensive data

## 🎯 **What Can CloudWhisper Do?**

### **Infrastructure Analysis**
- 📈 **Resource Overview**: Get instant overview of all your AWS resources
- 💰 **Cost Analysis**: Identify cost optimization opportunities
- 🔒 **Security Insights**: Security recommendations and vulnerability analysis
- 📊 **Performance Metrics**: Monitor and analyze performance data

### **Natural Language Queries**
```
"What are the IP addresses of my EC2 instances?"
"How much am I spending on AWS this month?"
"Show me all my S3 buckets and their sizes"
"What security issues do I have?"
"Which instances are running but not being used?"
```

### **Multi-Account Management**
- 🔄 Switch between AWS accounts instantly
- 📊 Compare resources across accounts
- 🎯 Account-specific analysis and recommendations

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8 or higher
- AWS Account with appropriate permissions
- OpenAI API key or Anthropic API key
- **Configuration setup** (see Configuration section below)

### **Installation**

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/cloudwhisper.git
cd cloudwhisper
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **⚠️ IMPORTANT: Configure credentials first**
**You MUST configure your credentials before running the application!**

**Option A: Environment Variables (Recommended - Most Secure)**
```bash
export OPENAI_API_KEY="sk-your-openai-key"
export ANTHROPIC_API_KEY="sk-ant-api03-your-anthropic-key"
export AWS_ACCESS_KEY_ID="your-aws-access-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

**Option B: Configuration Files (Alternative)**
```bash
./setup_config.sh
# Then edit the created files with your actual credentials
```

**💡 Note:** Environment variables take priority over configuration files. If you set environment variables, you can skip the configuration file setup!

4. **Configure AWS credentials**
**Option A: Use setup script (Recommended)**
```bash
./setup_config.sh
# Then edit the created files with your credentials
```

**Option B: Use environment variables (Most Secure)**
```bash
export AWS_ACCESS_KEY_ID="your-aws-access-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

**Option C: Manual configuration**
Copy template files and edit:
```bash
cp src/config/cloud_accounts.yaml.template src/config/cloud_accounts.yaml
# Edit with your AWS credentials
```

4. **Configure AI integration**
**Option A: Environment variables (Recommended)**
```bash
export OPENAI_API_KEY="sk-your-openai-key"
export ANTHROPIC_API_KEY="sk-ant-api03-your-anthropic-key"
```

**Option B: Configuration files**
```bash
cp src/config/ai_integration_config.yaml.template src/config/ai_integration_config.yaml
# Edit with your API keys
```

5. **Verify configuration**
```bash
# Run configuration validation
python3 validate_config.py

# Manual check (alternative)
ls -la src/config/
# Should show: ai_integration_config.yaml cloud_accounts.yaml

# Or check environment variables
echo $OPENAI_API_KEY
echo $AWS_ACCESS_KEY_ID
```

6. **Start the application**
```bash
# Web UI (Recommended)
python3 chat_ui.py

# Command Line Interface
python3 ai_chatbot.py
```

7. **Open your browser**
Navigate to `http://localhost:5001` and start chatting!

## 🎨 **Screenshots**

### **Web Interface**
- Modern, responsive design
- Real-time chat with AI
- Account switching
- Conversation history

### **Command Line Interface**
- Interactive terminal-based chat
- Quick responses
- Full AWS data access

## 📁 **Project Structure**

```
cloudwhisper/
├── src/
│   ├── config/
│   │   ├── ai_integration_config.yaml    # AI API configuration
│   │   └── cloud_accounts.yaml          # AWS account configuration
│   ├── mcp_server/
│   │   └── multi_cloud_mcp_server.py     # CloudWhisper MCP server
│   ├── aws_integration/
│   │   └── aws_client.py                 # AWS client implementation
│   ├── cloud_integration/
│   │   └── base_client.py                # Base cloud client
│   └── chatbot/
│       └── multi_cloud_chatbot.py       # CloudWhisper AI chatbot
├── templates/
│   └── chat.html                         # Web UI template
├── tests/                                # Comprehensive test suite
├── chat_ui.py                            # Flask web application
├── ai_chatbot.py                         # Command-line interface
├── requirements.txt                      # Python dependencies
└── README.md                             # This file
```

## 🔧 **Configuration**

**💡 Priority Order:** Environment Variables > Configuration Files

### **Option 1: Environment Variables (Recommended)**
Set these environment variables and skip configuration files:
```bash
export OPENAI_API_KEY="sk-your-openai-key"
export ANTHROPIC_API_KEY="sk-ant-api03-your-anthropic-key"
export AWS_ACCESS_KEY_ID="your-aws-access-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### **Option 2: Configuration Files (Alternative)**
CloudWhisper supports multiple AWS accounts. Configure them in `src/config/cloud_accounts.yaml`:

```yaml
aws_accounts:
  default:
    name: "Production Account"
    region: "us-east-1"
    access_key: "AKIA..."
    secret_key: "your-secret-key"
    description: "Main production environment"
    
  staging:
    name: "Staging Account"
    region: "us-west-2"
    access_key: "AKIA..."
    secret_key: "your-secret-key"
    description: "Staging environment"
    
  development:
    name: "Development Account"
    region: "eu-west-1"
    access_key: "AKIA..."
    secret_key: "your-secret-key"
    description: "Development environment"

default_account: "default"
```

### **AI Integration Setup**

Configure your AI provider in `src/config/ai_integration_config.yaml`:

```yaml
ai_integration:
  chatgpt:
    enabled: true
    api_key: "sk-your-openai-key"
    model: "gpt-4"
    
  claude:
    enabled: true
    api_key: "sk-ant-api03-YOUR-REAL-ANTHROPIC-KEY-HERE"
    model: "claude-3-sonnet-20240229"
```

## 🎯 **Usage Examples**

### **Web Interface**
1. Start the web server: `python3 chat_ui.py`
2. Open `http://localhost:5001`
3. Click "Initialize" to start
4. Ask questions about your AWS infrastructure

### **Command Line Interface**
1. Run: `python3 ai_chatbot.py`
2. Type your questions directly
3. Get instant AI-powered responses

### **Example Queries**
```
"What are the IP addresses of my EC2 instances?"
"How much storage am I using in S3?"
"Show me all my CloudWatch alarms"
"What's the cost breakdown of my infrastructure?"
"Which instances are running but not being used?"
"Are there any security issues with my setup?"
```

## 🧪 **Testing**

CloudWhisper includes a comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/test_aws_client.py
python -m pytest tests/test_mcp_server.py
python -m pytest tests/test_web_ui.py
```

## 🔒 **Security**

### **Configuration Protection**
- **Template Files**: Use `.template` files for safe sharing
- **Environment Variables**: Recommended for production
- **Git Protection**: Sensitive files are in `.gitignore`
- **Setup Scripts**: Automated secure configuration

### **Best Practices**
- **Never commit secrets**: Use environment variables
- **Rotate keys regularly**: Set up key rotation schedules
- **Use IAM roles**: For production deployments
- **Monitor access**: Track API key usage
- **Least privilege**: Only necessary AWS permissions

### **Security Features**
- **AWS Credentials**: Secure storage and validation
- **API Keys**: Environment variable support
- **Data Privacy**: All data stays within your infrastructure
- **No external calls**: Except to AWS and AI APIs

## 🚨 **Troubleshooting**

### **Common Issues**

1. **"Configuration not found" errors**
   - **First check:** Are environment variables set? Run `echo $OPENAI_API_KEY`
   - **If not:** Run `./setup_config.sh` to create configuration files
   - Check if `src/config/` directory exists
   - Verify configuration files are not empty

2. **"Access Denied" errors**
   - Check AWS credentials and permissions
   - Verify account configuration
   - Run `python3 validate_config.py` to check configuration

3. **"AI not responding"**
   - Check API keys in configuration
   - Verify internet connection
   - Ensure at least one AI provider is configured

4. **"Account not found"**
   - Verify AWS credentials are correct
   - Check `cloud_accounts.yaml` configuration
   - Run configuration validation

### **Debug Commands**
```bash
# Validate configuration (checks both env vars and config files)
python3 validate_config.py

# Check environment variables
echo "OpenAI: $OPENAI_API_KEY"
echo "AWS: $AWS_ACCESS_KEY_ID"

# Test AWS credentials
aws sts get-caller-identity

# Test AI APIs
curl -H "Authorization: Bearer YOUR_KEY" https://api.openai.com/v1/models

# Check configuration files (only if not using env vars)
ls -la src/config/
cat src/config/ai_integration_config.yaml
cat src/config/cloud_accounts.yaml
```

## 🤝 **Contributing**

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Add tests** for your changes
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### **Development Setup**
```bash
git clone https://github.com/yourusername/cloudwhisper.git
cd cloudwhisper
pip install -r requirements.txt
python -m pytest tests/
```

## 📈 **Roadmap**

- [ ] **Multi-Cloud Support**: GCP and Azure integration
- [ ] **Advanced Analytics**: Cost forecasting and optimization
- [ ] **Security Scanning**: Automated security assessments
- [ ] **API Integration**: REST API for programmatic access
- [ ] **Mobile App**: iOS and Android applications
- [ ] **Team Collaboration**: Multi-user support and sharing

## 🏆 **Features**

### **Current Features**
- ✅ AWS EC2, S3, CloudWatch integration
- ✅ Multi-account support
- ✅ AI-powered analysis (ChatGPT & Claude)
- ✅ Web and CLI interfaces
- ✅ Real-time data retrieval
- ✅ Comprehensive test suite

### **Planned Features**
- 🔄 Multi-cloud support (GCP, Azure)
- 📊 Advanced analytics and reporting
- 🔒 Security scanning and recommendations
- 📱 Mobile applications
- 🌐 REST API for integrations

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **OpenAI** for ChatGPT API
- **Anthropic** for Claude API
- **AWS** for comprehensive cloud services
- **Flask** for the web framework
- **Boto3** for AWS integration

## 📞 **Support**

- 📧 **Email**: support@cloudwhisper.ai
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/cloudwhisper/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/cloudwhisper/discussions)
- 📖 **Documentation**: [Wiki](https://github.com/yourusername/cloudwhisper/wiki)

## 🌟 **Star History**

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/cloudwhisper&type=Date)](https://star-history.com/#yourusername/cloudwhisper&Date)

---

<div align="center">

**Made with ❤️ for the AWS community**

[⭐ Star this repo](https://github.com/yourusername/cloudwhisper) | [🐛 Report Bug](https://github.com/yourusername/cloudwhisper/issues) | [💡 Request Feature](https://github.com/yourusername/cloudwhisper/issues)

</div>