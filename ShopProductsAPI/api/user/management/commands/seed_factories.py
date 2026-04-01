from django.core.management.base import BaseCommand
from django.db import transaction

from api.user.tests.factories import UserFactory, AdminFactory
from api.store.tests.factories import StoreFactory
from api.product.tests.factories import ProductFactory


class Command(BaseCommand):
    help = 'Seed database using factory_boy factories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=1,
            help='Number of regular users to create (default: 1)',
        )
        parser.add_argument(
            '--admins',
            type=int,
            default=1,
            help='Number of admin users to create (default: 1)',
        )
        parser.add_argument(
            '--stores',
            type=int,
            default=1,
            help='Number of stores to create (default: 1)',
        )
        parser.add_argument(
            '--products',
            type=int,
            default=5,
            help='Number of products to create (default: 5)',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Seeding database with factories...')

        # Create users
        users = UserFactory.create_batch(options['users'])
        self.stdout.write(self.style.SUCCESS(f'Created {len(users)} user(s)'))
        for user in users:
            self.stdout.write(f'  - {user.email}')

        # Create admins
        admins = AdminFactory.create_batch(options['admins'])
        self.stdout.write(self.style.SUCCESS(f'Created {len(admins)} admin(s)'))
        for admin in admins:
            self.stdout.write(f'  - {admin.email}')

        # Create stores (auto-creates vendor owner)
        stores = StoreFactory.create_batch(options['stores'])
        self.stdout.write(self.style.SUCCESS(f'Created {len(stores)} store(s)'))
        for store in stores:
            self.stdout.write(f'  - {store.name} (owner: {store.owner.email})')

        # Create products (uses existing stores if available)
        if stores:
            products = []
            for store in stores:
                store_products = ProductFactory.create_batch(
                    options['products'] // len(stores) or 1,
                    store=store
                )
                products.extend(store_products)
        else:
            products = ProductFactory.create_batch(options['products'])

        self.stdout.write(self.style.SUCCESS(f'Created {len(products)} product(s)'))
        for product in products:
            self.stdout.write(f'  - {product.title} @ {product.store.name} (${product.price})')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('Database seeded successfully with factories!'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
