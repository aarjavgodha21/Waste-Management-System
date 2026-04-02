"""
Django management command to seed the database with e-waste example data.

Usage:
    python manage.py seed_data
    python manage.py seed_data --flush   # wipe and re-seed
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random

from waste.models import (
    user_Registration,
    userType,
    collector_Registration,
    products,
    stock_his,
    category,
    locations,
    waste_pickup,
    CollectionHistory,
    Purchase,
    OrderUpdates,
    Comaplaints,
)


class Command(BaseCommand):
    help = "Seed the database with e-waste specific example data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all existing data before seeding.",
        )

    # ------------------------------------------------------------------
    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("Flushing existing data …")
            self._flush()

        self.stdout.write("Seeding database with e-waste data …")

        admin_user = self._create_admin()
        collector_user, collector_reg = self._create_collector()
        users = self._create_users()
        categories = self._create_categories()
        prods = self._create_products()
        locs = self._create_locations()
        self._create_pickups_and_collections(users, collector_reg, categories)
        self._create_orders(users, prods)
        self._create_complaints(users)

        self.stdout.write(self.style.SUCCESS("✅  E-waste seed data created successfully!"))
        self.stdout.write("")
        self.stdout.write("Login credentials:")
        self.stdout.write("  Admin     → admin@ewaste.com / admin123")
        self.stdout.write("  Collector → collector@ewaste.com / collector123")
        self.stdout.write("  User 1    → user1@ewaste.com / user123")
        self.stdout.write("  User 2    → user2@ewaste.com / user123")

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _flush(self):
        Comaplaints.objects.all().delete()
        OrderUpdates.objects.all().delete()
        Purchase.objects.all().delete()
        CollectionHistory.objects.all().delete()
        waste_pickup.objects.all().delete()
        locations.objects.all().delete()
        stock_his.objects.all().delete()
        products.objects.all().delete()
        category.objects.all().delete()
        collector_Registration.objects.all().delete()
        user_Registration.objects.all().delete()
        userType.objects.all().delete()
        User.objects.all().delete()

    # ---- users -------------------------------------------------------

    def _create_admin(self):
        if User.objects.filter(username="admin@ewaste.com").exists():
            self.stdout.write("  Admin already exists, skipping.")
            return User.objects.get(username="admin@ewaste.com")

        user = User.objects.create_superuser(
            username="admin@ewaste.com",
            email="admin@ewaste.com",
            password="admin123",
            first_name="Admin",
            last_name="1",
        )
        self.stdout.write("  Created admin user.")
        return user

    def _create_collector(self):
        if User.objects.filter(username="collector@ewaste.com").exists():
            self.stdout.write("  Collector already exists, skipping.")
            u = User.objects.get(username="collector@ewaste.com")
            return u, collector_Registration.objects.get(collector_id=u)

        user = User.objects.create_user(
            username="collector@ewaste.com",
            email="collector@ewaste.com",
            password="collector123",
            first_name="Raju Sharma",
            last_name="1",
        )
        reg = collector_Registration.objects.create(
            collector_id=user,
            name="Raju Sharma",
            email="collector@ewaste.com",
            mobile="9876543210",
            address="12, Green Park, Mumbai",
            password="collector123",
        )
        userType.objects.create(user=user, type="collector")
        self.stdout.write("  Created collector user.")
        return user, reg

    def _create_users(self):
        user_data = [
            {
                "email": "user1@ewaste.com",
                "name": "Aarav Patel",
                "mobile": "9123456780",
                "address": "45, Marine Drive, Mumbai",
                "pincode": "400001",
            },
            {
                "email": "user2@ewaste.com",
                "name": "Priya Desai",
                "mobile": "9234567891",
                "address": "78, Hill Road, Bandra",
                "pincode": "400002",
            },
        ]
        regs = []
        for d in user_data:
            if User.objects.filter(username=d["email"]).exists():
                self.stdout.write(f"  User {d['email']} already exists, skipping.")
                u = User.objects.get(username=d["email"])
                regs.append(user_Registration.objects.get(user=u))
                continue

            user = User.objects.create_user(
                username=d["email"],
                email=d["email"],
                password="user123",
                first_name=d["name"],
                last_name="1",  # verified
            )
            reg = user_Registration.objects.create(
                user=user,
                name=d["name"],
                email=d["email"],
                mobile=d["mobile"],
                address=d["address"],
                pincode=d["pincode"],
                password="user123",
                point=250,
            )
            userType.objects.create(user=user, type="user")
            regs.append(reg)
            self.stdout.write(f"  Created user {d['email']}.")
        return regs

    # ---- categories --------------------------------------------------

    def _create_categories(self):
        cat_data = [
            ("Circuit Boards", 15),
            ("Cables & Wires", 8),
            ("Batteries", 12),
            ("Displays & Screens", 20),
            ("Mobile Devices", 25),
            ("Computer Parts", 18),
        ]
        cats = []
        for name, point in cat_data:
            obj, created = category.objects.get_or_create(
                name=name, defaults={"point": point}
            )
            cats.append(obj)
            if created:
                self.stdout.write(f"  Created category: {name} ({point} pts/kg)")
        return cats

    # ---- products ----------------------------------------------------

    def _create_products(self):
        prod_data = [
            {
                "name": "Refurbished Wireless Mouse",
                "desc": "Ergonomic wireless mouse rebuilt from recycled e-waste components. 12-month warranty included.",
                "rate": 599,
                "point": 80,
                "stock": 20,
            },
            {
                "name": "Recycled PCB Coaster Set",
                "desc": "Set of 4 unique coasters handcrafted from reclaimed printed circuit boards. Each piece is one-of-a-kind.",
                "rate": 399,
                "point": 50,
                "stock": 30,
            },
            {
                "name": "Upcycled Circuit Board Clock",
                "desc": "Stunning wall clock made from decommissioned motherboard. Silent quartz movement. A perfect conversation piece.",
                "rate": 1299,
                "point": 150,
                "stock": 10,
            },
            {
                "name": "Refurbished USB-C Hub",
                "desc": "4-port USB-C hub remanufactured from recovered components. Supports data transfer and charging.",
                "rate": 899,
                "point": 120,
                "stock": 15,
            },
            {
                "name": "E-Waste Art Desk Lamp",
                "desc": "Unique desk lamp sculpted from discarded keyboard keys and circuit components. LED bulb included.",
                "rate": 1499,
                "point": 200,
                "stock": 8,
            },
            {
                "name": "Recycled Copper Wire Bracelet",
                "desc": "Artisan bracelet crafted from reclaimed copper wiring. Adjustable size, hypoallergenic finish.",
                "rate": 299,
                "point": 40,
                "stock": 25,
            },
        ]
        prods = []
        for d in prod_data:
            if products.objects.filter(name=d["name"]).exists():
                prods.append(products.objects.get(name=d["name"]))
                continue
            p = products.objects.create(
                name=d["name"],
                desc=d["desc"],
                rate=d["rate"],
                point=d["point"],
                status=1,
            )
            stock_his.objects.create(product=p, stock=d["stock"])
            prods.append(p)
            self.stdout.write(f"  Created product: {d['name']}")
        return prods

    # ---- locations ---------------------------------------------------

    def _create_locations(self):
        pincodes = ["400001", "400002", "400003", "400050", "400053"]
        locs = []
        for pc in pincodes:
            obj, created = locations.objects.get_or_create(pincode=pc)
            locs.append(obj)
            if created:
                self.stdout.write(f"  Created location pincode: {pc}")
        return locs

    # ---- pickups & collections ----------------------------------------

    def _create_pickups_and_collections(self, users, collector_reg, categories):
        now = timezone.now().date()
        for i, user_reg in enumerate(users):
            if waste_pickup.objects.filter(userid=user_reg).exists():
                continue

            # collected pickup (this month for admin dashboard stats)
            pickup = waste_pickup.objects.create(
                userid=user_reg,
                collector=collector_reg,
                status="collected",
                rdate=now - timedelta(days=5 + i * 3),
                pdate=now - timedelta(days=2 + i * 2),
            )
            # add collection records
            for cat in random.sample(list(categories), min(3, len(categories))):
                weight = round(random.uniform(0.5, 5.0), 1)
                point = int(weight * cat.point)
                CollectionHistory.objects.create(
                    pid=pickup,
                    category=cat,
                    weight=weight,
                    point=point,
                )

            # pending pickup
            waste_pickup.objects.create(
                userid=user_reg,
                status="requested",
                rdate=now - timedelta(days=1),
            )

            self.stdout.write(f"  Created e-waste pickup records for {user_reg.name}")

    # ---- orders -------------------------------------------------------

    def _create_orders(self, users, prods):
        if Purchase.objects.exists():
            self.stdout.write("  Orders already exist, skipping.")
            return

        now = timezone.now().date()
        statuses = ["Ordered", "Shipped", "Delivered"]

        for i, user_reg in enumerate(users):
            for j in range(2):
                prod = prods[(i + j) % len(prods)]
                qty = random.randint(1, 2)
                status = statuses[(i + j) % len(statuses)]
                pur = Purchase.objects.create(
                    user=user_reg,
                    product=prod,
                    mobile=user_reg.mobile,
                    address=user_reg.address,
                    pincode=user_reg.pincode,
                    quantity=str(qty),
                    type="P",
                    total=prod.rate * qty,
                    status=status,
                    date=now - timedelta(days=5 - j),
                )
                OrderUpdates.objects.create(
                    order=pur,
                    status="Ordered",
                    update="E-waste reward product ordered.",
                    date=now - timedelta(days=5 - j),
                )
                if status in ("Shipped", "Delivered"):
                    OrderUpdates.objects.create(
                        order=pur,
                        status="Shipped",
                        update="Package shipped via eco-courier.",
                        date=now - timedelta(days=3 - j),
                    )
                if status == "Delivered":
                    OrderUpdates.objects.create(
                        order=pur,
                        status="Delivered",
                        update="Package delivered successfully.",
                        date=now - timedelta(days=1),
                    )

        self.stdout.write("  Created sample e-waste reward orders.")

    # ---- complaints --------------------------------------------------

    def _create_complaints(self, users):
        if Comaplaints.objects.exists():
            self.stdout.write("  Complaints already exist, skipping.")
            return

        now = timezone.now().date()
        complaints_data = [
            {
                "subject": "Delayed E-Waste Pickup",
                "complaint": "My e-waste pickup request was not attended to for over a week. I have old motherboards and batteries ready for collection.",
                "status": "Solved",
                "sdate": now - timedelta(days=2),
            },
            {
                "subject": "Wrong Reward Product",
                "complaint": "I redeemed my points for the USB-C Hub but received a different item. Please arrange a replacement.",
                "status": "Pending",
                "sdate": None,
            },
            {
                "subject": "Recycling Points Not Credited",
                "complaint": "The collector picked up 3kg of circuit boards and 2kg of batteries but points were not added to my account.",
                "status": "Pending",
                "sdate": None,
            },
        ]

        for i, cd in enumerate(complaints_data):
            user_reg = users[i % len(users)]
            Comaplaints.objects.create(
                user=user_reg,
                subject=cd["subject"],
                complaint=cd["complaint"],
                rdate=now - timedelta(days=7 - i),
                sdate=cd["sdate"],
                status=cd["status"],
            )

        self.stdout.write("  Created sample e-waste complaints.")
