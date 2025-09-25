#!/usr/bin/env python3
"""
Enhanced AWS Client with Multi-Account Support
"""

import boto3
import yaml
import json
import os
import structlog
from datetime import datetime
from typing import Dict, Any, List, Optional
try:
    from ..cloud_integration.base_client import BaseCloudClient, DateTimeEncoder
except ImportError:
    from cloud_integration.base_client import BaseCloudClient, DateTimeEncoder

# Check if running as subprocess to avoid stdout pollution
import sys
if len(sys.argv) > 1 and sys.argv[1] == "--subprocess":
    # Create a dummy logger that does nothing
    logger = type('DummyLogger', (), {'info': lambda self, x: None, 'error': lambda self, x: None, 'dummy': True})()
else:
    logger = structlog.get_logger(__name__)

class AWSClient(BaseCloudClient):
    """Enhanced AWS client with multi-account support."""
    
    def __init__(self, account_id: str = "default", config_path: str = "src/config/cloud_accounts.yaml"):
        """Initialize AWS client with specific account."""
        self.account_id = account_id
        self.config = self._load_account_config(config_path)
        self.session = None
        self._init_client()
    
    def _init_client(self):
        """Initialize AWS session for the selected account."""
        try:
            account_config = self.config.get("aws_accounts", {}).get(self.account_id, {})
            region = account_config.get("region", "us-east-1")
            
            # Check if we have direct credentials or profile
            if "access_key" in account_config and "secret_key" in account_config:
                # Use direct credentials
                self.session = boto3.Session(
                    aws_access_key_id=account_config["access_key"],
                    aws_secret_access_key=account_config["secret_key"],
                    region_name=region
                )
            else:
                # Use profile (fallback)
                profile = account_config.get("profile", "default")
                self.session = boto3.Session(profile_name=profile, region_name=region)
            
            # Test the session
            sts = self.session.client('sts')
            identity = sts.get_caller_identity()
            
            # Only log if not in subprocess mode
            if hasattr(logger, 'info') and not hasattr(logger, 'dummy'):
                logger.info(f"Connected to AWS account: {identity.get('Account')} in region: {region}")
            
        except Exception as e:
            logger.error(f"Error initializing AWS session for account {self.account_id}: {e}")
            # Fallback to default session
            self.session = boto3.Session()
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get current account information."""
        try:
            sts = self.session.client('sts')
            identity = sts.get_caller_identity()
            
            account_config = self.config.get("aws_accounts", {}).get(self.account_id, {})
            
            return {
                "account_id": self.account_id,
                "account_name": account_config.get("name", "Unknown"),
                "region": account_config.get("region", "Unknown"),
                "aws_account_id": identity.get('Account'),
                "user_arn": identity.get('Arn'),
                "provider": "aws",
                "description": account_config.get("description", "")
            }
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return {"error": str(e)}
    
    def list_available_accounts(self) -> List[Dict[str, Any]]:
        """List all available AWS accounts."""
        accounts = []
        for account_id, config in self.config.get("aws_accounts", {}).items():
            accounts.append({
                "id": account_id,
                "name": config.get("name", account_id),
                "region": config.get("region", "Unknown"),
                "description": config.get("description", "")
            })
        return accounts
    
    def switch_account(self, account_id: str) -> bool:
        """Switch to a different AWS account."""
        try:
            if account_id in self.config.get("aws_accounts", {}):
                self.account_id = account_id
                self._init_client()
                # Only log if not in subprocess mode
                if hasattr(logger, 'info'):
                    logger.info(f"Switched to AWS account: {account_id}")
                return True
            else:
                logger.error(f"Account {account_id} not found in configuration")
                return False
        except Exception as e:
            logger.error(f"Error switching to account {account_id}: {e}")
            return False
    
    def list_instances(self) -> Dict[str, Any]:
        """List EC2 instances."""
        return self.list_ec2_instances()
    
    def list_storage_buckets(self) -> Dict[str, Any]:
        """List S3 buckets."""
        return self.list_s3_buckets()
    
    def get_monitoring_alerts(self) -> Dict[str, Any]:
        """Get CloudWatch alarms."""
        return self.get_cloudwatch_alarms()
    
    def list_ec2_instances(self) -> Dict[str, Any]:
        """List EC2 instances with enhanced information."""
        try:
            ec2 = self.session.client('ec2')
            response = ec2.describe_instances()
            
            instances = []
            running_count = 0
            stopped_count = 0
            
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    # Get instance type details
                    instance_type = instance.get('InstanceType', 'unknown')
                    cpu_cores = self._get_instance_cpu_cores(instance_type)
                    memory_gb = self._get_instance_memory_gb(instance_type)
                    
                    # Get network interfaces
                    network_interfaces = []
                    for ni in instance.get('NetworkInterfaces', []):
                        network_interfaces.append({
                            'id': ni.get('NetworkInterfaceId'),
                            'subnet_id': ni.get('SubnetId'),
                            'vpc_id': ni.get('VpcId'),
                            'private_ip': ni.get('PrivateIpAddress'),
                            'public_ip': ni.get('Association', {}).get('PublicIp'),
                            'security_groups': [sg.get('GroupName') for sg in ni.get('Groups', [])]
                        })
                    
                    # Get block device mappings
                    block_devices = []
                    for bdm in instance.get('BlockDeviceMappings', []):
                        block_devices.append({
                            'device_name': bdm.get('DeviceName'),
                            'volume_id': bdm.get('Ebs', {}).get('VolumeId'),
                            'delete_on_termination': bdm.get('Ebs', {}).get('DeleteOnTermination', False)
                        })
                    
                    # Get tags
                    tags = {}
                    for tag in instance.get('Tags', []):
                        tags[tag.get('Key')] = tag.get('Value')
                    
                    instance_info = {
                        'instance_id': instance.get('InstanceId'),
                        'name': tags.get('Name', 'Unnamed'),
                        'instance_type': instance_type,
                        'cpu_cores': cpu_cores,
                        'memory_gb': memory_gb,
                        'status': instance.get('State', {}).get('Name'),
                        'region': self.session.region_name,
                        'availability_zone': instance.get('Placement', {}).get('AvailabilityZone'),
                        'launch_time': instance.get('LaunchTime').isoformat() if instance.get('LaunchTime') else None,
                        'network_interfaces': network_interfaces,
                        'block_devices': block_devices,
                        'tags': tags,
                        'platform': instance.get('Platform'),
                        'monitoring': instance.get('Monitoring', {}).get('State'),
                        'iam_instance_profile': instance.get('IamInstanceProfile', {}).get('Arn'),
                        'ebs_optimized': instance.get('EbsOptimized', False),
                        'root_device_type': instance.get('RootDeviceType'),
                        'root_device_name': instance.get('RootDeviceName')
                    }
                    
                    instances.append(instance_info)
                    
                    # Count by status
                    if instance.get('State', {}).get('Name') == 'running':
                        running_count += 1
                    elif instance.get('State', {}).get('Name') == 'stopped':
                        stopped_count += 1
            
            return {
                "success": True,
                "instances": instances,
                "count": len(instances),
                "running_count": running_count,
                "stopped_count": stopped_count
            }
            
        except Exception as e:
            logger.error(f"Error listing EC2 instances: {e}")
            return {"success": False, "error": str(e)}
    
    def list_s3_buckets(self) -> Dict[str, Any]:
        """List S3 buckets with enhanced information."""
        try:
            s3 = self.session.client('s3')
            response = s3.list_buckets()
            
            buckets = []
            total_size = 0
            total_objects = 0
            
            for bucket in response['Buckets']:
                bucket_name = bucket['Name']
                
                try:
                    # Get bucket location
                    location_response = s3.get_bucket_location(Bucket=bucket_name)
                    location = location_response.get('LocationConstraint') or 'us-east-1'
                    
                    # Get bucket versioning
                    try:
                        versioning_response = s3.get_bucket_versioning(Bucket=bucket_name)
                        versioning = versioning_response.get('Status') == 'Enabled'
                    except:
                        versioning = False
                    
                    # Get bucket encryption
                    try:
                        encryption_response = s3.get_bucket_encryption(Bucket=bucket_name)
                        encryption = 'Enabled'
                    except:
                        encryption = 'NotEnabled'
                    
                    # Get bucket size and object count (sample)
                    try:
                        paginator = s3.get_paginator('list_objects_v2')
                        bucket_size = 0
                        object_count = 0
                        
                        for page in paginator.paginate(Bucket=bucket_name, MaxItems=1000):
                            if 'Contents' in page:
                                for obj in page['Contents']:
                                    bucket_size += obj.get('Size', 0)
                                    object_count += 1
                        
                        total_size += bucket_size
                        total_objects += object_count
                    except Exception:
                        bucket_size = 0
                        object_count = 0
                    
                    bucket_info = {
                        'name': bucket_name,
                        'location': location,
                        'versioning': versioning,
                        'encryption': encryption,
                        'size_bytes': bucket_size,
                        'size_gb': round(bucket_size / (1024 * 1024 * 1024), 2),
                        'object_count': object_count,
                        'created': bucket.get('CreationDate').isoformat() if bucket.get('CreationDate') else None
                    }
                    buckets.append(bucket_info)
                    
                except Exception as e:
                    logger.warning(f"Error getting details for bucket {bucket_name}: {e}")
                    # Add basic info even if details fail
                    bucket_info = {
                        'name': bucket_name,
                        'location': 'Unknown',
                        'versioning': False,
                        'encryption': 'Unknown',
                        'size_bytes': 0,
                        'size_gb': 0,
                        'object_count': 0,
                        'created': bucket.get('CreationDate').isoformat() if bucket.get('CreationDate') else None
                    }
                    buckets.append(bucket_info)
            
            return {
                "success": True,
                "buckets": buckets,
                "count": len(buckets),
                "total_size_gb": round(total_size / (1024 * 1024 * 1024), 2),
                "total_objects": total_objects,
                "encrypted_buckets": len([b for b in buckets if b['encryption'] == 'Enabled']),
                "versioned_buckets": len([b for b in buckets if b['versioning']])
            }
            
        except Exception as e:
            logger.error(f"Error listing S3 buckets: {e}")
            return {"success": False, "error": str(e)}
    
    def get_cloudwatch_alarms(self) -> Dict[str, Any]:
        """Get CloudWatch alarms with enhanced information."""
        try:
            cloudwatch = self.session.client('cloudwatch')
            response = cloudwatch.describe_alarms()
            
            alarms = []
            enabled_count = 0
            disabled_count = 0
            
            for alarm in response['MetricAlarms']:
                # Get alarm actions
                actions = []
                if alarm.get('AlarmActions'):
                    actions.extend(alarm['AlarmActions'])
                if alarm.get('OKActions'):
                    actions.extend(alarm['OKActions'])
                
                alarm_info = {
                    'name': alarm.get('AlarmName'),
                    'description': alarm.get('AlarmDescription'),
                    'metric_name': alarm.get('MetricName'),
                    'namespace': alarm.get('Namespace'),
                    'state': alarm.get('StateValue'),
                    'state_reason': alarm.get('StateReason'),
                    'actions': actions,
                    'threshold': alarm.get('Threshold'),
                    'comparison_operator': alarm.get('ComparisonOperator'),
                    'evaluation_periods': alarm.get('EvaluationPeriods'),
                    'period': alarm.get('Period'),
                    'statistic': alarm.get('Statistic'),
                    'treat_missing_data': alarm.get('TreatMissingData'),
                    'created': alarm.get('AlarmConfigurationUpdatedTimestamp').isoformat() if alarm.get('AlarmConfigurationUpdatedTimestamp') else None
                }
                
                alarms.append(alarm_info)
                
                # Count by state
                if alarm.get('StateValue') == 'ALARM':
                    enabled_count += 1
                else:
                    disabled_count += 1
            
            return {
                "success": True,
                "alerts": alarms,
                "count": len(alarms),
                "enabled_alerts": enabled_count,
                "disabled_alerts": disabled_count
            }
            
        except Exception as e:
            logger.error(f"Error getting CloudWatch alarms: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_instance_cpu_cores(self, instance_type: str) -> int:
        """Get CPU cores for instance type."""
        # Basic mapping - in production, you'd want a more comprehensive mapping
        cpu_mapping = {
            't3.micro': 2, 't3.small': 2, 't3.medium': 2,
            't3.large': 2, 't3.xlarge': 4, 't3.2xlarge': 8,
            'm5.large': 2, 'm5.xlarge': 4, 'm5.2xlarge': 8,
            'c5.large': 2, 'c5.xlarge': 4, 'c5.2xlarge': 8
        }
        return cpu_mapping.get(instance_type, 1)
    
    def _get_instance_memory_gb(self, instance_type: str) -> int:
        """Get memory in GB for instance type."""
        # Basic mapping - in production, you'd want a more comprehensive mapping
        memory_mapping = {
            't3.micro': 1, 't3.small': 2, 't3.medium': 4,
            't3.large': 8, 't3.xlarge': 16, 't3.2xlarge': 32,
            'm5.large': 8, 'm5.xlarge': 16, 'm5.2xlarge': 32,
            'c5.large': 4, 'c5.xlarge': 8, 'c5.2xlarge': 16
        }
        return memory_mapping.get(instance_type, 1) 