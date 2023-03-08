# Financial System

Financial System es un sistema de manejo de créditos respaldados por garantes y empeños a clientes, que también cuenta con un sistema de caja para manejar ingresos y egresos dentro de la empresa. El sistema permite pagar los créditos, refinanciarlos y hacer pagos parciales, totales o mínimos. Además, tiene una aplicación de notas internas para los asesores.

## Aplicaciones

El sistema de Django está dividido en las siguientes aplicaciones:

- Core: contiene la configuración general del proyecto.
- Adviser: permite la gestión de los asesores y sus notas internas.
- Cashregister: permite la gestión de la caja de la empresa.
- Client: permite la gestión de los clientes.
- Credit: permite la gestión de los créditos y sus pagos.
- Guarantor: permite la gestión de los garantes.
- Warranty: permite la gestión de los empeños.
- Payment: permite la gestión de los pagos.
- Registration: permite la gestión de los registros.

## Requerimientos

El sistema de Django requiere las siguientes dependencias:

- asgiref==3.6.0
- astroid==2.13.3
- Babel==2.11.0
- colorama==0.4.6
- crispy-bootstrap5==0.7
- dill==0.3.6
- Django==4.1.5
- django-bootstrap-datepicker-plus==5.0.3
- django-braces==1.15.0
- django-ckeditor==6.5.1
- django-crispy-forms==1.14.0
- django-filter==22.1
- django-fontawesome-6==1.0.0.0
- django-js-asset==2.0.0
- django-material-icons==0.1.2
- django-money==3.0.0
- django-moneyfield==0.2.1
- django-tables2==2.5.1
- django-widget-tweaks==1.4.12
- fontawesome==5.10.1.post1
- fontawesome-free==5.15.4
- fontawesomefree==6.2.1
- isort==5.12.0
- lazy-object-proxy==1.9.0
- mccabe==0.7.0
- money==1.3.0
- Pillow==9.4.0
- platformdirs==2.6.2
- psycopg2==2.9.5
- py-moneyed==2.0
- pycodestyle==2.10.0
- pydantic==1.10.5
- pylint==2.15.10
- pylint-celery==0.3
- pylint-django==2.5.3
- pylint-plugin-utils==0.7
- python-dateutil==2.8.2
- pytz==2022.7.1
- six==1.16.0
- sqlparse==0.4.3
- tomli==2.0.1
- tomlkit==0.11.6
- typing_extensions==4.4.0
- tzdata==2022.7
- wrapt==1.14.1

## Installation

To get started with the Financial-System, follow these steps:

- Clone this repository to your local machine
- Create a virtual environment for the project and activate it
- Install the requirements using pip install -r requirements.txt
- Run migrations using python manage.py migrate
- Create a superuser using python manage.py createsuperuser
- Run the development server using python manage.py runserver
- You should now be able to access the Financial-System at http://localhost:8000/.

## Contributions

Contributions to the Financial-System are always welcome