# Contributing to Retro Board

Thank you for your interest in contributing to Retro Board! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- Git

### Backend Setup

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

## Code Style Guidelines

### Python (Backend)

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guide
- Use type hints for function parameters and return values
- Maximum line length: 100 characters
- Use meaningful variable and function names

### TypeScript (Frontend)

- Follow the ESLint configuration in the project
- Use TypeScript strict mode
- Prefer functional components with hooks
- Use meaningful component and variable names

## Pull Request Process

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the code style guidelines
3. **Write or update tests** for your changes if applicable
4. **Update documentation** if you're changing functionality
5. **Ensure all tests pass** before submitting
6. **Create a Pull Request** with a clear description of the changes

### PR Checklist

- [ ] Code follows the project's style guidelines
- [ ] Tests have been added/updated as needed
- [ ] Documentation has been updated as needed
- [ ] All CI checks pass
- [ ] PR description clearly explains the changes

## Issue Reporting

### Bug Reports

When reporting bugs, please include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Browser and OS information
- Screenshots or error logs if applicable

### Feature Requests

When requesting features, please include:

- A clear description of the problem you're trying to solve
- Your proposed solution
- Any alternatives you've considered
- Additional context or mockups if helpful

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm run lint
npm run build
```

## Questions?

If you have questions, feel free to open an issue for discussion.

Thank you for contributing!
