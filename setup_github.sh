#!/bin/bash

# CloudWhisper GitHub Repository Setup Script
# This script helps you set up the GitHub repository for CloudWhisper

echo "🌟 Setting up CloudWhisper GitHub Repository..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
fi

# Add all files
echo "📦 Adding files to Git..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "feat: initial CloudWhisper release

- AI-powered AWS infrastructure chatbot
- Multi-account AWS support
- Web UI and CLI interfaces
- Real-time AWS data analysis
- ChatGPT and Claude integration
- Comprehensive test suite
- Professional documentation"

# Set up remote (replace with your GitHub username)
echo "🔗 Setting up GitHub remote..."
echo "Please replace 'yourusername' with your actual GitHub username:"
echo "git remote add origin https://github.com/yourusername/cloudwhisper.git"
echo "git branch -M main"
echo "git push -u origin main"

echo ""
echo "✅ CloudWhisper is ready for GitHub!"
echo ""
echo "Next steps:"
echo "1. Create a new repository on GitHub named 'cloudwhisper'"
echo "2. Copy the repository URL"
echo "3. Run the git commands above with your actual repository URL"
echo "4. Enable GitHub Actions in your repository settings"
echo "5. Add repository topics: aws, chatbot, ai, python, infrastructure"
echo "6. Set up branch protection rules for main branch"
echo ""
echo "🎉 Your CloudWhisper project is ready to go live!"
