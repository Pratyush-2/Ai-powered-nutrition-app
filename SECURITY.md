# Security Guidelines

## 🔒 Important Security Information

### Credentials Management

**NEVER commit the following files to git:**
- `analog-reef-470415-q6-b8ddae1e11b3.json` - Google Cloud Vision API credentials
- `.env` - Environment variables with API keys
- `*.db` - Database files containing user data
- Any files containing API keys, passwords, or secrets

### Google Cloud Vision API Credentials

The credentials file `analog-reef-470415-q6-b8ddae1e11b3.json` is:
- ✅ Already in `.gitignore` (line 137)
- ✅ Should remain local to your machine
- ✅ Should NOT be shared or committed

**If credentials are accidentally committed:**
1. Remove from git history: `git rm --cached analog-reef-470415-q6-b8ddae1e11b3.json`
2. Revoke the service account in Google Cloud Console
3. Generate new credentials
4. Update `.gitignore` if needed

### Environment Variables

Use `.env` file for local development (already in `.gitignore`):
```bash
# Copy the example file
cp .env.example .env

# Edit with your actual keys
# NEVER commit .env to git
```

### Database Files

All database files (`*.db`, `*.sqlite`, `*.sqlite3`) are ignored by git.
- Database files contain user data and should never be committed
- They are generated locally when the application runs
- Backup databases separately if needed

## 🛡️ Best Practices

1. **Never commit secrets** - Use environment variables
2. **Review changes** - Check `git status` before committing
3. **Use .env.example** - Document required environment variables
4. **Rotate credentials** - Regularly update API keys
5. **Monitor access** - Check Google Cloud Console for unusual activity

## 📞 Security Issues

If you discover a security vulnerability:
1. **DO NOT** create a public issue
2. Contact the repository maintainer privately
3. Provide details of the vulnerability
4. Allow time for a fix before public disclosure

## ✅ Security Checklist

Before committing:
- [ ] No API keys in code
- [ ] No credentials files tracked
- [ ] No database files tracked
- [ ] `.env` file not committed
- [ ] Sensitive data removed from logs
- [ ] Dependencies are up-to-date

