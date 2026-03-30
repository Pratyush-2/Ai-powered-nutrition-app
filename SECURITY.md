# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please report it responsibly.

**Please DO NOT open a public GitHub issue for security vulnerabilities.**

### How to Report

1. **Email**: Send a detailed report to [pratyush0040@gmail.com](mailto:pratyush0040@gmail.com)
2. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

| Action | Timeframe |
|--------|-----------|
| Acknowledgment | Within 48 hours |
| Initial assessment | Within 1 week |
| Fix deployed | Within 2 weeks (critical) |

## Security Best Practices

### For Contributors

- **Never commit secrets** — Use environment variables via `.env` (see `.env.example`)
- **Review changes** — Check `git diff --staged` before committing
- **Keep dependencies updated** — Run `pip audit` and `safety check` regularly
- **Use HTTPS** — All API communication should use TLS in production

### For Deployment

- Enable rate limiting via `RATE_LIMIT_PER_MINUTE` environment variable
- Use a production database (PostgreSQL) instead of SQLite
- Set strong `SECRET_KEY` and JWT expiration
- Enable CORS only for trusted origins
- Run behind a reverse proxy (e.g., Nginx) with TLS

### Credential Management

| File | Purpose | Committed? |
|------|---------|------------|
| `.env` | API keys and secrets | ❌ Never — in `.gitignore` |
| `.env.example` | Template with placeholder values | ✅ Yes |
| `*.json` (service accounts) | Cloud provider credentials | ❌ Never — in `.gitignore` |
| `*.db` | Database files with user data | ❌ Never — in `.gitignore` |

## Automated Security Checks

This project includes a CI pipeline (`.github/workflows/ci.yml`) with:

- **Bandit** — Static analysis for Python security issues
- **Safety** — Dependency vulnerability scanning
- **Flake8** — Code quality and syntax error detection

## Scope

The following are in scope for security reports:

- Authentication and authorization flaws
- Injection vulnerabilities (SQL, command, etc.)
- Data exposure or leakage
- Insecure dependencies
- Misconfigured security headers

## Acknowledgments

We appreciate the security research community. Responsible reporters will be credited in release notes (with permission).
