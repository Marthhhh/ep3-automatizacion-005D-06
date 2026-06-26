#!/usr/bin/env python3
# fase4_validacion_restconf/validacion_restconf.py

import os
import sys
import datetime
import yaml
import requests
import json

# Deshabilitar advertencias de certificados SSL autofirmados (verify=False)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def cargar_variables():
    ruta_vars = "../vars/vars_005D-06.yaml"
    if not os.path.exists(ruta_vars):
        print(f"[-] Error: No se encuentra el archivo de variables en {ruta_vars}")
        sys.exit(1)
    with open(ruta_vars, 'r') as f:
        return yaml.safe_load(f)

def buscar_valor_en_json(estructura, valor_buscado):
    """Busca de forma recursiva si un valor existe dentro de un diccionario o lista JSON."""
    if estructura == valor_buscado:
        return True
    if isinstance(estructura, dict):
        for v in estructura.values():
            if buscar_valor_en_json(v, valor_buscado):
                return True
    elif isinstance(estructura, list):
        for item in estructura:
            if buscar_valor_en_json(item, valor_buscado):
                return True
    return False

def main():
    # Imprimir metadatos obligatorios por rúbrica
    print("=== METADATOS DE EJECUCIÓN RESTCONF ===")
    print(f"Script: {os.path.basename(__file__)}")
    print(f"Fecha/Hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Host VM: {os.uname()[1]}")
    print("======================================\n")

    data = cargar_variables()
    
    # Configuración base para RESTCONF
    base_url = f"https://{data['router']['ip']}/restconf/data"
    headers = {
        "Accept": "application/yang-data+json",
        "Content-Type": "application/yang-data+json"
    }
    auth = (data['router']['usuario'], data['router']['password'])

    # Crear la estructura de subcarpetas interna exigida
    os.makedirs("evidencias/responses", exist_ok=True)

    # Definición de los 4 Endpoints obligatorios
    endpoints = {
        "hostname": {
            "url": f"{base_url}/Cisco-IOS-XE-native:native/hostname",
            "file": "evidencias/responses/get_hostname.json"
        },
        "loopback": {
            "url": f"{base_url}/ietf-interfaces:interfaces/interface=Loopback{data['router']['loopback_id']}",
            "file": "evidencias/responses/get_loopback.json"
        },
        "interfaces": {
            "url": f"{base_url}/ietf-interfaces:interfaces/interface=GigabitEthernet1",
            "file": "evidencias/responses/get_interfaces.json"
        },
        "ntp": {
            "url": f"{base_url}/Cisco-IOS-XE-native:native/ntp",
            "file": "evidencias/responses/get_ntp.json"
        }
    }

    respuestas_json = {}

    # Realizar las consultas GET y persistir las respuestas crudas en JSON
    for key, info in endpoints.items():
        try:
            response = requests.get(info["url"], headers=headers, auth=auth, verify=False)
            if response.status_code == 200:
                content = response.json()
                respuestas_json[key] = content
                with open(info["file"], "w", encoding="utf-8") as f:
                    json.dump(content, f, indent=4)
                print(f"[+] Endpoint [{key}] guardado exitosamente.")
            else:
                print(f"[-] Error en {key}: Código HTTP {response.status_code}")
                respuestas_json[key] = None
        except Exception as e:
            print(f"[-] Error de conexión en {key}: {e}")
            respuestas_json[key] = None

    print("\n--- INICIANDO COMPARACIÓN DE CRITERIOS COMPLIANCE ---")
    criterios = 0

    # Criterio 1: Hostname Corporativo
    try:
        host_obtenido = respuestas_json["hostname"]["Cisco-IOS-XE-native:hostname"]
        c1 = "[OK]" if host_obtenido == data['cliente']['hostname'] else "[FAIL]"
    except:
        host_obtenido, c1 = "No encontrado", "[FAIL]"
    if c1 == "[OK]": criterios += 1
    print(f"Criterio 1 - Hostname corporativo: {host_obtenido} -> {c1}")

    # Criterio 2: IP Loopback de Gestión
    try:
        ip_obtenida = respuestas_json["loopback"]["ietf-interfaces:interface"]["ietf-ip:ipv4"]["address"][0]["ip"]
        c2 = "[OK]" if ip_obtenida == data['router']['loopback_ip'] else "[FAIL]"
    except:
        ip_obtenida, c2 = "No encontrado", "[FAIL]"
    if c2 == "[OK]": criterios += 1
    print(f"Criterio 2 - IP Loopback Gestión: {ip_obtenida} -> {c2}")

    # Criterio 3: Descripción Interfaz WAN
    try:
        desc_obtenida = respuestas_json["interfaces"]["ietf-interfaces:interface"]["description"]
        c3 = "[OK]" if desc_obtenida == data['router']['descripcion_wan'] else "[FAIL]"
    except:
        desc_obtenida, c3 = "No encontrado", "[FAIL]"
    if c3 == "[OK]": criterios += 1
    print(f"Criterio 3 - Descripción Interfaz WAN: {desc_obtenida} -> {c3}")

    # Criterio 4: Servidor NTP Configurado (Búsqueda flexible recursiva)
    ntp_target = data['router']['ntp_server']
    if respuestas_json.get("ntp") and buscar_valor_en_json(respuestas_json["ntp"], ntp_target):
        ntp_obtenido, c4 = ntp_target, "[OK]"
    else:
        ntp_obtenido, c4 = "No encontrado", "[FAIL]"
    if c4 == "[OK]": criterios += 1
    print(f"Criterio 4 - Servidor NTP Configurado: {ntp_obtenido} -> {c4}")

    # Reporte Global Final de la Fase 4
    print("\n======================================")
    print(f"Resultado: {criterios}/4 Criterios Correctos")
    if criterios == 4:
        print("STATUS GLOBAL: CONFORME")
    else:
        print("STATUS GLOBAL: NO CONFORME")
    print("======================================")

if __name__ == "__main__":
    main()
