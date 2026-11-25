# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| dev | ✅ |

## Reporting a vulnerability

Please **do not** open a public issue for security vulnerabilities.

Instead, email the maintainers or open a private security advisory via GitHub.
Include:
- Description of the vulnerability
- Steps to reproduce
- Affected components (Rust core / Python GUI / DB)
- Potential impact

We aim to acknowledge reports within 72 hours.

## Scope notes

- brilliantcheck is **read-only**: it does not write to devices.
- Never commit secrets (API keys, tokens, signing keys, user data) or device identifiers (IMEI/serial) to the repo.
- Hardware identifiers handled by the tool must be treated as sensitive.