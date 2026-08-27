// =====================================================
// Datos de prueba para MongoDB
// AlimentaCR - Bitácora de eventos
//
// Los identificadores utilizados aquí corresponden a
// los registros insertados por la migración V2 de
// PostgreSQL.
// =====================================================

const dbAlimentaCR = db.getSiblingDB("alimentacr_bitacora");
const coleccionEventos = dbAlimentaCR.getCollection("eventos");

// Insertar las semillas solamente cuando la colección esté vacía.
if (coleccionEventos.countDocuments({}) === 0) {
    coleccionEventos.insertMany([
        {
            tipo_evento: "ORGANIZACION_REGISTRADA",
            fecha_hora: ISODate("2026-08-02T09:00:00Z"),
            usuario_id: 1,
            entidad: "ORGANIZACION",
            entidad_id: 2,
            datos: {
                nombre: "Supermercado La Esperanza",
                tipo_organizacion: "DONANTE"
            }
        },
        {
            tipo_evento: "ORGANIZACION_APROBADA",
            fecha_hora: ISODate("2026-08-02T10:00:00Z"),
            usuario_id: 1,
            entidad: "ORGANIZACION",
            entidad_id: 2,
            datos: {
                estado_anterior: "PENDIENTE",
                estado_nuevo: "APROBADA",
                observacion: "Documentación de la organización verificada."
            }
        },
        {
            tipo_evento: "ORGANIZACION_REGISTRADA",
            fecha_hora: ISODate("2026-08-04T11:00:00Z"),
            usuario_id: 1,
            entidad: "ORGANIZACION",
            entidad_id: 4,
            datos: {
                nombre: "Fundación Manos Solidarias",
                tipo_organizacion: "BENEFICIARIA"
            }
        },
        {
            tipo_evento: "ORGANIZACION_APROBADA",
            fecha_hora: ISODate("2026-08-04T12:00:00Z"),
            usuario_id: 1,
            entidad: "ORGANIZACION",
            entidad_id: 4,
            datos: {
                estado_anterior: "PENDIENTE",
                estado_nuevo: "APROBADA",
                observacion: "Organización beneficiaria aprobada."
            }
        },
        {
            tipo_evento: "DONACION_PUBLICADA",
            fecha_hora: ISODate("2026-08-15T08:00:00Z"),
            usuario_id: 2,
            entidad: "DONACION",
            entidad_id: 1,
            datos: {
                alimento: "Manzanas",
                cantidad: 25,
                unidad_medida: "KILOGRAMO",
                categoria_id: 1,
                organizacion_donante_id: 2,
                estado: "DISPONIBLE"
            }
        },
        {
            tipo_evento: "DONACION_PUBLICADA",
            fecha_hora: ISODate("2026-08-16T09:00:00Z"),
            usuario_id: 3,
            entidad: "DONACION",
            entidad_id: 2,
            datos: {
                alimento: "Pan cuadrado",
                cantidad: 20,
                unidad_medida: "PAQUETE",
                categoria_id: 2,
                organizacion_donante_id: 3,
                estado: "DISPONIBLE"
            }
        },
        {
            tipo_evento: "SOLICITUD_CREADA",
            fecha_hora: ISODate("2026-08-16T08:30:00Z"),
            usuario_id: 4,
            entidad: "SOLICITUD",
            entidad_id: 1,
            datos: {
                donacion_id: 1,
                organizacion_beneficiaria_id: 4,
                estado: "PENDIENTE"
            }
        },
        {
            tipo_evento: "SOLICITUD_CREADA",
            fecha_hora: ISODate("2026-08-16T09:15:00Z"),
            usuario_id: 5,
            entidad: "SOLICITUD",
            entidad_id: 2,
            datos: {
                donacion_id: 1,
                organizacion_beneficiaria_id: 5,
                estado: "PENDIENTE"
            }
        },
        {
            tipo_evento: "SOLICITUD_CREADA",
            fecha_hora: ISODate("2026-08-17T10:00:00Z"),
            usuario_id: 4,
            entidad: "SOLICITUD",
            entidad_id: 3,
            datos: {
                donacion_id: 2,
                organizacion_beneficiaria_id: 4,
                estado: "PENDIENTE"
            }
        },
        {
            tipo_evento: "SOLICITUD_ACEPTADA",
            fecha_hora: ISODate("2026-08-17T10:45:00Z"),
            usuario_id: 3,
            entidad: "SOLICITUD",
            entidad_id: 3,
            datos: {
                donacion_id: 2,
                organizacion_beneficiaria_id: 4,
                estado_anterior: "PENDIENTE",
                estado_nuevo: "ACEPTADA"
            }
        },
        {
            tipo_evento: "SOLICITUD_RECHAZADA",
            fecha_hora: ISODate("2026-08-17T10:45:00Z"),
            usuario_id: 3,
            entidad: "SOLICITUD",
            entidad_id: 4,
            datos: {
                donacion_id: 2,
                organizacion_beneficiaria_id: 5,
                estado_anterior: "PENDIENTE",
                estado_nuevo: "RECHAZADA",
                motivo: "Otra solicitud fue aceptada."
            }
        },
        {
            tipo_evento: "DONACION_ASIGNADA",
            fecha_hora: ISODate("2026-08-17T10:45:00Z"),
            usuario_id: 3,
            entidad: "DONACION",
            entidad_id: 2,
            datos: {
                solicitud_aceptada_id: 3,
                organizacion_beneficiaria_id: 4,
                estado_anterior: "DISPONIBLE",
                estado_nuevo: "ASIGNADA"
            }
        },
        {
            tipo_evento: "ENTREGA_PROGRAMADA",
            fecha_hora: ISODate("2026-08-17T11:00:00Z"),
            usuario_id: 3,
            entidad: "ENTREGA",
            entidad_id: 1,
            datos: {
                solicitud_id: 3,
                donacion_id: 2,
                fecha_acordada: ISODate("2026-09-01T09:00:00Z"),
                estado: "PENDIENTE"
            }
        },
        {
            tipo_evento: "DONACION_PUBLICADA",
            fecha_hora: ISODate("2026-08-17T10:00:00Z"),
            usuario_id: 2,
            entidad: "DONACION",
            entidad_id: 3,
            datos: {
                alimento: "Arroz",
                cantidad: 10,
                unidad_medida: "CAJA",
                categoria_id: 3,
                organizacion_donante_id: 2,
                estado: "DISPONIBLE"
            }
        },
        {
            tipo_evento: "SOLICITUD_CREADA",
            fecha_hora: ISODate("2026-08-18T11:00:00Z"),
            usuario_id: 5,
            entidad: "SOLICITUD",
            entidad_id: 5,
            datos: {
                donacion_id: 3,
                organizacion_beneficiaria_id: 5,
                estado: "PENDIENTE"
            }
        },
        {
            tipo_evento: "SOLICITUD_ACEPTADA",
            fecha_hora: ISODate("2026-08-18T11:30:00Z"),
            usuario_id: 2,
            entidad: "SOLICITUD",
            entidad_id: 5,
            datos: {
                donacion_id: 3,
                organizacion_beneficiaria_id: 5,
                estado_anterior: "PENDIENTE",
                estado_nuevo: "ACEPTADA"
            }
        },
        {
            tipo_evento: "DONACION_ASIGNADA",
            fecha_hora: ISODate("2026-08-18T11:30:00Z"),
            usuario_id: 2,
            entidad: "DONACION",
            entidad_id: 3,
            datos: {
                solicitud_aceptada_id: 5,
                organizacion_beneficiaria_id: 5,
                estado_anterior: "DISPONIBLE",
                estado_nuevo: "ASIGNADA"
            }
        },
        {
            tipo_evento: "ENTREGA_PROGRAMADA",
            fecha_hora: ISODate("2026-08-18T12:00:00Z"),
            usuario_id: 2,
            entidad: "ENTREGA",
            entidad_id: 2,
            datos: {
                solicitud_id: 5,
                donacion_id: 3,
                fecha_acordada: ISODate("2026-08-25T10:00:00Z"),
                estado: "PENDIENTE"
            }
        },
        {
            tipo_evento: "ENTREGA_CONFIRMADA",
            fecha_hora: ISODate("2026-08-25T11:00:00Z"),
            usuario_id: 5,
            entidad: "ENTREGA",
            entidad_id: 2,
            datos: {
                solicitud_id: 5,
                donacion_id: 3,
                confirmacion_donante: true,
                confirmacion_beneficiario: true,
                estado_nuevo: "FINALIZADA",
                observacion: "Entrega recibida correctamente."
            }
        },
        {
            tipo_evento: "DONACION_ENTREGADA",
            fecha_hora: ISODate("2026-08-25T11:05:00Z"),
            usuario_id: 2,
            entidad: "DONACION",
            entidad_id: 3,
            datos: {
                entrega_id: 2,
                solicitud_id: 5,
                estado_anterior: "ASIGNADA",
                estado_nuevo: "ENTREGADA"
            }
        },
        {
            tipo_evento: "DONACION_CANCELADA",
            fecha_hora: ISODate("2026-08-20T08:00:00Z"),
            usuario_id: 3,
            entidad: "DONACION",
            entidad_id: 5,
            datos: {
                alimento: "Bollería variada",
                estado_anterior: "DISPONIBLE",
                estado_nuevo: "CANCELADA",
                motivo: "Los productos dejaron de estar disponibles."
            }
        }
    ]);

    print(
        "Semillas insertadas correctamente: "
        + coleccionEventos.countDocuments({})
        + " eventos."
    );
} else {
    print(
        "La colección 'eventos' ya contiene datos. "
        + "No se insertaron semillas duplicadas."
    );
}