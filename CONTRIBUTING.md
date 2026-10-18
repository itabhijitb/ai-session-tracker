# Contributing to ai-session-tracker

Thank you for your interest in contributing to ai-session-tracker! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and collaborative. We aim to maintain a welcoming environment for all contributors.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- A GitHub account

### Setting Up Development Environment

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-session-tracker.git
   cd ai-session-tracker
   ```

3. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. Install the package in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

5. Run the tests to verify your setup:
   ```bash
   pytest tests/ -v
   ```

## Development Workflow

### Branch Naming

Use descriptive branch names:
- `feature/your-feature-name`
- `bugfix/your-bug-fix`
- `docs/your-documentation-update`

### Making Changes

1. Create a new branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and write tests for new functionality

3. Run linting and formatting:
   ```bash
   ruff check src/ tests/
   ruff format src/ tests/
   ```

4. Run tests:
   ```bash
   pytest tests/ -v
   ```

5. Commit your changes with a clear message:
   ```bash
   git commit -m "Add support for new AI agent"
   ```

6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

7. Create a Pull Request on GitHub

## Adding Support for a New AI Agent

To add support for a new AI coding agent:

1. Create a new adapter file in `src/ai_session_tracker/adapters/`:
   - Name it after the agent (e.g., `new_agent.py`)
   - Inherit from `BaseAdapter`
   - Implement the required methods: `is_available()`, `list_sessions()`, `deep_search()`
   - Optionally implement `preview()` for conversation preview

2. Register the adapter in `src/ai_session_tracker/adapters/__init__.py`:
   - Import your new adapter
   - Add it to the `ALL_ADAPTERS` list

3. Add the agent to the RESUME_COMMANDS dict in `src/ai_session_tracker/cli.py`

4. Add the agent to the agent_paths dict in the `status()` command

5. Update `src/ai_session_tracker/setup.py` to update AGENTS.md for the new agent

6. Write tests for the new adapter in `tests/`

7. Update documentation (README.md, CHANGELOG.md)

8. Run tests and linting to ensure everything works

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_engine.py -v

# Run with coverage
pytest tests/ --cov=ai_session_tracker --cov-report=html
```

### Writing Tests

- Write tests for new functionality
- Ensure tests are independent and can run in any order
- Use descriptive test names
- Follow the existing test patterns in `tests/test_engine.py`

## Code Style

We use:
- **Ruff** for linting and formatting
- Line length: 120 characters
- Follow PEP 8 guidelines

### Checking Code Style

```bash
# Check for linting issues
ruff check src/ tests/

# Format code
ruff format src/ tests/

# Check format without modifying
ruff format --check src/ tests/
```

## Documentation

### Updating Documentation

- Update `README.md` for user-facing changes
- Update `CHANGELOG.md` for version changes
- Add docstrings to new functions and classes
- Update inline comments for complex logic

### API Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Include type hints for function parameters and return values

## Pull Request Process

1. Ensure your code passes all tests
2. Ensure your code passes linting checks
3. Update documentation as needed
4. Update CHANGELOG.md with your changes
5. Create a descriptive PR title and description
6. Link to any related issues
7. Wait for code review

### PR Checklist

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] Commit messages are clear
- [ ] PR description explains the changes

## Releasing

Releases are managed by the maintainers:

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create a git tag: `git tag v0.1.0`
4. Push the tag: `git push origin v0.1.0`
5. GitHub Actions will automatically build and publish to PyPI

## Questions?

If you have questions, feel free to:
- Open an issue on GitHub
- Ask in a Pull Request
- Contact the maintainers

Thank you for contributing!
