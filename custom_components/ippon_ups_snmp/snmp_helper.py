import logging
from pysnmp.hlapi.asyncio import (
    SnmpEngine, 
    UsmUserData, 
    usmHMACMD5AuthProtocol,
    UdpTransportTarget, 
    ContextData, 
    ObjectType, 
    ObjectIdentity,
    get_cmd as getCmd 
)

_LOGGER = logging.getLogger(__name__)

async def get_snmp_data_map(engine, host, port, user, auth_key, oids_map):
    """
    Асинхронный групповой запрос через проверенный метод.
    """
    try:
        auth_data = UsmUserData(user, authKey=auth_key, authProtocol=usmHMACMD5AuthProtocol)
        # Создаем цель
        target = await UdpTransportTarget.create((host, port), timeout=3.0, retries=2)
        
        # Запрашиваем без поиска MIB (минимизируем блокировки)
        var_binds_input = [
            ObjectType(ObjectIdentity(oid).addAsn1MibSource()) 
            for oid in oids_map.values()
        ]

        result = await getCmd(
            engine, auth_data, target, ContextData(), *var_binds_input
        )

        error_indication, error_status, _, var_binds = result

        if error_indication or error_status:
            return {}

        results = {}
        for var_bind in var_binds:
            results[str(var_bind[0])] = var_bind[1]
        return results

    except Exception as e:
        _LOGGER.error("SNMP Helper Error: %s", e)
        return {}
