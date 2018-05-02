import logging
import aioredis
from plugin import Plugin

log = logging.getLogger('discord')

class PluginManager:

    def __init__(self, multigaming):
        self.multigaming = multigaming
        self.db = multigaming.db
        self.multigaming.plugins = []

    def load(self, plugin):
        log.info('Loading plugin {}.'.format(plugin.__name__))
        plugin_instance = plugin(self.multigaming)
        self.multigaming.plugins.append(plugin_instance)
        log.info('Plugin {} loaded.'.format(plugin.__name__))

    def load_all(self):
        for plugin in Plugin.plugins:
            self.load(plugin)

    async def get_all(self, server):
        try:
            plugin_names = await self.db.redis.smembers('plugins:{}'.format(server.id))
            plugins = []
            for plugin in self.multigaming.plugins:
                if plugin.is_global:
                    plugins.append(plugin)
                if plugin.__class__.__name__ in plugin_names:
                    if hasattr(plugin, 'buff_name'):
                        buff_ok = await self.db.redis.get('buffs:{}:{}'.format(server.id,
                                                                               plugin.buff_name))
                        if not buff_ok:
                            continue

                    plugins.append(plugin)
            return plugins
        except aioredis.errors.ConnectionClosedError as e:
            await self.db.create()
            return await self.get_all(server)
