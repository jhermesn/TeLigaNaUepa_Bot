import discord
from discord.ext import commands, tasks
import asyncio
import logging
from datetime import datetime

from src.config import settings
from src.core.repositories.interfaces import (
    IGuildSettingsRepository,
    IAllEditaisRepository,
    IRoleRepository,
    ILogRepository,
)
from src.infra.web_scraper.uepa_scraper import UepaScraper
from src.core.entities.edital import Edital

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
        intents = discord.Intents.default()
        intents.guilds = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)

        self.guild_repo = guild_repo
        self.all_editais_repo = all_editais_repo
        self.role_repo = role_repo
        self.log_repo = log_repo
        self.scraper = scraper
        
        # Cache para evitar acessos constantes ao DB dentro do loop
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
                logger.info(f"Cog '{cog}' carregado com sucesso.")
            except Exception as e:
                logger.error(f"Erro ao carregar o cog '{cog}': {e}", exc_info=True)

    async def on_ready(self):
        """Executado quando o bot está online e pronto."""
        logger.info(f"Bot online como {self.user.name} (ID: {self.user.id})")
        logger.info(f"Conectado a {len(self.guilds)} servidores.")
        await self.tree.sync()

    async def on_guild_join(self, guild: discord.Guild):
        """Registra o servidor quando o bot entra."""
        logger.info(f"Bot adicionado ao servidor: {guild.name} (ID: {guild.id})")
        self.guild_repo.set(str(guild.id), {"enabled": False})
        self.log_repo.add(str(guild.id), "bot_joined", f"Bot adicionado ao servidor {guild.name}")

    async def on_guild_remove(self, guild: discord.Guild):
        """Log quando o bot é removido de um servidor."""
        logger.info(f"Bot removido do servidor: {guild.name} (ID: {guild.id})")
        self.log_repo.add(str(guild.id), "bot_removed", f"Bot removido do servidor {guild.name}")

    @tasks.loop(minutes=settings.CHECK_INTERVAL_MINUTES)
    async def check_editais_task(self):
        """Tarefa periódica que verifica e posta novos editais."""
        
        if self.is_first_check:
            logger.info("Primeira verificação. Estabelecendo linha de base de editais...")
            initial_editais = await self.scraper.fetch_editais()
            if initial_editais:
                # Sempre recarrega o cache de hashes do banco
                self.known_edital_hashes = self.all_editais_repo.get_all_hashes()
                
                # Verifica quais editais são realmente novos
                new_hashes = [e.hash for e in initial_editais if e.hash not in self.known_edital_hashes]
                
                if new_hashes:
                    # Adiciona apenas editais que não estão no banco
                    new_editais_to_add = [e for e in initial_editais if e.hash in new_hashes]
                    self.all_editais_repo.add_many([e.model_dump() for e in new_editais_to_add])
                    logger.info(f"{len(new_editais_to_add)} editais novos foram registrados no banco.")
                
                # Atualiza o cache com todos os hashes do banco
                self.known_edital_hashes = self.all_editais_repo.get_all_hashes()
                logger.info(f"Cache populado com {len(self.known_edital_hashes)} hashes de editais conhecidos.")
            
            self.is_first_check = False
            logger.info("Linha de base estabelecida. O bot está monitorando novos editais.")
            return

        logger.info("Iniciando verificação periódica de editais...")
        
        scraped_editais = await self.scraper.fetch_editais()
        if not scraped_editais:
            logger.warning("Scraper não retornou editais.")
            return

        new_editais = [edital for edital in scraped_editais if edital.hash not in self.known_edital_hashes]

        if not new_editais:
            logger.info("Nenhum edital novo encontrado.")
            return
        
        logger.info(f"Encontrados {len(new_editais)} novos editais. Notificando servidores ativos...")
        
        self.all_editais_repo.add_many([e.model_dump() for e in new_editais])
        for edital in new_editais:
            self.known_edital_hashes.add(edital.hash)

        active_guilds = self.guild_repo.get_all_guilds()
        for guild_settings in active_guilds:
            if not guild_settings.get("enabled"):
                continue

            guild = self.get_guild(int(guild_settings["guild_id"]))
            channel_id = guild_settings.get("channel_id")
            
            if not guild or not channel_id:
                continue

            try:
                await self.notify_guild(guild, int(channel_id), new_editais)
            except Exception as e:
                logger.error(f"Erro ao notificar o servidor {guild.name}: {e}", exc_info=True)

    async def notify_guild(self, guild: discord.Guild, channel_id: int, new_editais: list[Edital]):
        """Envia a notificação de novos editais para um servidor."""
        channel = guild.get_channel(channel_id)
        if not channel:
            logger.warning(f"Canal {channel_id} não encontrado em {guild.name}.")
            return

        roles = self.role_repo.get_all(str(guild.id))
        mentions = " ".join(f"<@&{role['role_id']}>" for role in roles if guild.get_role(int(role["role_id"])))

        logger.info(f"Postando {len(new_editais)} novos editais em {guild.name}...")
        # Postagem do mais velho para o mais novo (reverter ordem)
        for edital in reversed(new_editais):
            embed = discord.Embed(
                title="📢 Novo Edital da UEPA",
                description=edital.title,
                url=str(edital.link),
                color=discord.Color.blue(),
                timestamp=datetime.utcnow(),
            )
            embed.add_field(name="📅 Data", value=edital.date, inline=True)
            embed.set_footer(text="Monitor de Editais UEPA")

            await channel.send(f"{mentions} Novo edital publicado!", embed=embed)
            await asyncio.sleep(1)

        self.log_repo.add(str(guild.id), "editais_posted", f"{len(new_editais)} novos editais postados.")


    @check_editais_task.before_loop
    async def before_check_editais(self):
        """Aguarda o bot estar pronto antes de iniciar a tarefa."""
        await self.wait_until_ready()