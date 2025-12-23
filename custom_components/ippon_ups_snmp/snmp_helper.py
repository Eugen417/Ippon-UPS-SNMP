import logging
import asyncio
from pysnmp.hlapi.asyncio import (
    UsmUserData, 
    usmHMACMD5AuthProtocol,
    UdpTransportTarget, 
    ContextData, 
    ObjectType, 
    ObjectIdentity
)

# Выбор правильной команды для вашей версии библиотеки
try:
    from pysnmp.hlapi.asyncio import get_cmd as get_snmp_command
except ImportError:
    from pysnmp.hlapi.asyncio import getCmd as get_snmp_command

_LOGGER = logging.getLogger(__name__)

async def get_snmp_data_map(engine, host, port, user, auth_key, oids_map):
    """Опрос ИБП через SNMPv3 без лишнего логирования."""
    try:
        auth_data = UsmUserData(
            user, 
            authKey=auth_key, 
            authProtocol=usmHMACMD5AuthProtocol
        )
        
        target = await UdpTransportTarget.create((host, port), timeout=5, retries=2)
        var_binds_input = [ObjectType(ObjectIdentity(oid)) for oid in oids_map.values()]

        async with asyncio.timeout(10):
            result = await get_snmp_command(
                engine, 
                auth_data, 
                target, 
                ContextData(), 
                *var_binds_input
            )
            
            error_indication, error_status, _error_index, var_binds = result

            if error_indication:
                _LOGGER.error("Ошибка связи с ИБП %s: %s", host, error_indication)
                return {}
            
            if error_status:
                _LOGGER.error("Ошибка протокола ИБП %s: %s", host, error_status)
                return {}

            return {str(vb[0]): vb[1].prettyPrint() for vb in var_binds}

    except Exception as e:
        _LOGGER.error("Критический сбой SNMP хелпера на %s: %s", host, e)
        return {}
