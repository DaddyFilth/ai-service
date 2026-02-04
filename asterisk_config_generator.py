#!/usr/bin/env python3
"""
Asterisk Configuration Generator for AI Call Service

This script generates Asterisk configuration files needed to integrate
the AI Call Service with Asterisk PBX.
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from config import settings


class AsteriskConfigGenerator:
    """Generate Asterisk configuration files for AI service integration."""
    
    def __init__(self, output_dir: str = "./asterisk-configs"):
        """
        Initialize the configuration generator.
        
        Args:
            output_dir: Directory to save generated configuration files
        """
        self.output_dir = Path(output_dir)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def generate_all(self):
        """Generate all required Asterisk configuration files."""
        print("=== Asterisk Configuration Generator ===")
        print(f"Output directory: {self.output_dir}")
        print("")
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate each configuration file
        self.generate_ari_conf()
        self.generate_http_conf()
        self.generate_extensions_conf()
        self.generate_pjsip_conf()
        self.generate_install_script()
        self.generate_readme()
        
        print("")
        print("=== Generation Complete ===")
        print(f"Configuration files saved to: {self.output_dir}")
        print("")
        print("Next steps:")
        print(f"1. Review the generated files in {self.output_dir}/")
        print(f"2. Run the install script: sudo bash {self.output_dir}/install_configs.sh")
        print("3. Restart Asterisk: sudo systemctl restart asterisk")
        
    def generate_ari_conf(self):
        """Generate ari.conf for Asterisk REST Interface."""
        # Security: Never use a default password in production
        # The password should be managed via environment variables only
        if not settings.asterisk_password:
            password_placeholder = '<YOUR_ASTERISK_PASSWORD_FROM_ENV>'
            password_warning = (
                "; !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n"
                "; SECURITY WARNING: No ASTERISK_PASSWORD set in .env file!\n"
                "; You MUST set a strong password in your .env file before\n"
                "; using this configuration in production.\n"
                "; \n"
                "; To generate a secure password, run:\n"
                ";   python3 -c 'import secrets; print(secrets.token_hex(24))'\n"
                "; \n"
                "; Then add it to your .env file:\n"
                ";   ASTERISK_PASSWORD=<generated_password>\n"
                "; !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n"
            )
        else:
            # Don't write the actual password to the config file
            # Instead use a placeholder that requires manual configuration
            password_placeholder = '<SET_FROM_ENV_ASTERISK_PASSWORD>'
            password_warning = (
                "; SECURITY NOTE: Password is configured in .env file.\n"
                "; Replace the placeholder below with the value from:\n"
                f";   ASTERISK_PASSWORD in your .env file\n"
                "; \n"
                "; NEVER commit the actual password to version control!\n"
            )
        
        content = f"""[general]
enabled = yes
pretty = yes

{password_warning}[{settings.asterisk_username}]
type = user
read_only = no
password = {password_placeholder}
"""
        self._write_file("ari.conf", content)
        print("✓ Generated ari.conf")
        if not settings.asterisk_password:
            print("  🔒 SECURITY WARNING: Set ASTERISK_PASSWORD in .env before production use!")
        else:
            print("  🔒 Password placeholder added - update manually with .env value")
        
    def generate_http_conf(self):
        """Generate http.conf for HTTP/WebSocket support."""
        content = """[general]
enabled = yes
bindaddr = 0.0.0.0
bindport = 8088
"""
        self._write_file("http.conf", content)
        print("✓ Generated http.conf")
        
    def generate_extensions_conf(self):
        """Generate extensions.conf with dialplan for AI service."""
        service_url = f"http://{settings.service_host}:{settings.service_port}"
        
        content = f""";
; AI Call Service Integration
; Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
; AI Service URL: {service_url}
;

[ai-service]
; Main AI call screening context
; This handles incoming calls through the AI service

; Generic incoming call handler
exten => _X.,1,NoOp(AI Call Screening - Starting)
    same => n,Set(CALL_ID=${{UNIQUEID}})
    same => n,Set(CALLER_NUM=${{CALLERID(num)}})
    same => n,Set(CALLED_NUM=${{EXTEN}})
    same => n,Answer()
    same => n,Wait(1)
    same => n,NoOp(Call ID: ${{CALL_ID}}, From: ${{CALLER_NUM}}, To: ${{CALLED_NUM}})
    same => n,Stasis(ai-service,${{CALL_ID}},${{CALLER_NUM}},${{CALLED_NUM}})
    same => n,Hangup()

; Specific extension examples
exten => 100,1,NoOp(AI Service - Extension 100)
    same => n,Goto(ai-service,100,1)

