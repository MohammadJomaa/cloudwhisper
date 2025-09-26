# 🧪 CloudWhisper - Testing Guide

This document provides comprehensive information about testing the CloudWhisper project.

## 📋 Test Overview

The project includes a comprehensive test suite covering:

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing  
- **Configuration Tests**: YAML config validation
- **Web UI Tests**: Flask application testing
- **Basic Functionality Tests**: Smoke tests for core functionality

## 🚀 Quick Start

### Run All Tests
```bash
python3 simple_test.py          # Basic functionality test
python3 run_tests.py           # Full test suite
```

### Run Specific Test Categories
```bash
python3 run_tests.py --unit         # Unit tests only
python3 run_tests.py --integration  # Integration tests only
python3 run_tests.py --config       # Configuration tests only
python3 run_tests.py --web          # Web UI tests only
```

### Run Individual Test Files
```bash
python3 -m pytest tests/test_aws_client.py -v
python3 -m pytest tests/test_mcp_server.py -v
python3 -m pytest tests/test_ai_integration.py -v
```

## 📁 Test Structure

```
tests/
├── __init__.py                    # Test package
├── test_aws_client.py            # AWS client unit tests
├── test_mcp_server.py            # MCP server unit tests
├── test_ai_integration.py        # AI integration unit tests
├── test_integration.py            # Integration tests
├── test_config_validation.py     # Configuration tests
├── test_web_ui.py                # Web UI tests
└── test_runner.py                # Test runner utility
```

## 🧪 Test Categories

### 1. Unit Tests

**Purpose**: Test individual components in isolation

**Files**:
- `test_aws_client.py` - AWS client functionality
- `test_mcp_server.py` - MCP server protocol
- `test_ai_integration.py` - AI integration (ChatGPT/Claude)

**Coverage**:
- AWS client initialization and methods
- MCP server request/response handling
- AI client initialization and prompt formatting
- Error handling and edge cases

### 2. Integration Tests

**Purpose**: Test complete workflows end-to-end

**Files**:
- `test_integration.py` - Complete workflow testing

**Coverage**:
- MCP server to AI chatbot communication
- AWS account switching
- Data flow from cloud APIs to AI analysis
- Error handling in integration scenarios

### 3. Configuration Tests

**Purpose**: Validate configuration files and settings

**Files**:
- `test_config_validation.py` - Configuration validation

**Coverage**:
- YAML configuration file parsing
- Required field validation
- AWS account configuration
- AI API key validation
- Environment variable handling

### 4. Web UI Tests

**Purpose**: Test Flask web application

**Files**:
- `test_web_ui.py` - Web UI functionality

**Coverage**:
- Flask route testing
- API endpoint functionality
- JSON request/response handling
- Error handling
- Session management

## 🔧 Test Configuration

### Pytest Configuration (`pytest.ini`)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers --disable-warnings
```

### Test Markers
- `unit` - Unit tests
- `integration` - Integration tests
- `config` - Configuration tests
- `web` - Web UI tests
- `slow` - Slow running tests
- `aws` - Tests requiring AWS credentials
- `gcp` - Tests requiring GCP credentials
- `ai` - Tests requiring AI API keys

## 🚀 Running Tests

### Basic Functionality Test
```bash
python3 simple_test.py
```
**What it tests**:
- File structure validation
- Dependency checking
- Configuration file parsing
- Basic module imports
- Core functionality smoke tests

### Full Test Suite
```bash
python3 run_tests.py
```
**What it tests**:
- All unit tests
- Integration tests
- Configuration validation
- Web UI tests
- Comprehensive coverage

### Individual Test Categories
```bash
python3 run_tests.py --unit         # AWS client, MCP server, AI integration
python3 run_tests.py --integration  # End-to-end workflows
python3 run_tests.py --config       # Configuration validation
python3 run_tests.py --web          # Flask web application
```

### Test Report Generation
```bash
python3 run_tests.py --report
```
**Generates**:
- HTML coverage report (`htmlcov/index.html`)
- Terminal coverage summary
- Detailed test results

## 📊 Test Results

### Expected Test Results
```
📊 Test Summary
==================================================
File Structure: ✅ PASSED
Dependencies: ✅ PASSED
Configuration Files: ✅ PASSED
Web UI: ✅ PASSED
MCP Server: ✅ PASSED
AI Integration: ✅ PASSED
AWS Integration: ✅ PASSED

Overall: 7/7 tests passed
```

### Test Coverage
- **Unit Tests**: 15+ test cases
- **Integration Tests**: 8+ test cases
- **Configuration Tests**: 10+ test cases
- **Web UI Tests**: 20+ test cases
- **Total**: 50+ test cases

## 🔍 Troubleshooting

### Common Issues

#### 1. Import Errors
```
ImportError: attempted relative import beyond top-level package
```
**Solution**: The project uses flexible imports that work in both module and standalone contexts.

#### 2. Missing Dependencies
```
❌ package-name - NOT INSTALLED
```
**Solution**: Install missing packages:
```bash
pip install -r requirements.txt
```

#### 3. Configuration Errors
```
❌ Configuration file error
```
**Solution**: Check YAML syntax and required fields in config files.

#### 4. AWS Credentials
```
❌ AWS session creation failed
```
**Solution**: Configure AWS credentials or use mock tests.

### Debug Mode
```bash
python3 -m pytest tests/ -v --tb=long --capture=no
```

### Verbose Output
```bash
python3 run_tests.py --all -v
```

## 📈 Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: python3 simple_test.py
```

## 🎯 Test Best Practices

### 1. Mock External Services
- Use mocks for AWS API calls
- Mock AI API calls (OpenAI/Anthropic)
- Mock file system operations

### 2. Test Data Management
- Use temporary files for config testing
- Clean up test artifacts
- Use fixtures for common test data

### 3. Error Handling
- Test both success and failure scenarios
- Validate error messages
- Test timeout handling

### 4. Performance Testing
- Test with large datasets
- Monitor memory usage
- Test concurrent operations

## 📚 Additional Resources

### Test Documentation
- [pytest Documentation](https://docs.pytest.org/)
- [Flask Testing](https://flask.palletsprojects.com/en/2.0.x/testing/)
- [AWS Testing](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/testing.html)

### Project Documentation
- [README.md](README.md) - Project overview
- [MULTI_ACCOUNT_SETUP.md](MULTI_ACCOUNT_SETUP.md) - AWS setup
- [MULTI_CLOUD_SETUP.md](MULTI_CLOUD_SETUP.md) - Cloud setup

## 🎉 Success Criteria

A successful test run should show:
- ✅ All basic functionality tests pass
- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ All configuration tests pass
- ✅ All web UI tests pass
- ✅ No critical errors or warnings
- ✅ Test coverage > 80%

---

**Happy Testing! 🧪✨**
