# ArpanCart — First Working Version

A self-contained ArpanCart starter with a working customer storefront, cart/checkout demo, admin dashboard, service-menu database, CSV import/export, JSON database and backups.

## Run

Requires Python 3.9+.

```bash
python3 server.py
```

Open http://localhost:8080

## Structure

- `server.py` — API + local web server
- `db/database.json` — development database
- `backups/` — generated database backups
- `public/index.html` — storefront shell
- `public/style.css` — responsive UI
- `public/app.js` — storefront/admin logic
- `uploads/` — reserved for product assets

## CSV import

Service Menu Database accepts:

```csv
name,category,price,active
Puja Booking,Religious Services,999,true
Monthly Puja Pack,Monthly Services,1511,true
```

## Production upgrade path

Replace the JSON database with PostgreSQL, add real authentication/roles, Razorpay/UPI payment verification, cloud image storage, delivery integrations, email/SMS/WhatsApp notifications, rate limiting, audit logs and HTTPS deployment.
