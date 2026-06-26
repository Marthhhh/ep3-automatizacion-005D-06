# Informe Técnico de Implementación y Compliance Automatizado

## 1. Objetivo del proyecto
El presente proyecto consistió en la incorporación y el aprovisionamiento automatizado de un nuevo router corporativo para la empresa cliente TechSolutions Chile SpA. El objetivo fundamental fue ejecutar el ciclo completo de automatización de infraestructura de red: documentar el estado inicial de fábrica (baseline), habilitar los servicios programables, aplicar la configuración estándar de la compañía de forma reproducible y certificar de manera independiente mediante auditorías de software que el dispositivo se encuentra validado y listo para entrar en producción.

## 2. Alcance
El alcance de este trabajo abarcó las siguientes actividades técnicas:
* Captura de metadatos y estado del router (interfaces, plataforma y enrutamiento) previo a los cambios utilizando pyATS/Genie.
* Respaldo previo de la configuración de fábrica (running-config).
* Activación de los subsistemas NETCONF, RESTCONF e HTTP Seguro.
* Automatización de la configuración corporativa: asignación de hostname, banner de acceso legal, servidor NTP, descripción de la interfaz WAN GigabitEthernet1 e instanciación de la interfaz Loopback 10 de gestión.
* Auditorías independientes de solo lectura empleando scripts en Python con las librerías ncclient (NETCONF) y requests (RESTCONF).
* Análisis comparativo automatizado de estados (diff) y generación del certificado final de compliance.

Quedaron explícitamente fuera del alcance configuraciones de enrutamiento dinámico (OSPF, BGP), políticas avanzadas de seguridad perimetral (ACL, Zone-Based Firewall) o cualquier otro parámetro no provisto en la ficha de asignación del cliente.

## 3. Infraestructura utilizada
El entorno tecnológico empleado para el desarrollo y despliegue del proyecto consideró:
* **Estación de Trabajo (VM):** DEVASC VM (máquina virtual del ingeniero) ejecutando entorno Linux Ubuntu v20.04.
* **Dispositivo de Red (Dispositivo de Cliente):** Cisco CSR1kv (Cloud Services Router 1000v) operando con Cisco IOS-XE.
* **Control de Versiones y Auditoría:** Repositorio público/privado en GitHub (`ep3-automatizacion-005D-06`).
* **Software de Automatización:** Ansible Core v2.10+, pyATS v23.x (con Genie) y Python v3.8+.

## 4. Tecnologías empleadas y justificación
* **pyATS / Genie:** Se utilizó en la Fase 1 y Fase 5 porque permite conectarse vía CLI/SSH de forma agnóstica para "aprender" y estructurar el estado operativo interno del dispositivo en formatos JSON/Diccionarios. Es idóneo para generar snapshots estables y realizar comparaciones de estado de red complejas mediante su motor de `diff`.
* **Ansible:** Se seleccionó para la Fase 2 debido a su arquitectura sin agentes y su fuerte principio de idempotencia. Permite declarar configuraciones corporativas en Playbooks estructurados en YAML, garantizando que si se ejecuta dos veces, la segunda vuelta mantendrá el estado ideal sin duplicar comandos ni generar cortes en el router.
* **NETCONF:** Se empleó en la Fase 3 como protocolo de validación independiente ya que interactúa directamente con los modelos de datos YANG nativos del router a través de SSH (puerto 830), retornando la configuración completa del equipo en un árbol XML robusto y estructurado de solo lectura.
* **RESTCONF:** Se adoptó en la Fase 4 para la verificación de recursos específicos, ya que utiliza operaciones web estándar (HTTP GET) apuntando de forma directa a URLs conceptuales descritas en los modelos IETF y Cisco native, devolviendo payloads ligeros en formato JSON idóneos para auditorías rápidas por API.

## 5. Configuración aplicada
A continuación se detallan los parámetros técnicos definitivos implementados en el dispositivo del cliente:

| Parámetro Corporativo | Variable YAML Utilizada | Valor Final en el Router |
| :--- | :--- | :--- |
| **Código de Alumno** | `alumno.codigo` | 005D-06 |
| **Nombre Completo** | `alumno.nombre` | Devia Sepulveda Martin Antonio |
| **Empresa Cliente** | `cliente.empresa` | TechSolutions Chile SpA |
| **Hostname Corporativo** | `cliente.hostname` | RTR-TECHSOL |
| **IP Loopback de Gestión** | `router.loopback_ip` | 10.5.6.1 |
| **Máscara Loopback** | `router.loopback_mask` | 255.255.255.0 (Prefijo /24) |
| **Descripción Interfaz WAN** | `router.descripcion_wan` | Enlace-WAN-Temuco |
| **Banner de Acceso** | `router.banner` | ACCESO RESTRINGIDO - TECHSOL |
| **Servidor NTP Asignado** | `router.ntp_server` | 8.8.8.8 |

## 6. Resultados de validación
Las fases de auditoría programable e independiente arrojaron los siguientes resultados computacionales obligatorios:

| Criterio / Parámetro Verificado | Protocolo Utilizado | Estado | Dictamen Parcial |
| :--- | :--- | :--- | :--- |
| Hostname Corporativo (`RTR-TECHSOL`) | NETCONF (XML) | `[OK]` | CONFORME |
| Dirección IP Loopback (`10.5.6.1`) | NETCONF (XML) | `[OK]` | CONFORME |
| Máscara Loopback (`255.255.255.0`) | NETCONF (XML) | `[OK]` | CONFORME |
| Descripción Interfaz WAN (GigabitEthernet1) | NETCONF (XML) | `[OK]` | CONFORME |
| Servidor NTP Operacional (`8.8.8.8`) | NETCONF (XML) | `[OK]` | CONFORME |
| Hostname Corporativo (`RTR-TECHSOL`) | RESTCONF (JSON) | `[OK]` | CONFORME |
| Dirección IP Loopback (`10.5.6.1`) | RESTCONF (JSON) | `[OK]` | CONFORME |
| Descripción Interfaz WAN (GigabitEthernet1) | RESTCONF (JSON) | `[OK]` | CONFORME |
| Servidor NTP Operacional (`8.8.8.8`) | RESTCONF (JSON) | `[OK]` | CONFORME |

* **Resultado Global de Validación:** 100% de los criterios en conformidad.

## 7. Conclusiones
El despliegue automatizado concluyó de manera exitosa cubriendo satisfactoriamente el ciclo completo de provisionamiento programable. La utilización de herramientas de infraestructura como código (Ansible) eliminó los errores asociados a la configuración manual, y el uso coordinado de NETCONF y RESTCONF sirvió para validar de forma transparente e independiente la correcta aplicación de la política corporativa. El análisis final con `genie diff` certificó los cambios exactos aplicados frente al baseline original de fábrica. Por lo tanto, el router se declara en estado **GLOBAL CONFORME** y queda formalmente entregado al área de operaciones de TechSolutions Chile SpA.
