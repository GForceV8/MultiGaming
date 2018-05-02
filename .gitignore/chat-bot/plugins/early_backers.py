from plugin import Plugin
import discord
import asyncio
import logging

log = logging.getLogger('discord')

class EarlyBackers(Plugin):

    is_global = True
    multigaming_server_id = "159962941502783488"
    roles = [
        'Admin',
        'Support',
        'Contributors',
        'Early Backers'
    ]

    async def update_early_backers(self):
        server = discord.utils.find(lambda s: s.id==self.multigaming_server_id,
                                    self.multigaming.servers)
        if not server:
            return

        early_backers = (member.id for member in server.members
                         if any(map(lambda r: r.name in self.roles, member.roles)))

        await self.multigaming.db.redis.delete('early_backers')
        for backer in early_backers:
            await self.multigaming.db.redis.sadd('early_backers', backer)

    async def on_ready(self):
        while True:
            try:
                await self.update_early_backers()
            except Exception:
                log.info("An error occured in the Early Backers plugin")
            await asyncio.sleep(10)
