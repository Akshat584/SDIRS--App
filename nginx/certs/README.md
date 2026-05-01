# Nginx Certificates Directory

Place your SSL certificates here:
- `fullchain.pem`
- `privkey.pem`

For development, you can generate a self-signed certificate:
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout privkey.pem -out fullchain.pem
```
