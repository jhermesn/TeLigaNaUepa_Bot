"""Cog para comandos informativos e de ajuda."""
import logging
import discord
from discord import app_commands, TextChannel
from discord.ext import commands

from src.core.repositories.interfaces import (
    IAllEditaisRepository,
    IGuildSettingsRepository,
    IRoleRepository,
)
from src.infra.web_scraper.uepa_scraper import UepaScraper
from src.presentation.discord.bot import UEPABot
from src.config import settings

logger = logging.getLogger(__name__)


class InfoCog(commands.Cog):
    """Cog para comandos informativos e de ajuda."""

    def __init__(
        self,
        bot: UEPABot,
        guild_repo: IGuildSettingsRepository,
        role_repo: IRoleRepository,
        all_editais_repo: IAllEditaisRepository,
        scraper: UepaScraper,
    ):
        """Inicializa o cog."""
        self.bot = bot
        self.guild_repo = guild_repo
        self.role_repo = role_repo
        self.all_editais_repo = all_editais_repo
        self.scraper = scraper

    @app_commands.command(name="status", description="Verifica o status atual do bot")
    async def status(self, interaction: discord.Interaction):
        """Mostra o status do bot e suas configurações para o servidor."""
        guild_id = str(interaction.guild_id)
        guild_settings = self.guild_repo.get(guild_id)

        embed = discord.Embed(
            title="📊 Status do Monitor de Editais UEPA", color=discord.Color.blue()
        )

        if not guild_settings or not guild_settings.channel_id:
            embed.description = "⚠️ O bot ainda não foi configurado neste servidor."
            embed.add_field(
                name="💡 Próximo Passo", value="Use `/configurar` para iniciar.", inline=False
            )
        else:
            status_text = "✅ Ativo" if guild_settings.enabled else "⏸️ Pausado"
            channel = self.bot.get_channel(int(guild_settings.channel_id))
            channel_mention = "Canal não encontrado"
            if isinstance(channel, TextChannel):
                channel_mention = channel.mention
                         
            roles = self.role_repo.get_all(guild_id)
            roles_text = (
                "\n".join(f"<@&{r.role_id}>" for r in roles) if roles else "Nenhum"
            )

            embed.add_field(name="Status neste Servidor", value=status_text, inline=True)
            embed.add_field(
                name="Canal de Notificações", value=channel_mention, inline=True
            )
            embed.add_field(
                name="Total de Editais Vistos",
                value=str(self.all_editais_repo.count_all()),
                inline=True,
            )
            embed.add_field(
                name=f"Cargos a Mencionar ({len(roles)})",
                value=roles_text,
                inline=False,
            )

        embed.set_footer(
            text=f"Verificação global a cada {settings.CHECK_INTERVAL_MINUTES} minutos."
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="listar_editais",
        description="Lista os últimos 10 editais encontrados no site da UEPA",
    )
    async def list_editais(self, interaction: discord.Interaction):
        """Lista os últimos editais encontrados no site da UEPA."""
        await interaction.response.defer(ephemeral=True)

        editais = await self.scraper.fetch_editais()

        if not editais:
            await interaction.followup.send(
                "❌ Não foi possível buscar os editais no momento."
            )
            return

        embed = discord.Embed(
            title="📋 Últimos 10 Editais da UEPA",
            description="Lista dos editais mais recentes disponíveis no site.",
            color=discord.Color.blue(),
        )

        for edital in editais[:10]:
            embed.add_field(
                name=f"📄 {edital.title[:200]}",
                value=f"📅 {edital.date} - [Acessar]({edital.link})",
                inline=False,
            )

        embed.set_footer(
            text=f"Mostrando {len(editais[:10])} de {len(editais)} editais encontrados."
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="ajuda", description="Mostra a mensagem de ajuda com todos os comandos"
    )
    async def help(self, interaction: discord.Interaction):
        """Mostra uma mensagem de ajuda com os comandos do bot."""
        embed = discord.Embed(
            title="📚 Ajuda - Monitor de Editais UEPA",
            description="Eu monitoro e notifico sobre novos editais da UEPA. Aqui estão meus comandos:",
            color=discord.Color.dark_blue(),
        )

        config_cmds = """
        `/configurar` - Define o canal para receber as notificações.
        `/pausar` - Pausa o envio de novas notificações.
        `/retomar` - Retoma o envio de notificações.
        """

        roles_cmds = """
        `/adicionar_cargo` - Adiciona um cargo para ser mencionado.
        `/remover_cargo` - Remove um cargo da lista.
        `/listar_cargos` - Lista todos os cargos configurados.
        `/limpar_cargos` - Remove todos os cargos da lista.
        """

        general_cmds = """
        `/status` - Mostra o status e configurações atuais.
        `/listar_editais` - Lista os últimos editais do site da UEPA.
        `/verificar_agora` - Força uma nova verificação de editais.
        `/limpar_historico` - [PERIGOSO] Reseta a base de dados de editais do bot.
        `/ajuda` - Mostra esta mensagem.
        """

        embed.add_field(
            name="⚙️ Comandos de Configuração", value=config_cmds, inline=False
        )
        embed.add_field(name="👥 Comandos de Cargos", value=roles_cmds, inline=False)
        embed.add_field(name="📋 Comandos Gerais", value=general_cmds, inline=False)
        embed.set_footer(text="Bot desenvolvido para a comunidade da UEPA.")

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: UEPABot):
    """Configura o cog de informações."""
    if not bot.container:
        logger.error("Container do bot não foi inicializado.")
        return

    cog = InfoCog(
        bot=bot,
        guild_repo=bot.container.guild_settings_repo(),
        role_repo=bot.container.role_repo(),
        all_editais_repo=bot.container.all_editais_repo(),
        scraper=bot.container.uepa_scraper(),
    )
    await bot.add_cog(cog)
