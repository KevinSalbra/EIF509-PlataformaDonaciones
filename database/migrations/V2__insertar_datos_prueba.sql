-- =====================================================
-- Datos de prueba de AlimentaCR
-- Los identificadores explícitos permiten relacionar
-- los registros de PostgreSQL con los eventos de MongoDB.
-- =====================================================

-- =====================================================
-- 1. ORGANIZACIONES
-- =====================================================

INSERT INTO organizacion (
    id_organizacion,
    nombre,
    tipo,
    cedula_juridica,
    descripcion,
    direccion,
    telefono,
    estado,
    fecha_registro
)
VALUES
    (
        1,
        'Administración AlimentaCR',
        'DONANTE',
        '3-101-900001',
        'Organización utilizada para la administración de la plataforma.',
        'Heredia, Costa Rica',
        '2200-0001',
        'APROBADA',
        '2026-08-01 08:00:00'
    ),
    (
        2,
        'Supermercado La Esperanza',
        'DONANTE',
        '3-101-900002',
        'Supermercado donante de alimentos aptos para el consumo.',
        'San José, Costa Rica',
        '2200-0002',
        'APROBADA',
        '2026-08-02 09:00:00'
    ),
    (
        3,
        'Panadería El Trigal',
        'DONANTE',
        '3-101-900003',
        'Panadería local participante en el programa de donaciones.',
        'Heredia, Costa Rica',
        '2200-0003',
        'APROBADA',
        '2026-08-03 10:00:00'
    ),
    (
        4,
        'Fundación Manos Solidarias',
        'BENEFICIARIA',
        '3-101-900004',
        'Organización dedicada a brindar apoyo alimentario a familias.',
        'Alajuela, Costa Rica',
        '2200-0004',
        'APROBADA',
        '2026-08-04 11:00:00'
    ),
    (
        5,
        'Comedor Comunitario Nueva Vida',
        'BENEFICIARIA',
        '3-101-900005',
        'Comedor comunitario para personas en condición vulnerable.',
        'Cartago, Costa Rica',
        '2200-0005',
        'APROBADA',
        '2026-08-05 12:00:00'
    ),
    (
        6,
        'Asociación Ayuda del Valle',
        'BENEFICIARIA',
        '3-101-900006',
        'Asociación beneficiaria pendiente de aprobación.',
        'San Ramón, Alajuela, Costa Rica',
        '2200-0006',
        'PENDIENTE',
        '2026-08-20 09:30:00'
    );

-- =====================================================
-- 2. USUARIOS
-- =====================================================

INSERT INTO usuario (
    id_usuario,
    id_organizacion,
    nombre,
    correo,
    contrasena,
    telefono,
    rol,
    estado,
    fecha_registro
)
VALUES
    (
        1,
        1,
        'Administrador AlimentaCR',
        'admin@alimentacr.test',
        'hash_prueba_admin',
        '8800-0001',
        'ADMINISTRADOR',
        'ACTIVO',
        '2026-08-01 08:30:00'
    ),
    (
        2,
        2,
        'Laura Rodríguez',
        'laura.rodriguez@alimentacr.test',
        'hash_prueba_usuario_2',
        '8800-0002',
        'REPRESENTANTE_DONANTE',
        'ACTIVO',
        '2026-08-02 09:30:00'
    ),
    (
        3,
        3,
        'Carlos Jiménez',
        'carlos.jimenez@alimentacr.test',
        'hash_prueba_usuario_3',
        '8800-0003',
        'REPRESENTANTE_DONANTE',
        'ACTIVO',
        '2026-08-03 10:30:00'
    ),
    (
        4,
        4,
        'María Fernández',
        'maria.fernandez@alimentacr.test',
        'hash_prueba_usuario_4',
        '8800-0004',
        'REPRESENTANTE_BENEFICIARIA',
        'ACTIVO',
        '2026-08-04 11:30:00'
    ),
    (
        5,
        5,
        'José Vargas',
        'jose.vargas@alimentacr.test',
        'hash_prueba_usuario_5',
        '8800-0005',
        'REPRESENTANTE_BENEFICIARIA',
        'ACTIVO',
        '2026-08-05 12:30:00'
    ),
    (
        6,
        6,
        'Ana Morales',
        'ana.morales@alimentacr.test',
        'hash_prueba_usuario_6',
        '8800-0006',
        'REPRESENTANTE_BENEFICIARIA',
        'INACTIVO',
        '2026-08-20 10:00:00'
    );

-- =====================================================
-- 3. CATEGORÍAS
-- =====================================================

INSERT INTO categoria (
    id_categoria,
    nombre,
    descripcion,
    estado
)
VALUES
    (1, 'Frutas y verduras', 'Productos agrícolas frescos.', 'ACTIVA'),
    (2, 'Panadería', 'Pan, repostería y productos horneados.', 'ACTIVA'),
    (3, 'Granos y cereales', 'Arroz, frijoles, avena y otros granos.', 'ACTIVA'),
    (4, 'Lácteos', 'Leche, queso, yogur y productos relacionados.', 'ACTIVA'),
    (5, 'Alimentos enlatados', 'Productos enlatados no perecederos.', 'ACTIVA'),
    (6, 'Bebidas', 'Bebidas aptas para donación.', 'INACTIVA');

