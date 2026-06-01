# Contributing to Firearm Detection System

Thank you for your interest in contributing! Here's how to get started.

## 🐛 Reporting Bugs

1. Check if the issue already exists in [Issues](../../issues).
2. If not, open a new issue with:
   - A clear title
   - Steps to reproduce
   - Expected vs. actual behavior
   - Python version, OS, and GPU/CPU info

## 💡 Suggesting Features

Open a GitHub Issue with the `enhancement` label and describe:
- What problem it solves
- How you'd expect it to work

## 🔧 Submitting a Pull Request

1. **Fork** the repository and clone your fork locally.
2. Create a **feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes — keep commits small and focused.
4. **Run tests** before submitting:
   ```bash
   pip install pytest
   pytest tests/
   ```
5. **Push** your branch and open a Pull Request against `main`.

## ✅ Code Style

- Follow [PEP 8](https://pep8.org/) for Python code.
- Use descriptive variable and function names.
- Add docstrings to new functions.
- Keep lines under 100 characters where possible.

## 📋 Commit Message Format

Use conventional commits for clear history:

```
feat: add real-time video inference support
fix: resolve bounding box scaling bug on hi-DPI screens
docs: update quick-start guide
refactor: extract detection logic into separate module
```

## ⚠️ Ethical Responsibility

All contributions must align with the ethical use guidelines in the [LICENSE](LICENSE).
Do not add features designed for unauthorized surveillance or harmful use.

---

By contributing, you agree your work will be released under the project's [MIT License](LICENSE).
