# Safe Package Update Guide for DeepHunter

## Quick Start

### 1. Check for Vulnerabilities
```bash
# Install pip-audit (security vulnerability scanner)
pip install pip-audit

# Scan your requirements.txt for known CVEs
pip-audit -r requirements.txt
```

### 2. Run the Automated Checker
```bash
python check_vulnerabilities.py
```

This script will:
- Scan for CVEs in your current packages
- Check for available updates
- Create `requirements.updated.txt` with suggested versions

## Manual Update Process

### Step 1: Create a Test Environment
```bash
# Create a new virtual environment for testing
python -m venv test_env

# Activate it
test_env\Scripts\activate  # Windows
# source test_env/bin/activate  # Linux/Mac

# Install current packages
pip install -r requirements.txt
```

### Step 2: Update Packages Selectively

**Critical packages to prioritize (common CVE targets):**
- `requests` - HTTP library (frequent CVEs)
- `Django` - Web framework (security critical)
- `celery` - Task queue
- `bleach` - HTML sanitization
- `lxml` - XML parser
- `Authlib` - Authentication

**Update strategy:**
```bash
# Check specific package for CVEs
pip-audit | grep "package-name"

# Update specific package
pip install --upgrade package-name

# Pin the new version
pip freeze | grep package-name >> requirements.new.txt
```

### Step 3: Test Your Application

```bash
# Run Django checks
python manage.py check

# Run tests
python manage.py test

# Try migrations
python manage.py makemigrations --dry-run
python manage.py migrate --plan

# Start development server
python manage.py runserver
```

### Step 4: Verify Compatibility

Check for breaking changes in major releases:
- Django 5.2.x → Check release notes
- celery 5.x → Review changelog
- numpy 2.x → Major version change!

### Step 5: Apply Updates

```bash
# Backup current requirements
copy requirements.txt requirements.backup.txt

# Apply updates
copy requirements.updated.txt requirements.txt

# Install in production environment
pip install -r requirements.txt --upgrade
```

## Package-Specific Notes

### Django (Currently 5.2.8)
- Check: https://docs.djangoproject.com/en/5.2/releases/
- Security updates are released frequently
- Minor version updates (5.2.x) are usually safe

### NumPy (Currently 2.2.6)
- Version 2.x is a major update
- May have breaking changes from 1.x
- Test scientific/array operations carefully

### Requests (Currently 2.32.5)
- Commonly targeted for CVEs
- Keep updated to latest 2.x version
- Breaking changes unlikely in minor updates

### Celery (Currently 5.5.3)
- Check broker compatibility (Redis, RabbitMQ)
- Review task signatures after updates

## Alternative: Incremental Updates

Update packages one at a time to isolate issues:

```bash
# 1. Update security-critical packages first
pip install --upgrade requests Django bleach

# 2. Test
python manage.py test

# 3. Update remaining packages
pip install --upgrade celery redis openai

# 4. Test again
python manage.py test
```

## Continuous Monitoring

### Add to CI/CD Pipeline
```yaml
# Example GitHub Actions workflow
- name: Security Scan
  run: |
    pip install pip-audit
    pip-audit -r requirements.txt
```

### Regular Schedule
- Weekly: Run `pip-audit` to check for new CVEs
- Monthly: Update non-critical packages
- Immediately: Update when CVE affects your packages

## Rollback Plan

If updates break your application:

```bash
# Restore backup
copy requirements.backup.txt requirements.txt

# Reinstall old versions
pip install -r requirements.txt --force-reinstall

# Alternative: Use git
git checkout requirements.txt
```

## Tools & Resources

- **pip-audit**: https://pypi.org/project/pip-audit/
- **Safety**: Alternative CVE checker - `pip install safety && safety check`
- **Dependabot**: Automated updates on GitHub
- **Snyk**: Comprehensive vulnerability scanner
- **PyUp**: Automated Python security updates

## Best Practices

1. ✅ Always test in isolated environment first
2. ✅ Pin exact versions in requirements.txt (use ==)
3. ✅ Keep a backup of working requirements.txt
4. ✅ Run full test suite after updates
5. ✅ Update documentation with version changes
6. ✅ Check package changelogs for breaking changes
7. ✅ Monitor security advisories regularly
8. ❌ Don't update all packages blindly
9. ❌ Don't skip testing after updates
10. ❌ Don't use loose version constraints in production
