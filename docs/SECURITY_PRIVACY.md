# Security and privacy

## Main risks
Misleading links, accidental publication of restricted files, leaked credentials, personal-data exposure, broken links, unsafe third-party embeds, and false confidence from a client-side admin screen.

## Controls
- No secrets in HTML, JS, repository history, or public JSON.
- No client-side password as authorization; public JavaScript can be inspected and bypassed.
- Review and moderate contributions before publication.
- Check external domains; avoid unnecessary unsafe embeds.
- Minimize personal data. Do not collect names, phone numbers, marks, or detailed usage histories without a justified approved purpose and notice.
- Use HTTPS hosting.
- Review third-party CDNs for privacy, availability, and performance impact.
- Document retention/removal for any future upload service.
- Enforce authorization server-side if writing or authentication is added.
- Check Git history for accidentally committed secrets and rotate exposed keys.

## Reporting
Use public issues only for non-sensitive defects. Never post credentials or personal data publicly. Configure a maintainer-controlled private reporting channel before launch.
