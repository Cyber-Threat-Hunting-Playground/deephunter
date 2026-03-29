"""
Script to check Python packages for known CVEs and suggest safe updates.
Usage: python check_vulnerabilities.py
"""
import subprocess
import sys
import json
from packaging import version as pkg_version

def install_pip_audit():
    """Install pip-audit if not available."""
    print("Checking for pip-audit...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "show", "pip-audit"], 
                      capture_output=True, check=True)
        print("✓ pip-audit is installed")
    except subprocess.CalledProcessError:
        print("Installing pip-audit...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pip-audit"], check=True)
        print("✓ pip-audit installed successfully")

def run_vulnerability_scan():
    """Run pip-audit to scan for vulnerabilities."""
    print("\n" + "="*60)
    print("SCANNING FOR VULNERABILITIES")
    print("="*60 + "\n")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip_audit", "-r", "requirements.txt", "--format", "json"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print("✓ No known vulnerabilities found!")
            return None
        else:
            # Parse JSON output
            try:
                vulns = json.loads(result.stdout)
                return vulns
            except json.JSONDecodeError:
                # Try non-JSON format
                print(result.stdout)
                return result.stdout
                
    except Exception as e:
        print(f"Error running scan: {e}")
        return None

def check_latest_versions():
    """Check for latest versions of all packages."""
    print("\n" + "="*60)
    print("CHECKING FOR PACKAGE UPDATES")
    print("="*60 + "\n")
    
    with open("requirements.txt", "r") as f:
        packages = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    
    updates_available = []
    
    for package in packages:
        if "==" in package:
            name, current_version = package.split("==")
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "index", "versions", name],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                # Parse available versions
                if "Available versions:" in result.stdout:
                    versions_line = result.stdout.split("Available versions:")[1].split("\n")[0]
                    versions = [v.strip() for v in versions_line.split(",")]
                    if versions:
                        latest = versions[0]
                        if latest != current_version:
                            updates_available.append((name, current_version, latest))
                            print(f"📦 {name}: {current_version} → {latest}")
                        else:
                            print(f"✓ {name}: {current_version} (up to date)")
                            
            except Exception as e:
                print(f"⚠ Could not check {name}: {e}")
    
    return updates_available

def create_updated_requirements(updates):
    """Create a new requirements file with suggested updates."""
    print("\n" + "="*60)
    print("CREATING requirements.updated.txt")
    print("="*60 + "\n")
    
    with open("requirements.txt", "r") as f:
        lines = f.readlines()
    
    updates_dict = {name: latest for name, _, latest in updates}
    
    updated_lines = []
    for line in lines:
        if "==" in line:
            name = line.split("==")[0].strip()
            if name in updates_dict:
                updated_lines.append(f"{name}=={updates_dict[name]}\n")
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)
    
    with open("requirements.updated.txt", "w") as f:
        f.writelines(updated_lines)
    
    print("✓ Created requirements.updated.txt with latest versions")

def main():
    print("\n🔍 Python Package CVE Checker for DeepHunter\n")
    
    # Step 1: Install pip-audit
    install_pip_audit()
    
    # Step 2: Scan for vulnerabilities
    vulns = run_vulnerability_scan()
    
    # Step 3: Check for updates
    updates = check_latest_versions()
    
    # Step 4: Create updated requirements
    if updates:
        create_updated_requirements(updates)
        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60)
        print("""
1. Review requirements.updated.txt
2. Test in a separate virtual environment:
   python -m venv test_env
   test_env\\Scripts\\activate  (Windows)
   pip install -r requirements.updated.txt
   python manage.py test

3. If tests pass, backup and update:
   copy requirements.txt requirements.backup.txt
   copy requirements.updated.txt requirements.txt

4. Run vulnerability scan again to confirm fixes
""")
    else:
        print("\n✓ All packages are up to date!")

if __name__ == "__main__":
    main()
