-- sql/stg_agi2_ekag.sql
-- Staging de agi2_ekag
-- Origen: bruto.agi2_ekag, cargado tal como llegó de la API (todo es texto).
-- T1: Renombrar socrata_id como id_fila para identificar cada registro (ej. 'row-dhj2~i5pi~6b3d' -> 'row-dhj2~i5pi~6b3d').
-- T2: Cortar los primeros 10 caracteres de fecha_de_solicitud para quitar la hora y convertirlo a tipo fecha DATE (ej. '2020-04-08T00:00:00.000' -> 2020-04-08, que se visualiza como 08-04-2020).
-- T3: Convertir divipola_departamento de texto a número entero INT64 (ej. '11' -> 11).
-- T4: Renombrar regi_n como region para corregir el nombre de la columna sin alterar su texto (ej. 'Bogotá D.C.' -> 'Bogotá D.C.').
-- T5: Renombrar clasificaci_n_taxonom_a como clasificacion para simplificar el nombre de la columna sin alterar su texto (ej. 'Compromiso de Información' -> 'Compromiso de Información').

CREATE OR REPLACE VIEW staging.stg_agi2_ekag AS
SELECT
  socrata_id AS id_fila,                                                                  -- T1
  SAFE_CAST(SUBSTR(TRIM(fecha_de_solicitud), 1, 10) AS DATE) AS fecha_de_solicitud,       -- T2
  orden_de_la_entidad,
  sector,
  regi_n AS region,                                                                       -- T4
  SAFE_CAST(TRIM(divipola_departamento) AS INT64) AS divipola_departamento,               -- T3
  departamento,
  clasificaci_n_taxonom_a AS clasificacion,                                               -- T5
  tipo_de_incidente,
  importancia,
  archivo_origen
FROM bruto.agi2_ekag;