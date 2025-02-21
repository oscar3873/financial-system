import sys
import os
import django

# Ruta que deseas agregar
ruta = "/home/ovsoft/financial-system/financialsystem/"

if ruta not in sys.path:
    sys.path.append(ruta)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "financialsystem.settings")
django.setup()


from adviser.models import Adviser
from clients.models import Client, PhoneNumberClient
from credit.models import Credit
from cashregister.models import CashRegister, Movement
from guarantor.models import Guarantor
from credit.utils import refresh_condition
import os
import logging
import traceback
from datetime import datetime

# Crear una carpeta para los logs
log_directory = "./daily_update_logs"
os.makedirs(log_directory, exist_ok=True)

# Generar el nombre del archivo con un timestamp
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"{log_directory}/daily_update_log_{timestamp}.log"

logging.basicConfig(
    filename=log_filename,  # Cambia esto por el nombre de tu archivo de log
    filemode='a',
    level=logging.INFO,  # Nivel para registrar errores
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Función para limpiar registros antiguos si exceden 32 archivos
def clean_old_logs(directory, max_files):
    log_files = sorted(
        [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".log")],
        key=os.path.getmtime  # Ordenar por fecha de modificación
    )
    while len(log_files) > max_files:
        oldest_file = log_files.pop(0)  # Eliminar el archivo más antiguo
        os.remove(oldest_file)
        logging.info(f"Archivo eliminado: {oldest_file}")

if __name__ == "__main__":
    logging.info("Daily update start")
    try:
        refresh_condition()
    except Exception as e:
        # Registrar la excepción con el traceback completo
        logging.error(e)
        logging.error("Se produjo una excepción al ejecutar refresh_condition:")
        logging.error(traceback.format_exc())
    clean_old_logs(log_directory, 32)
    logging.info("Daily update end")