exten => 200,1,NoOp(AI Service - Extension 200)
    same => n,Goto(ai-service,200,1)

; Emergency bypass (direct dial without AI)
exten => 911,1,NoOp(Emergency - Bypass AI)
    same => n,Dial(SIP/emergency-trunk/911)
    same => n,Hangup()

[from-trunk]
; Handle calls from external SIP trunks
exten => _X.,1,NoOp(Incoming call from trunk)
    same => n,Goto(ai-service,${{EXTEN}},1)

[default]
; Default context - route to AI service
exten => _X.,1,NoOp(Default context - routing to AI)
    same => n,Goto(ai-service,${{EXTEN}},1)
"""
        self._write_file("extensions.conf", content)
        print("✓ Generated extensions.conf")
        
    def generate_pjsip_conf(self):
        """Generate pjsip.conf for SIP trunk configuration."""
        # Security: Never use a default password in production
        # The password should be managed via environment variables only
        if not settings.asterisk_password:
            password_placeholder = '<YOUR_ASTERISK_PASSWORD_FROM_ENV>'
            password_warning = (
                "; !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n"
                "; SECURITY WARNING: No ASTERISK_PASSWORD set in .env file!\n"
                "; You MUST set a strong password in your .env file before\n"
                "; using this configuration in production.\n"
                "; \n"
                "; To generate a secure password, run:\n"
                ";   python3 -c 'import secrets; print(secrets.token_hex(24))'\n"
                "; \n"
                "; Then add it to your .env file:\n"
                ";   ASTERISK_PASSWORD=<generated_password>\n"
                "; !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n"
            )
        else:
            # Don't write the actual password to the config file
            # Instead use a placeholder that requires manual configuration
            password_placeholder = '<SET_FROM_ENV_ASTERISK_PASSWORD>'
            password_warning = (
                "; SECURITY NOTE: Password is configured in .env file.\n"
                "; Replace the placeholder below with the value from:\n"
                f";   ASTERISK_PASSWORD in your .env file\n"
                "; \n"
                "; NEVER commit the actual password to version control!\n\n"
            )
        
        content = f""";
; PJSIP Configuration for AI Call Service
; Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
;
{password_warning}
[transport-udp]
type = transport
protocol = udp
bind = 0.0.0.0:{settings.asterisk_port}

[transport-tcp]
type = transport
protocol = tcp
bind = 0.0.0.0:{settings.asterisk_port}

; AI Service endpoint (for internal use)
[ai-service-endpoint]
type = endpoint
context = ai-service
disallow = all
allow = ulaw
allow = alaw
allow = g722
allow = opus
direct_media = no
trust_id_inbound = yes

[ai-service-aor]
type = aor
max_contacts = 1

[ai-service-auth]
type = auth
auth_type = userpass
username = {settings.asterisk_username}
password = {password_placeholder}

; Example SIP trunk configuration (customize for your provider)
; [trunk-example]
; type = endpoint
; context = from-trunk
; disallow = all
; allow = ulaw
; allow = alaw
; outbound_auth = trunk-example-auth
; aors = trunk-example-aor
; 
; [trunk-example-aor]
; type = aor
; contact = sip:your-provider.com
; 
; [trunk-example-auth]
; type = auth
; auth_type = userpass
; username = your-username
; password = your-password
"""
        self._write_file("pjsip.conf", content)
        print("✓ Generated pjsip.conf")
        if not settings.asterisk_password:
            print("  🔒 SECURITY WARNING: Set ASTERISK_PASSWORD in .env before production use!")
        else:
            print("  🔒 Password placeholder added - update manually with .env value")
        
    def generate_install_script(self):
        """Generate installation script for the configuration files."""
        content = f"""#!/bin/bash
#
# Asterisk Configuration Installation Script
# Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
#

set -e

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

echo "=== Asterisk Configuration Installer for AI Service ==="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "${{RED}}Error: This script must be run as root (use sudo)${{NC}}"
    exit 1
fi

# Check if Asterisk is installed
if ! command -v asterisk &> /dev/null; then
    echo "${{RED}}Error: Asterisk is not installed${{NC}}"
    echo "Install Asterisk first: sudo apt install asterisk"
    exit 1
fi

# Asterisk config directory
ASTERISK_DIR="/etc/asterisk"
BACKUP_DIR="/etc/asterisk/backup_{self.timestamp}"

# Create backup directory
echo "Creating backup directory: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Backup existing configuration files
echo ""
echo "Backing up existing configuration files..."
for file in ari.conf http.conf extensions.conf pjsip.conf; do
    if [ -f "$ASTERISK_DIR/$file" ]; then
        echo "  Backing up $file"
        cp "$ASTERISK_DIR/$file" "$BACKUP_DIR/$file"
    fi
