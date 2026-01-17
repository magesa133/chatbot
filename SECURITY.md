# 🔒 Security Guidelines

## 🚨 Never Commit Secrets to Git

This repository **must never contain** real API keys, passwords, or other sensitive credentials.

### ✅ What to Do:
- Use `.env` files for local development (already in `.gitignore`)
- Use `env_example.txt` as a template with placeholder values
- Set environment variables in production systems
- Use secure secret management services (AWS Secrets Manager, etc.)

### ❌ What NOT to Do:
- Commit real API keys to `env_example.txt`
- Include passwords in configuration files
- Push `.env` files to version control
- Share credentials in documentation

### 🛡️ Security Checklist:
- [ ] `.env` files are in `.gitignore`
- [ ] `env_example.txt` contains only placeholders
- [ ] No real credentials in documentation
- [ ] No secrets in test files
- [ ] No API keys in source code

### 🚨 If Secrets Are Exposed:
1. **Immediately revoke** the compromised credentials
2. **Generate new keys/tokens** from the service provider
3. **Remove from git history** using `git filter-branch` or BFG Repo Cleaner
4. **Force push** the cleaned history
5. **Update all systems** with new credentials

### 🛠️ Tools for Secret Detection:
- [GitGuardian](https://gitguardian.com/) - Automated secret detection
- [TruffleHog](https://github.com/trufflesecurity/trufflehog) - Secret scanning
- [Gitleaks](https://github.com/gitleaks/gitleaks) - Git secret scanner

### 📞 Report Security Issues:
If you discover security vulnerabilities, please report them privately to the repository maintainer.

---

**🔐 Security is everyone's responsibility. Keep Tanzania's data safe! 🇹🇿**
