import os
import random
from faker import Faker

# Configura Django antes de importar los modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financialsystem.settings')
import django
django.setup()

from faker import Faker
from adviser.models import Adviser
from clients.models import Client, PhoneNumberClient
from credit.models import Credit
from cashregister.models import CashRegister, Movement


fake = Faker()

def create_fake_clients_and_phone_numbers(num_records):
    advisers = Adviser.objects.all()
    cash_registers = CashRegister.objects.all()

    for _ in range(num_records):
        adviser = fake.random_element(advisers)
        cash_register = fake.random_element(cash_registers)

        client = Client.objects.create(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            adviser=adviser,
            email=fake.email(),
            civil_status=fake.random_element(Client.CivilStatus)[0],
            dni=fake.random_number(digits=8),
            profession=fake.job().replace(',', ' '),
            address=fake.address().replace(',', ' '),
            score=fake.random_int(min=0, max=1500),
            job_address=fake.address().replace(',', ' '),
        )
        print(f"Client {client.pk} created")
        PhoneNumberClient.objects.create(
            phone_number_c=fake.phone_number(),
            phone_type_c=fake.random_element(PhoneNumberClient.PHONETYPE)[0],
            client=client,
        )
        
        credit = Credit.objects.create(
            interest=40,
            amount=fake.pydecimal(left_digits=5, right_digits=2, positive=True),
            installment_num=fake.random_int(min=1, max=12),
            start_date=fake.date_time_this_year(),
            client=client,
        )
        
        movement = Movement.objects.create(
            amount=credit.amount,
            description=fake.text(max_nb_chars=500),
            money_type=fake.random_element(Movement.MONEY_TYPE)[0],
            cashregister=cash_register,
            user=adviser,
            operation_mode=Movement.OPERATION_CHOISE[1][0],
        )
        print(f"Movement {movement.pk} created")
        credit.mov=movement;
        credit.save()

        print(f"Credit {credit.pk} created")
if __name__ == '__main__':
    num_records = 1000  # Establece el número de registros que deseas crear
    create_fake_clients_and_phone_numbers(num_records)