done

# Install new configuration files
echo ""
echo "Installing new configuration files..."

# Function to install or merge configuration
install_config() {{
    local file=$1
    local source_file="$(dirname "$0")/$file"
    local dest_file="$ASTERISK_DIR/$file"
    
    if [ ! -f "$source_file" ]; then
        echo "${{YELLOW}}Warning: $source_file not found, skipping${{NC}}"
        return
    fi
    
    if [ -f "$dest_file" ]; then
        echo "  ${{YELLOW}}$file already exists${{NC}}"
        echo "    - Backup saved to: $BACKUP_DIR/$file"
        echo "    - New config saved to: $dest_file.ai-service"
        cp "$source_file" "$dest_file.ai-service"
        echo "    ${{YELLOW}}You need to manually merge $dest_file.ai-service into $dest_file${{NC}}"
    else
        echo "  Installing $file"
        cp "$source_file" "$dest_file"
    fi
}}

install_config "ari.conf"
install_config "http.conf"
install_config "extensions.conf"
install_config "pjsip.conf"

# Set proper permissions
echo ""
echo "Setting file permissions..."
chown -R asterisk:asterisk "$ASTERISK_DIR"
chmod 640 "$ASTERISK_DIR"/*.conf 2>/dev/null || true

# Verify configuration
echo ""
echo "Verifying Asterisk configuration..."
if asterisk -rx "core show version" &> /dev/null; then
    echo "${{GREEN}}✓ Asterisk is running${{NC}}"
    
    echo ""
    echo "Testing configuration syntax..."
    if asterisk -rx "dialplan reload" &> /dev/null; then
        echo "${{GREEN}}✓ Configuration syntax is valid${{NC}}"
    else
        echo "${{RED}}✗ Configuration has errors${{NC}}"
        echo "Check logs: tail -f /var/log/asterisk/full"
    fi
else
    echo "${{YELLOW}}Asterisk is not running - configuration will be validated on start${{NC}}"
fi

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Backups saved to: $BACKUP_DIR"
echo ""
echo "Next steps:"
echo "1. Review and merge any .ai-service files if needed"
echo "2. Edit $ASTERISK_DIR/pjsip.conf to add your SIP trunk(s)"
echo "3. Reload or restart Asterisk:"
echo "   sudo systemctl restart asterisk"
echo "   OR"
echo "   sudo asterisk -rx 'core reload'"
echo ""
echo "4. Start the AI service:"
echo "   cd {os.getcwd()}"
echo "   source venv/bin/activate"
echo "   python api.py"
echo ""
echo "5. Test the integration:"
echo "   asterisk -rvvv"
echo "   Then make a test call to your Asterisk server"
"""
        self._write_file("install_configs.sh", content, executable=True)
        print("✓ Generated install_configs.sh")
        
    def generate_readme(self):
        """Generate README with instructions."""
        content = f"""# Asterisk Configuration Files for AI Call Service

Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Overview

These configuration files integrate Asterisk PBX with the AI Call Service.

## Files Included

1. **ari.conf** - Asterisk REST Interface configuration
2. **http.conf** - HTTP/WebSocket server configuration  
3. **extensions.conf** - Dialplan for routing calls through AI service
4. **pjsip.conf** - SIP endpoint and trunk configuration
5. **install_configs.sh** - Automated installation script

## Quick Installation

```bash
# Review the generated files
ls -la {self.output_dir}/

# Install the configurations (requires root)
cd {self.output_dir}
sudo bash install_configs.sh
```

## Manual Installation

If you prefer to manually install:

1. Backup your existing Asterisk configuration:
   ```bash
   sudo cp -r /etc/asterisk /etc/asterisk.backup
   ```

2. Copy or merge the configuration files:
   ```bash
   sudo cp ari.conf /etc/asterisk/
   sudo cp http.conf /etc/asterisk/
   # For extensions.conf and pjsip.conf, merge with your existing config
   ```

3. Set proper permissions:
   ```bash
   sudo chown asterisk:asterisk /etc/asterisk/*.conf
   sudo chmod 640 /etc/asterisk/*.conf
   ```

4. Reload Asterisk:
   ```bash
   sudo systemctl restart asterisk
   # or
   sudo asterisk -rx 'core reload'
   ```

## Configuration Details

### ARI (Asterisk REST Interface)

- Enables the REST API for programmatic call control
- Username: {settings.asterisk_username}
- Password: Managed via ASTERISK_PASSWORD in .env file (never hardcoded in code; empty allowed for development only)
- Port: 8088 (HTTP)

### Dialplan (extensions.conf)

- Context `[ai-service]`: Routes calls through AI service
- Context `[from-trunk]`: Handles external calls
- Stasis application: `ai-service` - bridges to Python service

### SIP (pjsip.conf)

- Transport: UDP/TCP on port {settings.asterisk_port}
- Codecs: ulaw, alaw, g722, opus
- Authentication configured for AI service endpoint

## Testing the Integration

1. Start the AI service:
   ```bash
   cd {os.getcwd()}
   source venv/bin/activate
   python api.py
   ```

2. Connect to Asterisk CLI:
   ```bash
   sudo asterisk -rvvv
   ```

3. Make a test call to your Asterisk server

4. Check logs:
   ```bash
   # Asterisk logs
   sudo tail -f /var/log/asterisk/full
   
   # AI service logs
   # (shown in terminal where api.py is running)
   ```

## Customization

### Adding SIP Trunks

Edit `pjsip.conf` and add your provider details:

```ini
[your-trunk-name]
type = endpoint
context = from-trunk
aors = your-trunk-name-aor
outbound_auth = your-trunk-name-auth
; ... other settings

[your-trunk-name-aor]
type = aor
contact = sip:provider.com

[your-trunk-name-auth]
type = auth
auth_type = userpass
username = your-username
password = your-password
```

### Customizing Dialplan

Edit `extensions.conf` to modify call routing behavior:

- Add extensions for specific departments
- Implement time-based routing
- Add voicemail boxes
- Configure call forwarding rules

## Troubleshooting

### Asterisk won't start
```bash
# Check configuration syntax
sudo asterisk -c
# or
sudo asterisk -rx "core show settings"
```

### ARI connection issues
```bash
# Test ARI endpoint
curl http://localhost:8088/ari/api-docs/resources.json

# Check if HTTP server is enabled
sudo asterisk -rx "http show status"
```

### Calls not routing to AI service
```bash
# Verify dialplan
sudo asterisk -rx "dialplan show ai-service"

# Enable verbose logging
sudo asterisk -rx "core set verbose 5"
```

## Security Notes

⚠️ **CRITICAL Security Considerations:**

1. **Password Management:**
   - NEVER commit your .env file to version control (it's in .gitignore)
   - Use strong passwords (minimum 12 characters, generated via setup.sh)
   - Generated config files use placeholders - replace with actual .env values manually
   - Change default passwords in `ari.conf` and `pjsip.conf` before production

2. **Network Security:**
   - Use firewall rules to restrict access to port 8088 (ARI)
   - Consider using TLS for ARI connections in production
   - Restrict SIP port access to trusted networks only

3. **System Security:**
   - Regularly update Asterisk to get security patches
   - Set .env file permissions to 600 (owner-only): `chmod 600 .env`
   - Monitor Asterisk logs for suspicious activity

4. **Password Requirements:**
   - Minimum 12 characters
   - No common weak patterns (e.g., "password", "admin", "123456")
   - Auto-generated passwords meet these requirements

## Support

For issues with:
- **Asterisk configuration**: Check Asterisk documentation
- **AI Service integration**: See {os.getcwd()}/README.md
- **SIP/telephony**: Consult your SIP provider documentation

## Backup and Recovery

A backup was created during installation at:
`/etc/asterisk/backup_{self.timestamp}/`

To restore from backup:
```bash
sudo cp -r /etc/asterisk/backup_{self.timestamp}/* /etc/asterisk/
sudo systemctl restart asterisk
```
"""
        self._write_file("README.md", content)
        print("✓ Generated README.md")
        
    def _write_file(self, filename: str, content: str, executable: bool = False):
        """
        Write content to a file.
        
        Args:
            filename: Name of the file
            content: Content to write
            executable: Whether to make the file executable
        """
        filepath = self.output_dir / filename
        filepath.write_text(content)
        
        if executable:
            # Make file executable
            os.chmod(filepath, 0o755)


def main():
    """Main entry point for the configuration generator."""
    parser = argparse.ArgumentParser(
        description="Generate Asterisk configuration files for AI Call Service"
    )
    parser.add_argument(
        "-o", "--output",
        default="./asterisk-configs",
        help="Output directory for configuration files (default: ./asterisk-configs)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing output directory"
    )
    
    args = parser.parse_args()
    
    # Check if output directory exists
    output_path = Path(args.output)
    if output_path.exists() and not args.force:
        print(f"Error: Output directory {args.output} already exists")
        print("Use --force to overwrite or choose a different directory with -o")
        sys.exit(1)
    
    # Generate configurations
    generator = AsteriskConfigGenerator(args.output)
    generator.generate_all()


if __name__ == "__main__":
    main()
