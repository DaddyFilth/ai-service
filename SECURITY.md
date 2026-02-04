# Security Policy

## Supported Versions

This project follows security best practices for credential management and authentication.

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| dev     | :white_check_mark: |

## Security Features

### Password Security
- **Automatic Password Validation**: All passwords are validated for strength at startup
- **Minimum Requirements**: 12 characters minimum length
- **Weak Pattern Detection**: Rejects common weak patterns (e.g., "password", "admin", "123456", "CHANGE_THIS")
- **Auto-Generation**: Setup script generates cryptographically secure passwords using Python's `secrets` module
- **Environment-Based**: Passwords stored in `.env` file (never in code or version control)
- **Config File Protection**: Generated Asterisk configs use placeholders, never actual passwords

### Configuration Security
- **File Permissions**: `.env` file automatically set to 600 (owner-only read/write)
- **Gitignore Protection**: `.env` file excluded from version control
- **Placeholder System**: Generated config files require manual password entry
- **Clear Warnings**: Prominent security warnings when passwords not configured

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please follow these steps:

1. **Do NOT** open a public issue
2. Email the maintainers directly with details
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

### Response Timeline
- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Critical issues within 14 days, others within 30 days

### What to Expect
- Acknowledgment of your report
- Regular updates on fix progress
- Credit in release notes (if desired)
- Notification when fix is released

## Security Best Practices

When deploying this service:

1. **Always use strong passwords**
   - Run setup.sh to auto-generate secure passwords
   - Or generate manually: `python3 -c 'import secrets; print(secrets.token_hex(24))'`

2. **Protect your .env file**
   - Never commit to version control
   - Set permissions to 600: `chmod 600 .env`
   - Backup securely with encryption

3. **Network Security**
   - Use firewall rules to restrict port access
   - Consider TLS/SSL for production
   - Limit ARI port (8088) access to trusted networks

4. **Regular Updates**
   - Keep Asterisk updated for security patches
   - Update Python dependencies regularly
   - Monitor security advisories

5. **Monitoring**
   - Review Asterisk logs regularly
   - Monitor for unauthorized access attempts
   - Set up alerts for suspicious activity

6. **Rate Limiting** (recommended for production)
   - Implement rate limiting on authentication endpoints to prevent brute force attacks
   - Consider using middleware like `aiohttp-ratelimit` or reverse proxy rate limiting
   - Recommended limits:
     - `/auth/login`: 5 requests per minute per IP
     - `/auth/register`: 3 requests per hour per IP
     - `/call/incoming`: 60 requests per minute per user

7. **CORS Configuration** (if serving web clients)
   - Configure CORS headers appropriately for your use case
   - Never use wildcard (`*`) for origins, headers, or exposed headers in production
   - Specify exact allowed origins and headers
   - Use `aiohttp-cors` middleware for proper CORS support
   - Example configuration:
     ```python
     import aiohttp_cors
     
     cors = aiohttp_cors.setup(app, defaults={
         "https://yourdomain.com": aiohttp_cors.ResourceOptions(
             allow_credentials=True,
             expose_headers=["Content-Type", "Authorization"],
             allow_headers=["Content-Type", "Authorization"],
             allow_methods=["GET", "POST", "PUT", "DELETE"]
         )
     })
     
     # Apply CORS to routes
     for route in list(app.router.routes()):
         cors.add(route)
     ```

## Known Security Considerations

- **Development Mode**: Empty passwords allowed for development/testing only
- **Generated Configs**: Must manually update with actual passwords before production
- **Log Files**: Ensure log files don't contain sensitive information
- **Asterisk Security**: Follow Asterisk security best practices for production deployments
- **Input Validation**: All user inputs are validated and sanitized to prevent injection attacks
- **Path Traversal Protection**: File paths are sanitized to prevent directory traversal attacks
- **API Query Parameters**: Validated with proper error handling to prevent crashes
