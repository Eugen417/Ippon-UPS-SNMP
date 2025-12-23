import logging
from pysnmp.hlapi.asyncio import (
    SnmpEngine, 
    UsmUserData, 
    usmHMACMD5AuthProtocol,
    UdpTransportTarget, 
    ContextData, 
    ObjectType, 
    ObjectIdentity,
    getCmd
)

_LOGGER = logging.getLogger(__name__)

async def get_snmp_data_map(engine, host, port, user, auth_key, oids_map):
    """Асинхронный опрос через SNMPv3 AuthNoPriv."""
    try:
        # Настройка авторизации: MD5 и отсутствие приватного ключа (authNoPriv)
        auth_data = UsmUserData(
            user, 
            authKey=auth_key, 
            authProtocol=usmHMACMD5AuthProtocol
            # Шифрование (privKey) не указываем, так как используем authNoPriv
        )
        
        # Прямой конструктор цели
        target = UdpTransportTarget((host, port), timeout=5.0, retries=3)
        
        # Формируем список OID
        var_binds_input = [
            ObjectType(ObjectIdentity(oid).addAsn1MibSource()) 
            for oid in oids_map.values()
        ]

        # Запрос
        result = await getCmd(engine, auth_data, target, ContextData(), *var_binds_input)
        error_indication, error_status, _, var_binds = result

        if error_indication:
            _LOGGER.error("v3 Сетевая ошибка: %s", error_indication)
            return {}
        
        if error_status:
            _LOGGER.error("v3 Ошибка ИБП: %s", error_status)
            return {}

        # Возвращаем данные
        return {str(vb[0]): vb[1].prettyPrint() for vb in var_binds}

    except Exception as e:
        _LOGGER.error("Критическая ошибка v3 хелпера: %s", e)
        return {}
