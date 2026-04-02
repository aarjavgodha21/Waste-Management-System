# Waste Management System

## Overview

This project is a Django + MySQL web application for e-waste and recyclable waste collection management.

It supports three roles:

- User: request pickup, earn points, purchase/redeem products, track order updates, and raise complaints.
- Collector: verify users, manage assigned pickup requests, and record collected waste.
- Admin: manage products, categories, collectors, locations, orders, complaints, and reports.

## Tech Stack

- Python 3.12
- Django 5.2
- MySQL 8.4
- mysqlclient

## Prerequisites (macOS)

Install these tools first:

```bash
brew install python@3.12 mysql@8.4 pkg-config
brew services start mysql@8.4
```

## Database Setup

Create the database once:

```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS db_wastemanagement CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

## Environment Variables

Project settings load values from `waste_management/.env`.

1. Copy example file:

```bash
cp waste_management/.env.example waste_management/.env
```

2. Edit `waste_management/.env` and set your MySQL password:

```env
DB_NAME=db_wastemanagement
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

`waste_management/.env` is ignored by Git, so secrets are not pushed.

## Run The Project (One Command)

From project root:

```bash
./run_project.command
```

This launcher will:

- create and activate `.venv` if missing,
- install dependencies (if missing),
- start MySQL service (best effort),
- run migrations,
- start Django development server.

Open:

`http://127.0.0.1:8000/`

## Manual Run (Alternative)

If you prefer running step-by-step:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
cd waste_management
python manage.py migrate
python manage.py runserver
```

## Main Routes

- Home: `/`
- Login: `/login`
- Register: `/UserRegister`
- Admin module: `/admin/`
- User module: `/user/`
- Collector module: `/collector/`

## Example Workflows

### Example 1: User Pickup And Rewards

1. Open `/UserRegister` and create a user account.
2. Login from `/login`.
3. Open `/user/PickupRequest` and submit a pickup request.
4. Login as collector and open `/collector/PickupRequest`.
5. Record collection from `/collector/Collection`.
6. Check user points from `/user/PointHistory`.

Expected result: pickup status is updated and reward points increase for the user.

### Example 2: Product Purchase Flow

1. Login as admin and add products from `/admin/addproduct`.
2. Login as user and browse `/user/Shop`.
3. Open a product from `/user/Product`.
4. Complete order from `/user/Checkout`.
5. Track order from `/user/OrderHistory` and `/user/OrderUpdates`.

Expected result: order appears in history with status updates.

### Example 3: Complaint Tracking

1. Login as user and submit complaint from `/user/ComplaintRegister`.
2. Login as admin and open `/admin/ViewComplaints`.
3. Mark complaint solved from `/admin/ComplaintSolved`.
4. Login as user and verify status at `/user/TrackComplaints`.

Expected result: complaint status changes from pending to solved.

## Useful Verification Commands

Run from project root:

```bash
# Check database tables using values from waste_management/.env
DB_USER=$(grep '^DB_USER=' waste_management/.env | cut -d= -f2-)
DB_NAME=$(grep '^DB_NAME=' waste_management/.env | cut -d= -f2-)
DB_PASS=$(grep '^DB_PASSWORD=' waste_management/.env | cut -d= -f2-)
mysql -u "$DB_USER" -p"$DB_PASS" -D "$DB_NAME" -e "SHOW TABLES;"

# Validate Django setup
source .venv/bin/activate
cd waste_management
python manage.py check
python manage.py migrate
```

## Troubleshooting

- `Access denied for user 'root'@'localhost'`:
  - Verify `DB_PASSWORD` in `waste_management/.env`.
  - Test MySQL login directly: `mysql -u root -p`.
- `mysqlclient` build errors:
  - Ensure `pkg-config` and MySQL are installed via Homebrew.
- MySQL service not running:
  - Run `brew services list` and `brew services start mysql@8.4`.

## License

This project is licensed under the MIT License.
