# Nombre del proyecto

Equipo E__12 · Análisis de Datos Intermedio · Estud-IA (Capa 2)

## Brief v1

| Campo | Respuesta |
|---|---|
| Usuario y decisión | Director de Seguridad Digital decide qué órdenes de entidad (nacional, territorial o privado) priorizar para campañas de prevención, alertas tempranas y asignación de capacidad de respuesta, revisando el tablero quincenalmente (en línea con la actualización del dataset). | 
| Pregunta | ¿Qué tipos de entidad concentran los ciberincidentes de mayor importancia en Colombia y cuál es el tipo de ataque predominante en cada uno? | 
| Fuente con API | https://www.datos.gov.co/resource/agi2-ekag.json | 
| Qué representa una fila | Un incidente de ciberseguridad individual reportado, validado y gestionado por el ColCERT. | 
| Campo que la identifica | No existe un campo de llave primaria en el esquema público (9 columnas). Se debe usar el identificador interno de fila de Socrata (:id vía API, consultando $select=:id). | 
| Cada cuánto se actualiza | Quincenalmente. | 
| Dato a confirmar | Confirmar los valores exactos de dominio (catálogo de categorías) de las columnas importancia (ej. Alta, Media, Baja según Resolución 500 de 2021), orden_de_la_entidad y clasificaci_n_taxonom_a mediante una consulta GROUP BY al endpoint para validar que no existan nulos, duplicados ortográficos o variaciones de mayúsculas/minúsculas. | 
| Tres indicadores | 1. Porcentaje de incidentes de importancia crítica/alta sobre el total de incidentes por sector (% Incidentes Críticos por Sector). · 2. Tasa de variación quincenal de incidentes por tipo de ataque (Variación % Quincenal por Tipo de Incidente). · 3. Índice de concentración territorial (% de incidentes por Región / Departamento frente al total nacional). |
| Terminó bien si… | Al consumir el API, el tablero cruza sin errores de nulos o categorías duplicadas las 5.699 filas vigentes y responde en una sola vista qué sector lidera los incidentes de mayor importancia y cuál es su vector de ataque principal (Sí / No verificable por cualquier revisor). | 
| No vamos a construir | Trazabilidad por entidad específica (los registros están anonimizados a nivel de sector y orden de entidad). | 

## Contrato de datos

- Una fila es:
- La identifica:
- Si llega una fila repetida:
- Si falta un campo:

## Bitácora de decisiones

| Fecha | Decisión | Por qué |
|---|---|---|
| | | |

## Reglas del repositorio

- Es público: nada de datos personales, contraseñas, tokens ni llaves.
- Las credenciales van en un archivo `.env`, que Git ignora (ver `.gitignore`). `.env.example` muestra qué variables hacen falta, sin valores.
- Cada commit explica en su mensaje qué se decidió y por qué.

## Carga y staging

### Carga a BigQuery

| | |
|---|---|
| Bruto cargado | `data/raw/…json` |
| Tabla en BigQuery | `bruto.…` (todas las columnas como texto) |
| Traídas según `conteos.csv` | |
| `COUNT(*)` en BigQuery | |

### Staging: de dónde viene cada columna

Archivo: `sql/stg_….sql` (vista `staging.stg_…`).

| Columna en el staging | Viene de (bruto) | Regla |
|---|---|---|
| | | |

### Conteo antes y después (`sql/controles_stg.sql`)

| Control | Bruto | Staging | ¿Es lo esperado? |
|---|---|---|---|
| Filas | | | |