-- =====================================================
-- 4. DONACIONES
-- =====================================================

INSERT INTO donacion (
    id_donacion,
    id_organizacion_donante,
    id_categoria,
    alimento,
    descripcion,
    cantidad,
    unidad_medida,
    fecha_publicacion,
    fecha_limite_retiro,
    estado
)
VALUES
    (
        1,
        2,
        1,
        'Manzanas',
        'Manzanas en buen estado para consumo inmediato.',
        25.00,
        'KILOGRAMO',
        '2026-08-15 08:00:00',
        '2026-09-05',
        'DISPONIBLE'
    ),
    (
        2,
        3,
        2,
        'Pan cuadrado',
        'Paquetes de pan elaborados durante el día.',
        20.00,
        'PAQUETE',
        '2026-08-16 09:00:00',
        '2026-09-02',
        'ASIGNADA'
    ),
    (
        3,
        2,
        3,
        'Arroz',
        'Cajas con bolsas selladas de arroz.',
        10.00,
        'CAJA',
        '2026-08-17 10:00:00',
        '2026-09-15',
        'ENTREGADA'
    ),
    (
        4,
        2,
        5,
        'Atún enlatado',
        'Latas de atún dentro de su fecha de consumo.',
        48.00,
        'UNIDAD',
        '2026-08-18 11:00:00',
        '2026-10-30',
        'DISPONIBLE'
    ),
    (
        5,
        3,
        2,
        'Bollería variada',
        'Productos de panadería empacados.',
        15.00,
        'PAQUETE',
        '2026-08-19 12:00:00',
        '2026-09-03',
        'CANCELADA'
    ),
    (
        6,
        2,
        4,
        'Leche de larga duración',
        'Cajas de leche selladas.',
        30.00,
        'LITRO',
        '2026-08-20 13:00:00',
        '2026-09-20',
        'DISPONIBLE'
    );

-- =====================================================
-- 5. SOLICITUDES
-- =====================================================

INSERT INTO solicitud (
    id_solicitud,
    id_donacion,
    id_organizacion_beneficiaria,
    fecha_solicitud,
    estado,
    observacion
)
VALUES
    (
        1,
        1,
        4,
        '2026-08-16 08:30:00',
        'PENDIENTE',
        'La fundación requiere frutas para preparar paquetes de alimentos.'
    ),
    (
        2,
        1,
        5,
        '2026-08-16 09:15:00',
        'PENDIENTE',
        'El comedor solicita frutas para sus desayunos.'
    ),
    (
        3,
        2,
        4,
        '2026-08-17 10:00:00',
        'ACEPTADA',
        'Se solicita el pan para la alimentación del día siguiente.'
    ),
    (
        4,
        2,
        5,
        '2026-08-17 10:30:00',
        'RECHAZADA',
        'Solicitud rechazada porque otra organización fue seleccionada.'
    ),
    (
        5,
        3,
        5,
        '2026-08-18 11:00:00',
        'ACEPTADA',
        'Arroz solicitado para el comedor comunitario.'
    ),
    (
        6,
        4,
        4,
        '2026-08-19 12:00:00',
        'CANCELADA',
        'La organización canceló la solicitud antes de la asignación.'
    );

-- =====================================================
-- 6. ENTREGAS
-- =====================================================

INSERT INTO entrega (
    id_entrega,
    id_solicitud,
    fecha_creacion,
    fecha_acordada,
    lugar,
    observaciones,
    confirmacion_donante,
    confirmacion_beneficiario,
    estado
)
VALUES
    (
        1,
        3,
        '2026-08-17 11:00:00',
        '2026-09-01 09:00:00',
        'Sucursal central de Panadería El Trigal, Heredia',
        'La organización beneficiaria debe presentar identificación.',
        FALSE,
        FALSE,
        'PENDIENTE'
    ),
    (
        2,
        5,
        '2026-08-18 12:00:00',
        '2026-08-25 10:00:00',
        'Bodega de Supermercado La Esperanza, San José',
        'Entrega realizada y confirmada por ambas organizaciones.',
        TRUE,
        TRUE,
        'FINALIZADA'
    );

-- =====================================================
-- 7. ACTUALIZAR LAS SECUENCIAS DE IDENTIDAD
-- Esto evita que los próximos INSERT generen IDs repetidos.
-- =====================================================

ALTER TABLE organizacion
    ALTER COLUMN id_organizacion RESTART WITH 7;

ALTER TABLE usuario
    ALTER COLUMN id_usuario RESTART WITH 7;

ALTER TABLE categoria
    ALTER COLUMN id_categoria RESTART WITH 7;

ALTER TABLE donacion
    ALTER COLUMN id_donacion RESTART WITH 7;

ALTER TABLE solicitud
    ALTER COLUMN id_solicitud RESTART WITH 7;

ALTER TABLE entrega
    ALTER COLUMN id_entrega RESTART WITH 3;
