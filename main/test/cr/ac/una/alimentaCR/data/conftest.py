import pytest


@pytest.fixture(autouse=True)
def usar_esquema_flyway(preparar_esquema_flyway):
    """
    Garantiza que las pruebas de la capa data se ejecuten
    utilizando el esquema preparado por Flyway.
    """
    pass