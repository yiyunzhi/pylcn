import asyncio
import concurrent.futures
from fauxmo.plugins import FauxmoPlugin
from pypck.connection import PchkConnectionManager, LcnAddr
from pypck.lcn_defs import RelayStateModifier


class LCNControl:
    def __init__(self, **kwargs):
        pass

    def get_val(self, state):
        pass


class LCNR8Control(LCNControl):
    def __init__(self, **kwargs):
        LCNControl.__init__(self, **kwargs)
        self.offset = kwargs.get('offset', 0)
        self.onVal = RelayStateModifier.ON
        self.offVal = RelayStateModifier.OFF

    def get_val(self, state):
        _val = [RelayStateModifier.NOCHANGE] * 8
        if self.offset > 7:
            return _val
        if state == 'on':
            _val[self.offset] = self.onVal
        elif state == 'off':
            _val[self.offset] = self.offVal
        return _val


class LCNDOutputControl(LCNControl):
    def __init__(self, **kwargs):
        LCNControl.__init__(self, **kwargs)
        self.offset = kwargs.get('offset', 0)
        self.onVal = 100
        self.offVal = 0

    def get_val(self, state):
        # outputid,value(0-100),rampTime
        _val = [self.offset, self.offVal, 0]
        if self.offset > 7:
            return _val
        if state == 'on':
            _val[1] = self.onVal
        elif state == 'off':
            _val[1] = self.offVal
        return _val


class EnumLCNControlType:
    R8 = 'R8'
    D_OUTPUT = 'D_OUTPUT'


LCN_CONTROL_MAP = {EnumLCNControlType.R8: LCNR8Control,
                   EnumLCNControlType.D_OUTPUT: LCNDOutputControl}
lcn_async_calling_pool = concurrent.futures.ThreadPoolExecutor()


class LCNPlugin(FauxmoPlugin):
    def __init__(self, name, port, **kwargs):
        FauxmoPlugin.__init__(self, name=name, port=port)
        self._state = False
        self.pckClient: PchkConnectionManager = kwargs.get('pck_client')
        self.segId = kwargs.get('seg_id', 0)
        self.modId = kwargs.get('mod_id', 0)
        self.ctrlType = kwargs.get('control_type')
        _control_cls = LCN_CONTROL_MAP.get(self.ctrlType)
        if _control_cls is not None:
            self.control = _control_cls(**kwargs)
        else:
            self.control = None
        self.isGroup = kwargs.get('is_group', False)

    def set_state(self, cmd, data):
        pass

    def on(self) -> bool:
        if self.control is not None:
            _module = self.pckClient.get_address_conn(LcnAddr(self.segId, self.modId, self.isGroup))
            if self.ctrlType == EnumLCNControlType.R8:
                _ret = lcn_async_calling_pool.submit(asyncio.run, _module.control_relays(self.control.get_val('on'))).result()
            elif self.ctrlType == EnumLCNControlType.D_OUTPUT:
                _ret = lcn_async_calling_pool.submit(asyncio.run, _module.dim_output(*self.control.get_val('on'))).result()
            else:
                _ret = False
            if _ret:
                self._state = True
        return True

    def off(self) -> bool:
        if self.control is not None:
            _module = self.pckClient.get_address_conn(LcnAddr(self.segId, self.modId, self.isGroup))
            if self.ctrlType == EnumLCNControlType.R8:
                _ret = lcn_async_calling_pool.submit(asyncio.run, _module.control_relays(self.control.get_val('off'))).result()
            elif self.ctrlType == EnumLCNControlType.D_OUTPUT:
                _ret = lcn_async_calling_pool.submit(asyncio.run, _module.dim_output(*self.control.get_val('off'))).result()
            else:
                _ret = False
            if _ret:
                self._state = False
        return True

    def get_state(self) -> str:
        return 'off' if not self._state else 'on'
