import logging
import asyncio
from pysnmp.hlapi.asyncio import (
    UsmUserData, 
    usmHMACMD5AuthProtocol,
    UdpTransportTarget, 
    ContextData, 
    ObjectType, 
    ObjectIdentity,
    SnmpEngine,
    Integer32
)

try:
    from pysnmp.hlapi.asyncio import getCmd as get_snmp_command
    from pysnmp.hlapi.asyncio import setCmd as set_snmp_command
except ImportError:
    from pysnmp.hlapi.asyncio import get_cmd as get_snmp_command
    from pysnmp.hlapi.asyncio import set_cmd as set_snmp_command

_LOGGER = logging.getLogger(__name__)

def preload_mibs(engine: SnmpEngine):
    try:
        engine.getMibBuilder().loadModules('SNMPv2-MIB')
        engine.getMibBuilder().loadModules('IP-MIB')
    except Exception as e:
        _LOGGER.debug("Не удалось предзагрузить MIB: %s", e)

async def get_snmp_data_map(engine, host, port, user, auth_key, oids_map):
    if not oids_map: return {}
    try:
        if not hasattr(engine, '_mibs_preloaded'):
            await asyncio.get_event_loop().run_in_executor(None, preload_mibs, engine)
            engine._mibs_preloaded = True

        auth_data = UsmUserData(user, authKey=auth_key, authProtocol=usmHMACMD5AuthProtocol)
        target = await UdpTransportTarget.create((host, port), timeout=5, retries=2)
        var_binds_input = [ObjectType(ObjectIdentity(oid)) for oid in oids_map.values()]

        async with asyncio.timeout(10):
            result = await get_snmp_command(engine, auth_data, target, ContextData(), *var_binds_input)
            error_indication, error_status, error_index, var_binds = result
            if error_indication or error_status: return {}
            return {str(vb[0]): vb[1].prettyPrint() for vb in var_binds}
    except Exception:
        return {}

# --- НОВАЯ ФУНКЦИЯ ДЛЯ ОТПРАВКИ КОМАНД ---
async def set_snmp_data(engine, host, port, user, auth_key, oid, value):
    try:
        auth_data = UsmUserData(user, authKey=auth_key, authProtocol=usmHMACMD5AuthProtocol)
        target = await UdpTransportTarget.create((host, port), timeout=5, retries=2)
        
        # Передаем значение как целое число (Integer32)
        var_binds_input = [ObjectType(ObjectIdentity(oid), Integer32(value))]

        async with asyncio.timeout(10):
            result = await set_snmp_command(engine, auth_data, target, ContextData(), *var_binds_input)
            error_indication, error_status, error_index, var_binds = result
            if error_indication or error_status:
                _LOGGER.error("Ошибка SNMP SET: %s", error_indication or error_status)
                return False
            return True
    except Exception as e:
        _LOGGER.error("Сбой отправки SNMP команды: %s", e)
        return False