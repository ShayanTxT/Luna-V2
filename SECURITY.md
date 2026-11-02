# Security Policy

## Supported Versions
| Version | Supported |
|---------|-----------|
| 2.5.x   | ✅        |

## Reporting a Vulnerability

**Do not** open a public issue for security vulnerabilities.

Use one of these private channels:

1. **GitHub Security Advisories (preferred):**
   https://github.com/ShayanTxT/Luna-V2/security/advisories/new

2. **Direct contact:**
   Open an issue with title `[SECURITY]` and mention it contains sensitive details, then wait for maintainer to make it private.

We will acknowledge within 48 hours and provide a fix timeline.

## Best Practices
- Never commit `.env` or `WEB_SECRET` (must be >=32 chars)
- Rotate `BOT_TOKEN` if leaked via @BotFather
- Keep `WEB_SECRET` unique per deployment
