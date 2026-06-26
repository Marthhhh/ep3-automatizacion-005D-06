#!/usr/bin/env python3
# fase3_validacion_netconf/validacion_netconf.py

import os
import sys
import datetime
import yaml
import re
from ncclient import manager
import xml.etree.ElementTree as ET

def cargar_variables():
    ruta_vars = "../vars/vars_005D-06.yaml"
    if not os.path.exists(ruta_vars):
        print(f"[-] Error: No se encuentra el archivo de variables en {ruta_vars}")
        sys.exit(1)
    with open(ruta_vars, 'r') as f:
        return yaml.safe_load(f)

def main():
    print("=== METADATOS DE EJECUCIÓN NETCONF ===")
    print(f"Script: {os.path.basename(__file__)}")
    print(f"Fecha/Hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Host VM: {os.uname()[1]}")
    print("======================================\n")

    data = cargar_variables()
    filtro_xml = '<native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native"/>'

    print(f"[*] Conectando vía NETCONF a {data['router']['ip']}:830...")
    
    try:
        with manager.connect(
            host=data['router']['ip'],
            port=830,
            username=data['router']['usuario'],
            password=data['router']['password'],
            hostkey_verify=False,
            allow_agent=False,
            look_for_keys=False
        ) as m:
            
            rpc_reply = m.get_config(source='running', filter=('subtree', filtro_xml))
            raw_xml = rpc_reply.xml
            
            os.makedirs("evidencias", exist_ok=True)
            ruta_xml = "evidencias/rpc_reply_raw.xml"
            with open(ruta_xml, "w", encoding="utf-8") as f:
                f.write(raw_xml)
            print(f"[+] Archivo XML crudo guardado en: {ruta_xml}\n")
            
            # Limpieza drástica de namespaces para evitar conflictos
            xml_clean = re.sub(r'\sxmlns="[^"]+"', '', raw_xml)
            xml_clean = re.sub(r'\sxmlns:[^=]+="[^"]+"', '', xml_clean)
            xml_clean = re.sub(r'<\?[^>]*\?>', '', xml_clean) # Quitar declaración XML si existe
            
            root = ET.fromstring(xml_clean)
            
            # 1. Hostname
            hostname_val = "No encontrado"
            h_elem = root.find('.//hostname')
            if h_elem is not None:
                hostname_val = h_elem.text
            
            # 2 y 3. Loopback 10 (IP y Máscara)
            loopback_ip_val = "No encontrado"
            loopback_mask_val = "No encontrado"
            for lp in root.findall('.//Loopback'):
                name_elem = lp.find('name')
                if name_elem is not None and name_elem.text == str(data['router']['loopback_id']):
                    # Buscamos de forma recursiva cualquier tag que contenga la IP
                    for elem in lp.iter():
                        if elem.text == data['router']['loopback_ip']:
                            loopback_ip_val = elem.text
                        if elem.text == data['router']['loopback_mask']:
                            loopback_mask_val = elem.text

            # 4. Descripción WAN
            desc_wan_val = "No encontrado"
            for ge in root.findall('.//GigabitEthernet'):
                name_elem = ge.find('name')
                if name_elem is not None and name_elem.text == "1":
                    desc_elem = ge.find('description')
                    if desc_elem is not None:
                        desc_wan_val = desc_elem.text

            # 5. Servidor NTP
            ntp_val = "No encontrado"
            ntp_block = root.find('.//ntp')
            if ntp_block is not None:
                for elem in ntp_block.iter():
                    if elem.text == data['router']['ntp_server']:
                        ntp_val = elem.text
                        break

            # --- EVALUACIÓN FINAL ---
            criterios = 0
            
            c1 = "[OK]" if hostname_val == data['cliente']['hostname'] else "[FAIL]"
            if c1 == "[OK]": criterios += 1
            print(f"Criterio 1 - Hostname corporativo: {hostname_val} -> {c1}")
            
            c2 = "[OK]" if loopback_ip_val == data['router']['loopback_ip'] else "[FAIL]"
            if c2 == "[OK]": criterios += 1
            print(f"Criterio 2 - IP Loopback Gestión: {loopback_ip_val} -> {c2}")
            
            c3 = "[OK]" if loopback_mask_val == data['router']['loopback_mask'] else "[FAIL]"
            if c3 == "[OK]": criterios += 1
            print(f"Criterio 3 - Máscara Loopback Gestión: {loopback_mask_val} -> {c3}")
            
            c4 = "[OK]" if desc_wan_val == data['router']['descripcion_wan'] else "[FAIL]"
            if c4 == "[OK]": criterios += 1
            print(f"Criterio 4 - Descripción Interfaz WAN: {desc_wan_val} -> {c4}")
            
            c5 = "[OK]" if ntp_val == data['router']['ntp_server'] else "[FAIL]"
            if c5 == "[OK]": criterios += 1
            print(f"Criterio 5 - Servidor NTP Configurado: {ntp_val} -> {c5}")
            
            print("\n======================================")
            print(f"Resultado: {criterios}/5 Criterios Correctos")
            if criterios == 5:
                print("STATUS GLOBAL: CONFORME")
            else:
                print("STATUS GLOBAL: NO CONFORME")
            print("======================================")
            
    except Exception as e:
        print(f"[-] Fallo crítico en la sesión NETCONF: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
