class ConflictoConcurrenciaError(RuntimeError):
    """
    Otra transaccion modifico el registro despues de que se leyo
    (bloqueo optimista). La detecta la capa de datos; la API la traduce
    a 409 Conflict con Problem Details.
    """