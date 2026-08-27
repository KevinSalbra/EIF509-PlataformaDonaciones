// ============================================
// Inicialización de MongoDB - AlimentaCR
// Bitácora de eventos del sistema
// ============================================

// Seleccionar la base de datos de la aplicación
const dbAlimentaCR = db.getSiblingDB("alimentacr_bitacora");

// --------------------------------------------
// 1. Crear la colección "eventos"
// --------------------------------------------
if (!dbAlimentaCR.getCollectionNames().includes("eventos")) {
    dbAlimentaCR.createCollection("eventos");
}

// --------------------------------------------
// 2. Crear los índices
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
print("Colección 'eventos' e índices creados.");