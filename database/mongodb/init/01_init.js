// ============================================
// Inicialización de MongoDB - AlimentaCR
// Bitácora de eventos del sistema
// ============================================

// Seleccionar la base de datos de la aplicación
const dbAlimentaCR = db.getSiblingDB("alimentacr_bitacora");

// --------------------------------------------
// 1. Definir el validador de eventos
// --------------------------------------------

const validadorEventos = {
    $jsonSchema: {
        bsonType: "object",

        required: [
            "tipo_evento",
            "fecha_hora",
            "entidad",
            "entidad_id"
        ],

        properties: {
            tipo_evento: {
                bsonType: "string",
                description:
                    "El tipo de evento debe pertenecer al catálogo permitido.",
                enum: [
                    "ORGANIZACION_REGISTRADA",
                    "ORGANIZACION_APROBADA",
                    "DONACION_PUBLICADA",
                    "DONACION_ASIGNADA",
                    "DONACION_ENTREGADA",
                    "DONACION_CANCELADA",
                    "SOLICITUD_CREADA",
                    "SOLICITUD_ACEPTADA",
                    "SOLICITUD_RECHAZADA",
                    "ENTREGA_PROGRAMADA",
                    "ENTREGA_CONFIRMADA",
                    "ENTREGA_CANCELADA"
                ]
            },

            fecha_hora: {
                bsonType: "date",
                description:
                    "La fecha y hora del evento debe ser de tipo Date."
            },

            usuario_id: {
                bsonType: ["int", "long"],
                description:
                    "Identificador del usuario que realizó la acción."
            },

            entidad: {
                bsonType: "string",
                description:
                    "La entidad debe pertenecer al catálogo permitido.",
                enum: [
                    "ORGANIZACION",
                    "DONACION",
                    "SOLICITUD",
                    "ENTREGA"
                ]
            },

            entidad_id: {
                bsonType: ["int", "long"],
                description:
                    "Identificador de la entidad afectada."
            },

            datos: {
                bsonType: "object",
                description:
                    "Información adicional y flexible propia del evento."
            }
        }
    }
};

// --------------------------------------------
// 2. Crear la colección "eventos"
// --------------------------------------------

if (!dbAlimentaCR.getCollectionNames().includes("eventos")) {
    dbAlimentaCR.createCollection(
        "eventos",
        {
            validator: validadorEventos,
            validationLevel: "strict",
            validationAction: "error"
        }
    );

    print("Colección 'eventos' creada con su validador.");
} else {
    // Si la colección ya existe, actualizar su validador
    dbAlimentaCR.runCommand({
        collMod: "eventos",
        validator: validadorEventos,
        validationLevel: "strict",
        validationAction: "error"
    });

    print("Validador de la colección 'eventos' actualizado.");
}

// --------------------------------------------
// 3. Crear los índices
// --------------------------------------------

// Índice por fecha_hora
dbAlimentaCR.eventos.createIndex(
    { fecha_hora: -1 },
    { name: "idx_fecha_hora" }
);

// Índice por usuario_id
dbAlimentaCR.eventos.createIndex(
    { usuario_id: 1 },
    { name: "idx_usuario_id" }
);

// Índice compuesto por entidad + entidad_id
dbAlimentaCR.eventos.createIndex(
    { entidad: 1, entidad_id: 1 },
    { name: "idx_entidad_entidad_id" }
);

// Índice por tipo_evento
dbAlimentaCR.eventos.createIndex(
    { tipo_evento: 1 },
    { name: "idx_tipo_evento" }
);

print("Base de datos alimentacr_bitacora inicializada correctamente.");
print("Colección 'eventos', validador e índices configurados.");