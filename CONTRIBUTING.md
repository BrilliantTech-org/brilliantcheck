# Contributing to brilliantcheck

Thank you for your interest in contributing to **brilliantcheck (bdc)**.

## Code of conduct

This project follows our [Code of Conduct](./CODE_OF_CONDUCT.md). By participating you agree to uphold it.

## How to contribute

1. **Fork** the repository and create a feature branch from `main`.
2. **Discuss first** for large changes — open an issue describing the proposal.
3. **Keep changes focused** — one logical change per pull request.
4. **Write tests** for new functionality and bug fixes.
5. **Run checks** before submitting:
   - Rust: `cargo fmt`, `cargo clippy`, `cargo test`
   - Python: `pytest`, linting
6. **Open a pull request** with a clear description and link to any related issue.

## Reporting bugs

Use GitHub Issues. Include:
- Device model / brand
- OS and tool version
- Steps to reproduce
- Expected vs. actual behavior
- Logs (redact IMEI/serial if sensitive)

## Security issues

Do **not** open public issues for security vulnerabilities. See [SECURITY.md](./SECURITY.md).

## License

By contributing you agree that your contributions are licensed under the [MIT License](./LICENSE).