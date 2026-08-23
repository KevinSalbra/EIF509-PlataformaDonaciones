Database Markup lenguage (DBML) del diagrama SQL de la base de datos, se brinda para que cualquiera que tenga acceso a este documento puedo replicar el diagrama.

recomendacion: https://dbdiagram.io/home


Project AlimentaCR {
  database_type: 'PostgreSQL'
  Note: 'Modelo relacional normalizado en tercera forma normal para la plataforma AlimentaCR.'
}


// ======================================================
// ENUMERACIONES
// ======================================================

Enum tipo_organizacion {
  DONANTE
  BENEFICIARIA
}

Enum estado_organizacion {
  PENDIENTE
  APROBADA
  RECHAZADA
  INACTIVA
}

Enum rol_usuario {
  ADMINISTRADOR
  REPRESENTANTE_DONANTE
  REPRESENTANTE_BENEFICIARIA
}

Enum estado_usuario {
  ACTIVO
  INACTIVO
}

Enum estado_categoria {
  ACTIVA
  INACTIVA
}

Enum estado_donacion {
  DISPONIBLE
  ASIGNADA
  ENTREGADA
  CANCELADA
  VENCIDA
}

Enum estado_solicitud {
  PENDIENTE
  ACEPTADA
  RECHAZADA
  CANCELADA
}

Enum estado_entrega {
  PENDIENTE
  FINALIZADA
  CANCELADA
}

Enum unidad_medida {
  KILOGRAMO
  GRAMO
  LITRO
  UNIDAD
  PAQUETE
}

// ======================================================
// TABLA ORGANIZACION
// ======================================================

Table organizacion {
  id_organizacion bigint [pk, increment]

  nombre varchar(150) [not null]

  tipo tipo_organizacion [not null]

  cedula_juridica varchar(30) [not null, unique]

  descripcion varchar(500)

  direccion varchar(250) [not null]

  telefono varchar(20) [not null]

  estado estado_organizacion [not null, default: 'PENDIENTE']

  fecha_registro timestamp [not null]

  Note: 'Representa una organización donante o beneficiaria. Solo las organizaciones aprobadas pueden participar en los procesos principales.'
}


// ======================================================
// TABLA USUARIO
// ======================================================

Table usuario {
  id_usuario bigint [pk, increment]

  id_organizacion bigint [not null]

  nombre varchar(150) [not null]

  correo varchar(150) [not null, unique]

  contrasena varchar(255) [not null, note: 'Debe almacenar el hash de la contraseña.']

  telefono varchar(20)

  rol rol_usuario [not null]

  estado estado_usuario [not null, default: 'ACTIVO']

  fecha_registro timestamp [not null]

  indexes {
    id_organizacion [name: 'idx_usuario_organizacion']
    estado [name: 'idx_usuario_estado']
  }

  Note: 'Cada usuario pertenece a una organización. El rol determina las operaciones permitidas.'
}


// ======================================================
// TABLA CATEGORIA
// ======================================================

Table categoria {
  id_categoria bigint [pk, increment]

  nombre varchar(100) [not null, unique]

  descripcion varchar(250)

  estado estado_categoria [not null, default: 'ACTIVA']

  Note: 'Clasifica los alimentos publicados. Una categoría inactiva no puede usarse en nuevas donaciones.'
}


// ======================================================
// TABLA DONACION
// ======================================================

Table donacion {
  id_donacion bigint [pk, increment]

  id_organizacion_donante bigint [not null]

  id_categoria bigint [not null]

  alimento varchar(150) [not null]

  descripcion varchar(500)

  cantidad decimal(10,2) [not null, note: 'Debe ser mayor que cero.']

  unidad_medida unidad_medida [not null]

  fecha_publicacion timestamp [not null]

  fecha_limite_retiro date [not null, note: 'Debe ser posterior a la fecha de publicación y a la fecha actual al crear la donación.']

  estado estado_donacion [not null, default: 'DISPONIBLE']

  indexes {
    id_organizacion_donante [name: 'idx_donacion_organizacion']
    id_categoria [name: 'idx_donacion_categoria']
    estado [name: 'idx_donacion_estado']
    fecha_limite_retiro [name: 'idx_donacion_fecha_limite']
    (estado, id_categoria) [name: 'idx_donacion_estado_categoria']
  }

  Note: 'Cada donación pertenece a una organización donante y a una categoría. Una donación se asigna completamente a una sola organización beneficiaria.'
}


// ======================================================
// TABLA SOLICITUD
// ======================================================

Table solicitud {
  id_solicitud bigint [pk, increment]

  id_donacion bigint [not null]

  id_organizacion_beneficiaria bigint [not null]

  fecha_solicitud timestamp [not null]

  estado estado_solicitud [not null, default: 'PENDIENTE']

  observacion varchar(500)

  indexes {
    id_donacion [name: 'idx_solicitud_donacion']

    id_organizacion_beneficiaria [name: 'idx_solicitud_organizacion']

    estado [name: 'idx_solicitud_estado']

    (id_donacion, estado) [name: 'idx_solicitud_donacion_estado']

    (id_organizacion_beneficiaria, estado) [name: 'idx_solicitud_organizacion_estado']
  }

  Note: 'Una donación puede recibir varias solicitudes, pero solo una puede ser aceptada. Una organización no puede tener dos solicitudes pendientes para la misma donación.'
}


// ======================================================
// TABLA ENTREGA
// ======================================================

Table entrega {
  id_entrega bigint [pk, increment]

  id_solicitud bigint [not null, unique]

  fecha_creacion timestamp [not null]

  fecha_acordada timestamp [note: 'Se completa durante la coordinación de la entrega.']

  lugar varchar(250) [note: 'Puede estar vacío cuando se crea inicialmente la entrega.']

  observaciones varchar(500)

  confirmacion_donante boolean [not null, default: false]

  confirmacion_beneficiario boolean [not null, default: false]

  estado estado_entrega [not null, default: 'PENDIENTE']

  indexes {
    estado [name: 'idx_entrega_estado']
    fecha_acordada [name: 'idx_entrega_fecha_acordada']
  }

  Note: 'La entrega se crea únicamente desde una solicitud aceptada. Una solicitud puede generar como máximo una entrega.'
}


// ======================================================
// RELACIONES
// ======================================================

// Una organización puede tener muchos usuarios.
// Cada usuario pertenece exactamente a una organización.
Ref fk_usuario_organizacion {
  usuario.id_organizacion > organizacion.id_organizacion
}


// Una organización donante puede publicar muchas donaciones.
// Cada donación pertenece exactamente a una organización donante.
Ref fk_donacion_organizacion {
  donacion.id_organizacion_donante > organizacion.id_organizacion
}


// Una categoría puede clasificar muchas donaciones.
// Cada donación pertenece exactamente a una categoría.
Ref fk_donacion_categoria {
  donacion.id_categoria > categoria.id_categoria
}


// Una donación puede recibir muchas solicitudes.
// Cada solicitud pertenece exactamente a una donación.
Ref fk_solicitud_donacion {
  solicitud.id_donacion > donacion.id_donacion
}


// Una organización beneficiaria puede realizar muchas solicitudes.
// Cada solicitud pertenece exactamente a una organización beneficiaria.
Ref fk_solicitud_organizacion {
  solicitud.id_organizacion_beneficiaria > organizacion.id_organizacion
}


// Una solicitud puede generar cero o una entrega.
// Cada entrega corresponde exactamente a una solicitud.
// El campo id_solicitud es UNIQUE para impedir múltiples entregas.
Ref fk_entrega_solicitud {
  entrega.id_solicitud - solicitud.id_solicitud
}