from django.core.management.base import BaseCommand
from django.db.migrations.loader import MigrationLoader

class Command(BaseCommand):
    help = 'Generates a migrations manifest with the latest migration for each app.'

    def handle(self, *app_labels, **options):
        # Generate a migrations manifest with latest migration on each app
        loader = MigrationLoader(None, ignore_no_migrations=True)
        apps = sorted(loader.migrated_apps)
        graph = loader.graph

        with open('latest_migrations.manifest', 'w') as f:
            for app_name in apps:
                leaf_nodes = graph.leaf_nodes(app_name)
                if len(leaf_nodes) != 1:
                    raise Exception('App {} has multiple leaf migrations!'.format(app_name))
                f.write('{}: {}\n'.format(app_name, leaf_nodes[0][1]))