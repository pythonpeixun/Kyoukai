"""
Asphalt framework mixin for Kyokai.
"""
import logging

import asyncio
from functools import partial
from typing import Union

from asphalt.core import Component, resolve_reference, Context
from typeguard import check_argument_types

from kyokai.app import Kyokai
from kyokai.protocol import KyokaiProtocol
from kyokai.context import HTTPRequestContext

logger = logging.getLogger("Kyokai")


class KyoukaiComponent(Component):
    def __init__(self, app: Union[str, Kyokai], ip: str = '0.0.0.0', port: int = 4444, **cfg):
        assert check_argument_types()
        if not isinstance(app, Kyokai):
            self.app = resolve_reference(app)
        else:
            self.app = app
        self.ip = ip
        self.port = port
        self._extra_cfg = cfg

        # Set HTTPRequestContext's `cfg` val to the extra config.
        HTTPRequestContext.cfg = self._extra_cfg

        self.server = None

        self.app.reconfigure(cfg)

    def get_protocol(self, ctx: Context):
        return KyokaiProtocol(self.app, ctx)

    async def start(self, ctx: Context):
        """
        Starts a Kyokai server.
        """
        protocol = partial(self.get_protocol, ctx)
        self.server = await asyncio.get_event_loop().create_server(protocol, self.ip, self.port)
        logger.info("Kyokai serving on {}:{}.".format(self.ip, self.port))