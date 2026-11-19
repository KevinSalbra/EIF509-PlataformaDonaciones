-- =====================================================================
-- V3: columna de version para el bloqueo optimista 
-- =====================================================================
-- Cada UPDATE ejecutado por la aplicacion incrementa `version` y solo
-- se aplica si la fila conserva la version que se leyo
-- (UPDATE ... WHERE id = ? AND version = ?). Si otra transaccion ya
-- modifico la fila, el UPDATE afecta 0 filas y la API responde 409.
--
-- Entrega:   la coordinan a la vez la organizacion donante y la
--            beneficiaria (PATCH /entregas/{id}).
-- Solicitud: puede aceptarla el donante mientras la beneficiaria la
--            cancela (POST .../entrega vs DELETE /solicitudes/{id}).
--
-- DEFAULT 0 deja las filas existentes en la version inicial.

ALTER TABLE entrega
    ADD COLUMN version BIGINT NOT NULL DEFAULT 0;

ALTER TABLE solicitud
    ADD COLUMN version BIGINT NOT NULL DEFAULT 0;