import logging
from pysnmp.hlapi.asyncio import (
    SnmpEngine, UsmUserData, usmHMACMD5AuthProtocol,
    UdpTransportTarget, ContextData, ObjectType, ObjectIdentity,
    get_cmd as getCmd 
)

_LOGGER = logging.getLogger(__name__)

async def get_snmp_data_map(engine, host, port, user, auth_key, oids_map):
    try:
        auth_data = UsmUserData(user, authKey=auth_key, authProtocol=usmHMACMD5AuthProtocol)
        target = await UdpTransportTarget.create((host, port), timeout=3.0, retries=2)
        
        # Собираем список всех OID для одного запроса
        var_binds_input = [ObjectType(ObjectIdentity(oid)) for oid in oids_map.values()]

        result = await getCmd(
            engine, auth_data, target, ContextData(), *var_binds_input
        )

        error_indication, error_status, _, var_binds = result

        if error_indication or error_status:
            _LOGGER.debug("SNMP Error: %s", error_indication or error_status)
            return {}

        # Возвращаем словарь результатов
        results = {}
        for var_bind in var_binds:
            results[str(var_bind[0])] = var_bind[1]
        return results

    except Exception as e:
        _LOGGER.error("SNMP Helper Error: %s", e)
        return {}
