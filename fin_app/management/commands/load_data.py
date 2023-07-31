from django.core.management.base import BaseCommand
from fin_app.models import Company
import pandas as pd

class Command(BaseCommand):
    help = 'Load data from CSV file into Database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']
        df = pd.read_csv(csv_file_path)
        for index, row in df.iterrows():
            Company.objects.create(ticker=row['ticker'], short_name=row['short name'])

        self.stdout.write(self.style.SUCCESS('Company data imported successfully'))