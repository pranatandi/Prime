# Prime — Sistem CRM & ERP Dasar

Aplikasi CRM multi-tenant berbasis Django, dengan modul ERP dasar (Accounting,
Tax, Invoicing, Budget, Payroll, Purchasing).

## Fitur

- **Multi-tenant**: setiap perusahaan (tenant) mendaftar sendiri dan datanya
  terisolasi penuh dari tenant lain.
- **CRM**: Companies, Contacts, Sales Pipeline (Kanban drag-and-drop), Deals,
  Tasks & Activities.
- **Dashboard**: funnel pipeline, revenue & expense bulan berjalan, task jatuh
  tempo.
- **Finance**: Chart of Accounts, Journal Entries (double-entry), Tax Rates,
  Invoices (dengan line items), Budgets.
- **Payroll**: data karyawan, payroll run, generate payslip.
- **Purchasing**: vendor & purchase order dengan line items.
- **Role-based access**: ADMIN, SALES, FINANCE, HR, STAFF.

## Menjalankan secara lokal

```bash
pip install -r requirements.txt
cp .env.example .env      # opsional, default sudah pakai SQLite
python manage.py migrate
python manage.py seed_demo   # opsional: buat 2 tenant contoh dengan data demo
python manage.py runserver
```

Buka http://127.0.0.1:8000/signup/ untuk mendaftarkan perusahaan baru, atau
login dengan akun demo (jika `seed_demo` dijalankan):

- `admin_acme` / `demo12345`
- `admin_nusantara` / `demo12345`

## Menjalankan test

```bash
python manage.py test
```

## Konfigurasi database

Default memakai SQLite (`db.sqlite3`, tidak perlu setup apa pun). Untuk
Postgres, set `DATABASE_URL` di `.env`, misalnya:

```
DATABASE_URL=postgres://user:password@localhost:5432/prime_crm
```

## Struktur proyek

- `config/` — pengaturan Django (settings, urls)
- `core/` — model `Tenant`, mixin tenant-scoping, template & view generik
- `accounts/` — user, signup, login, manajemen pengguna
- `crm/` — Companies, Contacts, Pipeline, Deals, Activities
- `dashboard/` — halaman ringkasan
- `finance/` — Chart of Accounts, Journal Entries, Tax, Invoice, Budget
- `payroll/` — Employee, Payroll Run, Payslip
- `purchasing/` — Vendor, Purchase Order
