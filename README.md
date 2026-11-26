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

- Una fila es: Un incidente de ciberseguridad individual reportado, validado y gestionado por el ColCERT en Colombia (un evento único en una fecha de solicitud, sector y ubicación determinados).
- La identifica: El identificador interno de fila generado por la plataforma Socrata "socrata_id"
- Si llega una fila repetida: Se aplica una operación de actualización (upsert o MERGE) tomando como referencia su socrata_id. Si el identificador ya existe en la base de destino, se actualiza el registro vigente con los valores más recientes sin duplicar la fila; si todas las 9 columnas de negocio son idénticas pero tienen distinto socrata_id, se conserva el registro como evento independiente (ya que dos incidentes distintos pueden ocurrir el mismo día, en el mismo sector, departamento y con la misma tipología).
- Si falta un campo: Se aplica una regla de imputación controlada según la criticidad de la columna: 
    - Si falta fecha_de_solicitud o tipo_de_incidente, se envía a revisión y se excluye de los indicadores principales
    - Si falta un campo descriptivo o de clasificación (sector, orden_de_la_entidad, regi_n, departamento, clasificaci_n_taxonom_a o importancia), no se descarta la fila para no perder el conteo real de incidentes; se rellena con el valor estándar "NO REPORTADO" (y 0 o -1 en divipola_departamento) para que sea visible y filtrable en el tablero.

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
| Bruto cargado | `data/raw/agi2-ekag_2026-11-26_075222.json` |
| Tabla en BigQuery | `bruto.agi2_ekag` (todas las columnas como texto) |
| Traídas según `conteos.csv` | 4243 |
| `COUNT(*)` en BigQuery | 4243 |

### Staging: de dónde viene cada columna

Archivo: `sql/stg_agi2_ekag.sql` (vista `staging.stg_agi2_ekag`).

| Columna en el staging | Viene de (bruto) | Regla |
|---|---|---|
| `id_fila` | `socrata_id` | **T1:** Se renombra a `id_fila` para identificar de forma única cada registro. |
| `fecha_de_solicitud` | `fecha_de_solicitud` | **T2:** Se recortan los primeros 10 caracteres (quitando la hora) y se convierte a fecha (`DATE`) con `SAFE_CAST`. |
| `orden_de_la_entidad` | `orden_de_la_entidad` | Pasa sin cambios (texto). |
| `sector` | `sector` | Pasa sin cambios (texto). |
| `region` | `regi_n` | **T4:** Se renombra la columna a `region` para corregir el nombre; los valores pasan sin cambios. |
| `divipola_departamento` | `divipola_departamento` | **T3:** Se limpia de espacios y se convierte a número entero (`INT64`) con `SAFE_CAST`. |
| `departamento` | `departamento` | Pasa sin cambios (texto). |
| `clasificacion` | `clasificaci_n_taxonom_a` | **T5:** Se renombra la columna a `clasificacion` para simplificar el nombre; los valores pasan sin cambios. |
| `tipo_de_incidente` | `tipo_de_incidente` | Pasa sin cambios (texto). |
| `importancia` | `importancia` | Pasa sin cambios (texto). |
| `archivo_origen` | `archivo_origen` | Pasa sin cambios para conservar la trazabilidad del archivo cargado. |

> **Nota:** Las columnas técnicas `socrata_creado`, `socrata_actualizado` y `socrata_version` se excluyen del staging porque son metadatos internos de la plataforma de datos abiertos y no aportan al análisis.

### Conteo antes y después (`sql/controles_stg.sql`)

| Control | Bruto | Staging | ¿Es lo esperado? |
|---|---|---|---|
| **Filas totales** | 4243 | 4243 | Sí, se conservan todas las filas sin duplicar ni perder registros. |
| **`id_fila` nulos** | 0 | 0 | Sí, todos los registros tienen identificador único válido. |
| **`id_fila` distintos** | 4243 | 4243 | Sí, cada fila representa un único ciberincidente sin repeticiones. |
| **Nulos en `fecha_de_solicitud` (T2)** | 0 | 0 | Sí, todas las fechas tenían el formato esperado y se convirtieron sin errores. |
| **Nulos en `divipola_departamento` (T3)** | 0 | 0 | Sí, todos los códigos eran numéricos válidos y no se generaron nulos nuevos. |
| **Valores distintos en `region` (T4)** | 8 | 8 | Sí, se mantienen exactamente las mismas 8 regiones tras renombrar la columna. |
| **Valores distintos en `clasificacion` (T5)** | 12 | 12 | Sí, se mantienen exactamente las mismas 12 categorías tras renombrar la columna. |
