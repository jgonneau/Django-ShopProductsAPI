from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction

from api.user.models import User, Role
from api.store.models import Store
from api.product.models import Product
from api.order.models import Order, OrderStatus
from api.invoice.models import Invoice, InvoiceStatus


class Command(BaseCommand):
    help = 'Seed database with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Order.objects.all().delete()
            Invoice.objects.all().delete()
            Product.objects.all().delete()
            Store.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            User.objects.filter(is_superuser=True).delete()
            self.stdout.write(self.style.WARNING('Existing data cleared'))

        self.stdout.write('Seeding database...')

        # Create 2 admins
        admin1 = User.objects.create_superuser(
            email='admin@shop.com',
            password='admin123',
            username='admin1',
            role=Role.ADMIN
        )
        admin2 = User.objects.create_superuser(
            email='superadmin@shop.com',
            password='admin123',
            username='admin2',
            role=Role.ADMIN
        )
        self.stdout.write(self.style.SUCCESS('Created 2 admins'))

        # Create 5 regular users (2 vendors, 3 customers)
        vendor1 = User.objects.create_user(
            email='vendor1@shop.com',
            password='vendor123',
            username='vendor1',
            role=Role.VENDOR
        )
        vendor2 = User.objects.create_user(
            email='vendor2@shop.com',
            password='vendor123',
            username='vendor2',
            role=Role.VENDOR
        )
        customer1 = User.objects.create_user(
            email='customer1@shop.com',
            password='customer123',
            username='customer1',
            role=Role.CUSTOMER
        )
        customer2 = User.objects.create_user(
            email='customer2@shop.com',
            password='customer123',
            username='customer2',
            role=Role.CUSTOMER
        )
        customer3 = User.objects.create_user(
            email='customer3@shop.com',
            password='customer123',
            username='customer3',
            role=Role.CUSTOMER
        )
        self.stdout.write(self.style.SUCCESS('Created 5 users (2 vendors, 3 customers)'))

        # Create 2 stores
        store1 = Store.objects.create(
            name='Electronics Hub',
            description='Best electronics and gadgets',
            phone='+1-555-0101',
            address='123 Tech Street',
            city='San Francisco',
            state='CA',
            zip_code='94102',
            country='USA',
            owner=vendor1
        )
        store2 = Store.objects.create(
            name='Fashion World',
            description='Trendy clothes and accessories',
            phone='+1-555-0102',
            address='456 Style Avenue',
            city='New York',
            state='NY',
            zip_code='10001',
            country='USA',
            owner=vendor2
        )
        self.stdout.write(self.style.SUCCESS('Created 2 stores'))

        # Create 20 products (10 per store)
        products_store1 = []
        electronics = [
            ('Smartphone Pro', 'Latest smartphone with advanced features'),
            ('Laptop Elite', 'High-performance laptop for professionals'),
            ('Wireless Earbuds', 'Premium sound quality earbuds'),
            ('Smart Watch', 'Fitness and health tracking smartwatch'),
            ('Tablet Max', '12-inch tablet with stylus support'),
            ('Gaming Console', 'Next-gen gaming experience'),
            ('Bluetooth Speaker', 'Portable speaker with deep bass'),
            ('USB-C Hub', '7-in-1 USB-C hub for connectivity'),
            ('Webcam HD', '4K webcam for streaming and calls'),
            ('Mechanical Keyboard', 'RGB mechanical keyboard for gaming'),
        ]
        for i, (title, desc) in enumerate(electronics, 1):
            product = Product.objects.create(
                reference=f'ELEC-{i:03d}',
                title=title,
                description=desc,
                price=Decimal(f'{50 + i * 50}.99'),
                stock_quantity=100 - i * 5,
                activated=True,
                store=store1
            )
            products_store1.append(product)

        products_store2 = []
        fashion = [
            ('Classic T-Shirt', 'Comfortable cotton t-shirt'),
            ('Slim Fit Jeans', 'Modern slim fit denim jeans'),
            ('Leather Jacket', 'Premium leather jacket'),
            ('Running Shoes', 'Lightweight running shoes'),
            ('Casual Hoodie', 'Soft fleece hoodie'),
            ('Formal Shirt', 'Business casual formal shirt'),
            ('Summer Dress', 'Floral print summer dress'),
            ('Sports Cap', 'Adjustable sports cap'),
            ('Canvas Backpack', 'Durable canvas backpack'),
            ('Wool Scarf', 'Warm wool scarf for winter'),
        ]
        for i, (title, desc) in enumerate(fashion, 1):
            product = Product.objects.create(
                reference=f'FASH-{i:03d}',
                title=title,
                description=desc,
                price=Decimal(f'{20 + i * 15}.99'),
                stock_quantity=50 + i * 5,
                activated=True,
                store=store2
            )
            products_store2.append(product)
        self.stdout.write(self.style.SUCCESS('Created 20 products'))

        # Create 2 invoices
        invoice1 = Invoice.objects.create(
            reference='INV-001',
            content={
                'items': [
                    {'name': products_store1[0].title, 'qty': 1, 'price': str(products_store1[0].price)},
                    {'name': products_store1[1].title, 'qty': 1, 'price': str(products_store1[1].price)},
                ]
            },
            total=products_store1[0].price + products_store1[1].price,
            status=InvoiceStatus.PAID,
            customer=customer1,
            store=store1
        )
        invoice2 = Invoice.objects.create(
            reference='INV-002',
            content={
                'items': [
                    {'name': products_store2[0].title, 'qty': 2, 'price': str(products_store2[0].price)},
                    {'name': products_store2[2].title, 'qty': 1, 'price': str(products_store2[2].price)},
                ]
            },
            total=(products_store2[0].price * 2) + products_store2[2].price,
            status=InvoiceStatus.PENDING,
            customer=customer2,
            store=store2
        )
        self.stdout.write(self.style.SUCCESS('Created 2 invoices'))

        # Create 2 orders
        order1 = Order.objects.create(
            reference='ORD-001',
            content={'notes': 'Please deliver ASAP', 'shipping': 'express'},
            total=products_store1[0].price + products_store1[1].price,
            status=OrderStatus.DELIVERED,
            customer=customer1,
            store=store1,
            invoice=invoice1
        )
        order1.products.add(products_store1[0], products_store1[1])

        order2 = Order.objects.create(
            reference='ORD-002',
            content={'notes': 'Gift wrap please', 'shipping': 'standard'},
            total=(products_store2[0].price * 2) + products_store2[2].price,
            status=OrderStatus.PROCESSING,
            customer=customer2,
            store=store2,
            invoice=invoice2
        )
        order2.products.add(products_store2[0], products_store2[2])
        self.stdout.write(self.style.SUCCESS('Created 2 orders'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write('')
        self.stdout.write('Login credentials:')
        self.stdout.write(self.style.WARNING('  Admins:'))
        self.stdout.write('    - admin@shop.com (password: admin123)')
        self.stdout.write('    - superadmin@shop.com (password: admin123)')
        self.stdout.write(self.style.WARNING('  Vendors:'))
        self.stdout.write('    - vendor1@shop.com (password: vendor123)')
        self.stdout.write('    - vendor2@shop.com (password: vendor123)')
        self.stdout.write(self.style.WARNING('  Customers:'))
        self.stdout.write('    - customer1@shop.com (password: customer123)')
        self.stdout.write('    - customer2@shop.com (password: customer123)')
        self.stdout.write('    - customer3@shop.com (password: customer123)')
        self.stdout.write('')
