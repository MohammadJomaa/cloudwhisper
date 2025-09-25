# Contributing to CloudWhisper

Thank you for your interest in contributing to CloudWhisper! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues
- Use the [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md) for bugs
- Use the [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md) for new features
- Search existing issues before creating new ones
- Provide detailed information about your environment

### Code Contributions
1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Add tests** for your changes
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

## 🛠️ Development Setup

### Prerequisites
- Python 3.8 or higher
- Git
- AWS Account (for testing)

### Setup Instructions
```bash
# Clone your fork
git clone https://github.com/yourusername/cloudwhisper.git
cd cloudwhisper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov flake8

# Run tests
pytest tests/

# Run linting
flake8 src/
```

## 📝 Code Style

### Python Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Keep functions small and focused
- Use meaningful variable names

### Example:
```python
def get_aws_instances(account_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve EC2 instances for the specified AWS account.
    
    Args:
        account_id: The AWS account ID to query
        
    Returns:
        List of instance dictionaries with metadata
        
    Raises:
        AWSClientError: If AWS API call fails
    """
    # Implementation here
    pass
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_aws_client.py
```

### Writing Tests
- Write tests for new functionality
- Aim for high test coverage
- Use descriptive test names
- Test both success and failure cases

### Example Test:
```python
def test_get_aws_instances_success():
    """Test successful retrieval of AWS instances."""
    # Arrange
    mock_client = Mock()
    mock_client.describe_instances.return_value = {
        'Reservations': [{'Instances': [{'InstanceId': 'i-123'}]}]
    }
    
    # Act
    result = get_aws_instances('123456789012')
    
    # Assert
    assert len(result) == 1
    assert result[0]['InstanceId'] == 'i-123'
```

## 📋 Pull Request Guidelines

### Before Submitting
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No new warnings introduced
- [ ] Self-review completed

### PR Description
- Clearly describe what the PR does
- Reference any related issues
- Include screenshots for UI changes
- Add testing instructions if needed

## 🏷️ Commit Message Format

Use conventional commits format:
```
type(scope): description

[optional body]

[optional footer]
```

### Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### Examples:
```
feat(aws): add support for RDS instances
fix(ui): resolve initialization timeout issue
docs(readme): update installation instructions
```

## 🐛 Bug Reports

When reporting bugs, please include:
- **Environment details**: OS, Python version, browser
- **Steps to reproduce**: Clear, numbered steps
- **Expected vs actual behavior**
- **Screenshots or error logs**
- **AWS configuration details** (account ID, region, services)

## 💡 Feature Requests

When suggesting features:
- **Describe the problem** you're trying to solve
- **Explain your proposed solution**
- **Provide use cases** and examples
- **Consider alternatives** you've explored

## 📚 Documentation

### Code Documentation
- Use docstrings for all public functions
- Include type hints
- Add inline comments for complex logic
- Update README.md for user-facing changes

### API Documentation
- Document all API endpoints
- Include request/response examples
- Specify error codes and messages

## 🔒 Security

### Security Issues
- Report security vulnerabilities privately to maintainers
- Do not create public issues for security problems
- Use responsible disclosure practices

### Code Security
- Never commit secrets or credentials
- Use environment variables for sensitive data
- Validate all user inputs
- Follow AWS security best practices

## 🎯 Areas for Contribution

### High Priority
- [ ] Multi-cloud support (GCP, Azure)
- [ ] Advanced analytics and reporting
- [ ] Mobile responsiveness improvements
- [ ] Performance optimizations

### Medium Priority
- [ ] Additional AWS services integration
- [ ] Enhanced error handling
- [ ] More comprehensive tests
- [ ] Documentation improvements

### Low Priority
- [ ] UI/UX enhancements
- [ ] Additional language support
- [ ] Plugin system
- [ ] Advanced configuration options

## 📞 Getting Help

- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Create issues for bugs and feature requests
- **Email**: Contact maintainers for sensitive issues

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

Thank you for contributing to CloudWhisper! 🚀
