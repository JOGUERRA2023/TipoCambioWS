from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import requests
import json

# Configuración de Selenium con Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # Oculta la ventana del navegador
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Especifica la ruta a tu ChromeDriver
chrome_driver_path = "C:\\Windows\\System32\\chromedriver.exe"

# Inicializar el navegador
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Lista de endpoints a los que enviar los datos
endpoints = [
    "https://code.com/11111111111/api/tipocambio/2268"
    # Agrega más endpoints si es necesario
]
id_empresas=[
    "11111111111",
    ]

# Endpoint de autenticación
auth_endpoint = "https://code.com.com/api/acceso/sesion"
auth_credentials = {
    "username": "admin",
    "password": "123",
    "codigo":"000000"
}

# Función para obtener el token
def obtener_token(auth_endpoint, credentials):
    try:
        response = requests.post(auth_endpoint, json=credentials,verify=False)
        if response.status_code == 200:
            token = response.json().get("tokenDeAcceso")  # Suponiendo que la respuesta es {"token": "valor"}
            if token:
                return token
            else:
                print("Error: No se encontró el token en la respuesta.")
                return None
        else:
            print(f"Error en la autenticación: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error al conectar con el endpoint de autenticación: {str(e)}")
        return None

# Obtener el token
token = obtener_token(auth_endpoint, auth_credentials)

if not token:
    print("No se pudo obtener el token. Verifica las credenciales y el endpoint de autenticación.")
    driver.quit()
    exit()

try:
    # Abrir la página de SUNAT
    driver.get("https://e-consulta.sunat.gob.pe/cl-at-ittipcam/tcS01Alias")
    
    # Esperar a que la página cargue completamente
    time.sleep(10)

    # Localizar la tabla que contiene los valores del tipo de cambio
    tabla = driver.find_element(By.CLASS_NAME, "calendar-table")

    # Extraer las filas de la tabla
    filas = tabla.find_elements(By.TAG_NAME, "tr")

    # Variables para almacenar los últimos valores de compra y venta
    ultimo_compra = None
    ultimo_venta = None

    # Recorrer las filas para encontrar los valores de compra y venta
    for fila in filas:
        celdas = fila.find_elements(By.TAG_NAME, "td")
        for celda in celdas:
            # Buscar los elementos que contienen los valores de compra y venta
            eventos = celda.find_elements(By.CLASS_NAME, "event")
            for evento in eventos:
                if "Tipo de Cambio" in evento.get_attribute("title"):
                    texto = evento.text
                    if "Compra" in texto:
                        ultimo_compra = texto.split()[-1]  # Actualizar el último valor de compra
                    elif "Venta" in texto:
                        ultimo_venta = texto.split()[-1]  # Actualizar el último valor de venta

    # Imprimir los últimos valores de compra y venta
    if ultimo_compra and ultimo_venta:
        print(f"Último Tipo de Cambio Compra: {ultimo_compra}")
        print(f"Último Tipo de Cambio Venta: {ultimo_venta}")

        # Crear el cuerpo de la solicitud
        body = {
            "compra": float(ultimo_compra),
            "venta": float(ultimo_venta)
        }

        # Enviar los datos a cada endpoint
        
        for endpoint, id_empresa in zip(endpoints, id_empresas):
            try:
                headers = {
                    "Authorization": f"Bearer {token}",
                     "id_empresa": id_empresa,# Agregar el parámetro en los headers
                    "Accept": "application/json"
                    }  # Incluir el token en los headers
                response = requests.put(endpoint, json=body, headers=headers,verify=False)
                if response.status_code == 200:
                    respuesta = response.json()
                    if respuesta.get("id") == 0:
                        print(f"Operación exitosa para {endpoint}")
                    else:
                        print(f"Error en {endpoint}: La actualización no se realizó. Respuesta: {respuesta}")
                else:
                    print(f"Error en el endpoint {endpoint}: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Error al conectar con el endpoint {endpoint}: {str(e)}")
    else:
        print("No se encontraron valores de compra o venta.")

finally:
    # Cerrar el navegador
    driver.quit()