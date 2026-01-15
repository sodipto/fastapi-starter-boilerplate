# Package Management Guide

This guide covers Python package management for the FastAPI Starter Boilerplate project.

## Installing Dependencies

### Install all required packages
```bash
pip install -r requirements.txt
```
Installs all required packages from requirements.txt.

### Install a specific package
```bash
pip install <package-name>
```

### Install a package with specific version
```bash
pip install <package-name>==<version>
```

### Install from a different requirements file
```bash
pip install -r requirements-dev.txt
```

## Managing Requirements

### Update requirements.txt
```bash
pip freeze > requirements.txt
```
Updates requirements.txt with currently installed packages.

### Generate requirements from current environment
```bash
pip list --format=freeze > requirements.txt
```

### Install and add to requirements
```bash
pip install <package-name>
pip freeze > requirements.txt
```

## Virtual Environment Management

### Create virtual environment
```bash
# Using venv
python -m venv venv

# Using virtualenv
virtualenv venv
```

### Activate virtual environment
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Deactivate virtual environment
```bash
deactivate
```

## Package Information

### List installed packages
```bash
pip list
```

### Show package details
```bash
pip show <package-name>
```

### Check outdated packages
```bash
pip list --outdated
```

## Updating Packages

### Update a specific package
```bash
pip install --upgrade <package-name>
```

### Update all packages
```bash
pip list --outdated --format=freeze | %{$_.split('==')[0]} | %{pip install --upgrade $_}
```

## Uninstalling Packages

### Uninstall a package
```bash
pip uninstall <package-name>
```

### Uninstall multiple packages
```bash
pip uninstall -r requirements.txt -y
```

## Best Practices

- Always use virtual environments to isolate project dependencies
- Keep requirements.txt up to date
- Specify exact versions in production requirements
- Use separate requirements files for development and production
- Regularly check for security vulnerabilities in dependencies
- Review and test package updates before deploying to production

## Security

### Check for security vulnerabilities
```bash
pip install safety
safety check
```

### Audit packages
```bash
pip audit
```

## Development vs Production Dependencies

Consider splitting requirements into multiple files:

- `requirements.txt` - Production dependencies only
- `requirements-dev.txt` - Development dependencies (testing, linting, etc.)
- `requirements-test.txt` - Testing dependencies

### Install all dependencies (dev + prod)
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```
