#!/usr/bin/env python3
"""
CloudWhisper - AI-Powered AWS Chatbot Launcher
Built on Model Context Protocol (MCP) for seamless AI-cloud communication
"""

import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from chatbot.multi_cloud_chatbot import AWSChatbot

def main():
    """Launch CloudWhisper - AI-powered AWS chatbot."""
    
    print("🌟 CloudWhisper - AI-Powered AWS Chatbot")
    print("=" * 60)
    print("Ask me anything about your AWS infrastructure!")
    print("I'll whisper intelligent insights and recommendations.")
    print("Type 'help' for commands, 'quit' to exit")
    print("=" * 60)
    
    try:
        # Initialize the AI chatbot
        chatbot = AWSChatbot()
        
        # Start the chatbot
        chatbot.run()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main() 