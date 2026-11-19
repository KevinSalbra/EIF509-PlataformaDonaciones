-- =====================================================
-- V3: configurar contrasenas de las cuentas de prueba
--
-- La contrasena fue entregada directamente al evaluador.
-- En la base de datos se conserva únicamente su hash.
-- =====================================================

UPDATE usuario
SET contrasena = 'pbkdf2_sha256$600000$pPVAGrxwJ5jVZL0tl70JpM$v2bg5zDa7EnGsSEL5LImIkxZNdoTJ73bRMoyjGQfzrc='
WHERE correo IN (
    'admin@alimentacr.test',
    'laura.rodriguez@alimentacr.test',
    'carlos.jimenez@alimentacr.test',
    'maria.fernandez@alimentacr.test',
    'jose.vargas@alimentacr.test',
    'ana.morales@alimentacr.test'
);