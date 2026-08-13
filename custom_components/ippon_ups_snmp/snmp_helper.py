import logging
import asyncio

_LOGGER = logging.getLogger(__name__)

def _fetch_sync_isolated(host, port, user, auth_key, oids_map):
    """Синхронная функция, работающая в фоне. Запускает собственный изолированный цикл asyncio."""
    
    async def _do_fetch():
        # Все импорты здесь, чтобы они не триггерились при старте HA
        import pysnmp.hlapi.asyncio as hlapi
        try:
            getCmd = hlapi.getCmd
        except AttributeError:
            getCmd = hlapi.get_cmd
            
        engine = hlapi.SnmpEngine()
        auth_data = hlapi.UsmUserData(user, authKey=auth_key, authProtocol=hlapi.usmHMACMD5AuthProtocol)
        
        # Поддержка разных версий pysnmp v7
        if hasattr(hlapi.UdpTransportTarget, "create"):
            target = await hlapi.UdpTransportTarget.create((host, port), timeout=5, retries=2)
        else:
            target = hlapi.UdpTransportTarget((host, port), timeout=5, retries=2)
            
        result_dict = {}
        oid_items = list(oids_map.items())
        chunk_size = 5
        
        for i in range(0, len(oid_items), chunk_size):
            chunk = oid_items[i:i + chunk_size]
            var_binds_input = [hlapi.ObjectType(hlapi.ObjectIdentity(oid)) for _, oid in chunk]

            result = await getCmd(engine, auth_data, target, hlapi.ContextData(), *var_binds_input)
            error_indication, error_status, error_index, var_binds = result
            
            if error_indication:
                _LOGGER.debug("Таймаут SNMP GET (%s) для части параметров: %s", host, error_indication)
                continue
            elif error_status:
                _LOGGER.warning("Ошибка SNMP GET (%s): %s", host, error_status.prettyPrint())
                continue
                
            for vb in var_binds:
                result_dict[str(vb[0])] = vb[1].prettyPrint()
                
        return result_dict

    # Запускаем асинхронный код в изолированном цикле событий (не затрагивая ядро HA!)
    return asyncio.run(_do_fetch())


def _set_sync_isolated(host, port, user, auth_key, oid, value):
    """Синхронная функция для SET запроса в фоне с изолированным циклом."""
    
    async def _do_set():
        import pysnmp.hlapi.asyncio as hlapi
        try:
            setCmd = hlapi.setCmd
        except AttributeError:
            setCmd = hlapi.set_cmd
            
        try:
            Integer32 = hlapi.Integer32
        except AttributeError:
            from pysnmp.smi.rfc1902 import Integer32
            
        engine = hlapi.SnmpEngine()
        auth_data = hlapi.UsmUserData(user, authKey=auth_key, authProtocol=hlapi.usmHMACMD5AuthProtocol)
        
        if hasattr(hlapi.UdpTransportTarget, "create"):
            target = await hlapi.UdpTransportTarget.create((host, port), timeout=5, retries=2)
        else:
            target = hlapi.UdpTransportTarget((host, port), timeout=5, retries=2)
            
        var_bind = hlapi.ObjectType(hlapi.ObjectIdentity(oid), Integer32(value))

        result = await setCmd(engine, auth_data, target, hlapi.ContextData(), var_bind)
        error_indication, error_status, error_index, var_binds = result
        
        if error_indication or error_status:
            _LOGGER.error("Ошибка SNMP SET: %s / %s", error_indication, error_status)
            return False
        return True

    return asyncio.run(_do_set())


async def async_get_snmp_data_map(hass, host, port, user, auth_key, oids_map):
    """Безопасная точка входа для Home Assistant."""
    return await hass.async_add_executor_job(
        _fetch_sync_isolated, host, port, user, auth_key, oids_map
    )

async def async_set_snmp_data(hass, host, port, user, auth_key, oid, value):
    """Безопасная точка входа для Home Assistant."""
    return await hass.async_add_executor_job(
        _set_sync_isolated, host, port, user, auth_key, oid, value
    )
