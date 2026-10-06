# Production security checklist

1. HTTPS/TLS: terminate TLS at a trusted reverse proxy/load balancer; redirect HTTP to HTTPS and enable HSTS.
2. Authentication: rotate `APP_SECRET_KEY`; enforce 16+ character passphrases; use server-side sessions; never commit `.env`.
3. Admin MFA: keep TOTP enabled for all admin users and protect the enrollment secret.
4. Rate limits: use a shared Redis-backed limiter if running more than one API process.
5. WAF: place Cloudflare/AWS WAF/Sucuri in front of the application with OWASP protections and DDoS/rate rules.
6. Patching: run Dependabot/Snyk and package-manager audits; remove default credentials; re-run the security test suite after updates.
7. Headers: keep CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy and Permissions-Policy enabled.
8. Backups: schedule encrypted off-site backups of the production database and model artifacts; perform restore drills.
9. Logs: ship application audit logs to isolated storage; avoid storing passwords, session tokens, OTPs or raw secrets in logs.
10. Access control: keep `/profile/me` as the user self-service boundary; teacher/admin cohort access is role-gated.
