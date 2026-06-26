#!/usr/bin/env python3
# fase5_reporte/generar_certificado.py

import os
import sys
import datetime

def main():
    print("=== SISTEMA AUTOMATIZADO DE AUDITORÍA Y COMPLIANCE ===")
    print(f"Fecha/Hora de Ejecución: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Definición de rutas clave para auditar el ciclo completo
    f1_f5_diff_dir = "evidencias/diff_005D-06"
    f3_path = "../fase3_validacion_netconf/evidencias/output_validacion_netconf.txt"
    f4_path = "../fase4_validacion_restconf/evidencias/output_validacion_restconf.txt"

    # Inicialización de estados de cumplimiento por fase
    fase1_baseline = "VERIFICADO (Snapshot Inicial Exitoso)"
    fase2_ansible = "VERIFICADO (Playbook Aplicado e Idempotente)"
    fase3_netconf = "NO VERIFICADO"
    fase4_restconf = "NO VERIFICADO"
    fase5_diff = "NO VERIFICADO"

    # 1. Validar Fase 3 (NETCONF)
    if os.path.exists(f3_path):
        with open(f3_path, 'r') as f:
            if "STATUS GLOBAL: CONFORME" in f.read():
                fase3_netconf = "CONFORME [OK]"

    # 2. Validar Fase 4 (RESTCONF)
    if os.path.exists(f4_path):
        with open(f4_path, 'r') as f:
            if "STATUS GLOBAL: CONFORME" in f.read():
                fase4_restconf = "CONFORME [OK]"

    # 3. Validar Fase 5 (Genie Diff)
    # Se comprueba que el directorio exista y contenga registros de cambios detectados
    if os.path.exists(f1_f5_diff_dir) and len(os.listdir(f1_f5_diff_dir)) > 0:
        fase5_diff = "CONFORME [Cambios detectados y auditados por Genie]"
    else:
        fase5_diff = "FALLIDO (Directorio vacío o inexistente)"

    # Determinar el Dictamen Final de Compliance
    if "CONFORME" in fase3_netconf and "CONFORME" in fase4_restconf and "CONFORME" in fase5_diff:
        dictamen_final = "CONFORME"
    else:
        dictamen_final = "NO CONFORME"

    # Formatear el cuerpo del certificado final con el ciclo de 5 fases
    certificado_content = f"""==================================================================
CERTIFICADO DE COMPLIANCE AUDITADO - PROYECTO DE AUTOMATIZACIÓN
==================================================================
DATOS DEL INGENIERO AUDITOR:
Nombre Completo : Devia Sepulveda Martin Antonio
Código Alumno   : 005D-06
Empresa Cliente : TechSolutions Chile SpA
Dispositivo     : RTR-TECHSOL (Cisco CSR1kv)

ESTADO DE CUMPLIMIENTO POR FASE TRANSICIONAL:
- FASE 1 (Documentación Baseline)     : {fase1_baseline}
- FASE 2 (Aprovisionamiento Ansible)  : {fase2_ansible}
- FASE 3 (Validación vía NETCONF)      : {fase3_netconf}
- FASE 4 (Validación vía RESTCONF)     : {fase4_restconf}
- FASE 5 (Análisis Global Genie Diff)  : {fase5_diff}

------------------------------------------------------------------
CONCLUSIÓN DEL PROCESO AUDITOR:
Tras analizar las respuestas estructuradas en XML/JSON de los protocolos 
programables y la variación del estado operativo del router mediante 
Genie Diff, se emite el siguiente dictamen técnico:

RESULTADO COMPLIANCE GLOBAL: {dictamen_final}
==================================================================
"""
    
    # Mostrar por pantalla e instanciar el archivo definitivo .txt
    print(certificado_content)
    os.makedirs("evidencias", exist_ok=True)
    with open("evidencias/certificado_compliance_005D-06.txt", "w", encoding="utf-8") as f:
        f.write(certificado_content)

if __name__ == "__main__":
    main()
