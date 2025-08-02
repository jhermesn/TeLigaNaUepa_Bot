"""Classe principal do bot, herda de commands.Bot do discord.py."""

import asyncio
import logging
from datetime import datetime, timezone

import discord
from discord.ext import commands, tasks

from src.config import settings
from src.core.entities.edital import Edital
from src.core.repositories.interfaces import (
    IAllEditaisRepository,
    IGuildSettingsRepository,
    ILogRepository,
    IRoleRepository,
)
from src.infra.web_scraper.uepa_scraper import UepaScraper

logger = logging.getLogger(__name__)


class UEPABot(commands.Bot):
    """Classe principal do bot, herda de commands.Bot do discord.py."""

    def __init__(
        self,
        guild_repo: IGuildSettingsRepository,
        all_editais_repo: IAllEditaisRepository,
        role_repo: IRoleRepository,
        log_repo: ILogRepository,
        scraper: UepaScraper,
    ):
        """Inicializa o bot."""
        intents = discord.Intents.default()
        intents.guilds = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)

        self.guild_repo = guild_repo
        self.all_editais_repo = all_editais_repo
        self.role_repo = role_repo
        self.log_repo = log_repo
        self.scraper = scraper

        self.known_edital_hashes: set = set()
        self.is_first_check = True

    async def setup_hook(self):
        """Executado quando o bot é configurado."""
        logger.info("Iniciando setup do bot...")
        await self.load_cogs()
        self.check_editais_task.start()
        logger.info("Bot configurado e tarefas iniciadas.")

    async def load_cogs(self):
        """Carrega os cogs da aplicação."""
        cogs = [
            "src.presentation.discord.cogs.info",
            "src.presentation.discord.cogs.config",
            "src.presentation.discord.cogs.roles",
            "src.presentation.discord.cogs.admin",
        ]
        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info("Cog '%s' carregado com sucesso.", cog)
            except commands.ExtensionError as e:
                logger.error("Erro ao carregar o cog '%s': %s", cog, e, exc_info=True)

    async def on_ready(self):
        """Executado quando o bot está online e pronto."""
        if self.user:
            logger.info("Bot online como %s (ID: %s)", self.user.name, self.user.id)
        logger.info("Conectado a %d servidores.", len(self.guilds))
        await self.tree.sync()

    async def on_guild_join(self, guild: discord.Guild):
        """Registra o servidor quando o bot entra."""
        logger.info("Bot adicionado ao servidor: %s (ID: %s)", guild.name, guild.id)
        self.guild_repo.set(str(guild.id), {"enabled": False})
        self.log_repo.add(
            str(guild.id), "bot_joined", "Bot adicionado ao servidor " + guild.name
        )

    async def on_guild_remove(self, guild: discord.Guild):
        """Log quando o bot é removido de um servidor."""
        logger.info("Bot removido do servidor: %s (ID: %s)", guild.name, guild.id)
        self.log_repo.add(
            str(guild.id), "bot_removed", "Bot removido do servidor " + guild.name
        )

    @tasks.loop(minutes=settings.CHECK_INTERVAL_MINUTES)
    async def check_editais_task(self):
        """Tarefa periódica que verifica e posta novos editais."""

        if self.is_first_check:
            logger.info(
                "Primeira verificação. Estabelecendo linha de base de editais..."
            )
            initial_editais = await self.scraper.fetch_editais()
            if initial_editais:
                self.known_edital_hashes = self.all_editais_repo.get_all_hashes()

                new_editais_to_add = [
                    e
                    for e in initial_editais
                    if e.hash not in self.known_edital_hashes
                ]

                if new_editais_to_add:
                    self.all_editais_repo.add_many(new_editais_to_add)
                    logger.info(
                        "%d editais novos foram registrados no banco.",
                        len(new_editais_to_add),
                    )

                self.known_edital_hashes = self.all_editais_repo.get_all_hashes()
                logger.info(
                    "Cache populado com %d hashes de editais conhecidos.",
                    len(self.known_edital_hashes),
                )

            self.is_first_check = False
            logger.info(
                "Linha de base estabelecida. O bot está monitorando novos editais."
            )
            return

        logger.info("Iniciando verificação periódica de editais...")

        scraped_editais = await self.scraper.fetch_editais()
        if not scraped_editais:
            logger.warning("Scraper não retornou editais.")
            return

        new_editais = [
            edital
            for edital in scraped_editais
            if edital.hash not in self.known_edital_hashes
        ]

        if not new_editais:
            logger.info("Nenhum edital novo encontrado.")
            return

        logger.info(
            "Encontrados %d novos editais. Notificando servidores ativos...",
            len(new_editais),
        )

        self.all_editais_repo.add_many(new_editais)
        for edital in new_editais:
            self.known_edital_hashes.add(edital.hash)

        active_guilds = self.guild_repo.get_all_guilds()
        for guild_settings in active_guilds:
            if not guild_settings.enabled:
                continue

            guild = self.get_guild(int(guild_settings.guild_id))
            channel_id = guild_settings.channel_id

            if not guild or not channel_id:
                continue

            try:
                await self.notify_guild(guild, int(channel_id), new_editais)
            except (discord.Forbidden, discord.HTTPException) as e:
                logger.error(
                    "Erro ao notificar o servidor %s: %s", guild.name, e, exc_info=True
                )

    async def notify_guild(
        self, guild: discord.Guild, channel_id: int, new_editais: list[Edital]
    ):
        """Envia a notificação de novos editais para um servidor."""
        channel = guild.get_channel(channel_id)
        if not channel or not isinstance(channel, (discord.TextChannel, discord.Thread)):
            logger.warning(
                "Canal %s não é um canal de texto ou thread em %s.",
                channel_id,
                guild.name,
            )
            return

        roles = self.role_repo.get_all(str(guild.id))
        mentions = " ".join(
            f"<@&{role.role_id}>"
            for role in roles
            if guild.get_role(int(role.role_id))
        )

        logger.info(
            "Postando %d novos editais em %s...", len(new_editais), guild.name
        )
        for edital in reversed(new_editais):
            embed = discord.Embed(
                title="📢 Novo Edital da UEPA",
                description=edital.title,
                url=str(edital.link),
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(name="📅 Data", value=edital.date, inline=True)
            embed.set_footer(text="Monitor de Editais UEPA")

            await channel.send(f"{mentions} Novo edital publicado!", embed=embed)
            await asyncio.sleep(1)

        self.log_repo.add(
            str(guild.id),
            "editais_posted",
            str(len(new_editais)) + " novos editais postados.",
        )

    @check_editais_task.before_loop
    async def before_check_editais(self):
        """Aguarda o bot estar pronto antes de iniciar a tarefa."""
        await self.wait_until_ready()
