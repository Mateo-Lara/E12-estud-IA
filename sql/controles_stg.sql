-- sql/ctrl_stg_agi2_ekag.sql
-- Cifras de control del staging: filas antes y después, nulos nuevos y valores distintos.
SELECT '01 filas en el bruto' AS control, COUNT(*) AS valor FROM bruto.agi2_ekag
UNION ALL SELECT '02 filas en el staging', COUNT(*) FROM staging.stg_agi2_ekag
UNION ALL SELECT '03 T1: id_fila nulos', COUNTIF(id_fila IS NULL) FROM staging.stg_agi2_ekag
UNION ALL SELECT '04 T1: id_fila distintos', COUNT(DISTINCT id_fila) FROM staging.stg_agi2_ekag
UNION ALL SELECT '05 T2: fecha_de_solicitud nulos antes', COUNTIF(fecha_de_solicitud IS NULL OR TRIM(fecha_de_solicitud) = '') FROM bruto.agi2_ekag
UNION ALL SELECT '06 T2: fecha_de_solicitud nulos después', COUNTIF(fecha_de_solicitud IS NULL) FROM staging.stg_agi2_ekag
UNION ALL SELECT '07 T3: divipola_departamento nulos antes', COUNTIF(divipola_departamento IS NULL OR TRIM(divipola_departamento) = '') FROM bruto.agi2_ekag
UNION ALL SELECT '08 T3: divipola_departamento nulos después', COUNTIF(divipola_departamento IS NULL) FROM staging.stg_agi2_ekag
UNION ALL SELECT '09 T4: region distintos antes', COUNT(DISTINCT regi_n) FROM bruto.agi2_ekag
UNION ALL SELECT '10 T4: region distintos después', COUNT(DISTINCT region) FROM staging.stg_agi2_ekag
UNION ALL SELECT '11 T5: clasificacion distintos antes', COUNT(DISTINCT clasificaci_n_taxonom_a) FROM bruto.agi2_ekag
UNION ALL SELECT '12 T5: clasificacion distintos después', COUNT(DISTINCT clasificacion) FROM staging.stg_agi2_ekag
ORDER BY control;
