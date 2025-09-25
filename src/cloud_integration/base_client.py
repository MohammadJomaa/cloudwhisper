#!/usr/bin/env python3
"""
Base Cloud Client - Abstract base class for all cloud providers
"""

import yaml
import json
import os
import structlog
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = structlog.get_logger(__name__)

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class BaseCloudClient(ABC):
    """Abstract base class for all cloud providers."""
    
    def __init__(self, provider: str, account_id: str = "default", config_path: str = "src/config/cloud_accounts.yaml"):
        """Initialize cloud client with specific provider and account."""
        self.provider = provider
        self.account_id = account_id
        self.config = self._load_account_config(config_path)
        self.client = None
        self._init_client()
    
    def _load_account_config(self, config_path: str) -> Dict[str, Any]:
        """Load cloud account configuration."""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                return config
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using default settings")
            return {"cloud_providers": {self.provider: {"accounts": {"default": {"name": "Default", "region": "us-east-1"}}}}}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing config file: {e}")
            return {"cloud_providers": {self.provider: {"accounts": {"default": {"name": "Default", "region": "us-east-1"}}}}}
    
    @abstractmethod
    def _init_client(self):
        """Initialize cloud client for the selected account."""
        pass
    
    @abstractmethod
    def get_account_info(self) -> Dict[str, Any]:
        """Get current account information."""
        pass
    
    @abstractmethod
    def list_available_accounts(self) -> List[Dict[str, Any]]:
        """List all available accounts for this provider."""
        pass
    
    @abstractmethod
    def switch_account(self, account_id: str) -> bool:
        """Switch to a different account."""
        pass
    
    @abstractmethod
    def list_instances(self) -> Dict[str, Any]:
        """List compute instances (EC2, Compute Engine, etc.)."""
        pass
    
    @abstractmethod
    def list_storage_buckets(self) -> Dict[str, Any]:
        """List storage buckets (S3, Cloud Storage, etc.)."""
        pass
    
    @abstractmethod
    def get_monitoring_alerts(self) -> Dict[str, Any]:
        """Get monitoring alerts (CloudWatch, Cloud Monitoring, etc.)."""
        pass
    
    def format_result(self, data: Dict[str, Any]) -> str:
        """Format the result for display with enhanced data."""
        return json.dumps(data, cls=DateTimeEncoder, indent=2) 