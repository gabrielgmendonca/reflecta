# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please report it responsibly.

### How to Report

1. **Do not** open a public GitHub issue for security vulnerabilities
2. Send a detailed report to the repository maintainer via GitHub's private vulnerability reporting feature
3. Include as much information as possible:
   - Type of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your report within 48 hours
- **Assessment**: We will assess the vulnerability and determine its severity
- **Updates**: We will keep you informed about our progress
- **Resolution**: We aim to resolve critical vulnerabilities as quickly as possible
- **Credit**: We will credit you for the discovery (unless you prefer to remain anonymous)

### Scope

The following are in scope for security reports:

- Authentication and authorization issues
- Data exposure vulnerabilities
- Injection vulnerabilities (SQL, XSS, etc.)
- WebSocket security issues
- Server-side vulnerabilities

### Out of Scope

- Vulnerabilities in dependencies (please report these to the respective projects)
- Issues that require physical access to a user's device
- Social engineering attacks

## Security Best Practices

When deploying Retro Board:

1. Use HTTPS in production
2. Set secure environment variables
3. Keep dependencies updated
4. Use strong session secrets
5. Configure proper CORS settings

Thank you for helping keep Retro Board secure!
