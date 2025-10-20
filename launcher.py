import subprocess
import os
import sys

# Obtener ruta absoluta del ejecutable (ya instalado o desde dist/)
base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))

# Ruta original al app.py (fuera del entorno empaquetado)
script_path = os.path.join(os.path.dirname(__file__), 'app.py')

# Ejecutar app.py con Streamlit desde ruta absoluta
subprocess.run(["streamlit", "run", script_path])
