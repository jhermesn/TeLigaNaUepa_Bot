import discord
from discord import app_commands
from discord.ext import commands
import logging

from src.presentation.discord.bot import UEPABot

logger = logging.getLogger(__name__)

@app_commands.default_permissions(administrator=True)
class ConfigCog(commands.Cog):
    """Cog para comandos de configuração do bot."""

    def __init__(self, bot: UEPABot):
        self.bot = bot

    @app_commands.command(name="configurar", description="Configura o canal para notificações de editais")
    @app_commands.describe(canal="Canal onde os editais serão postados")
    async def configure(self, interaction: discord.Interaction, canal: discord.TextChannel):
        """Configura o canal de notificações e ativa o bot."""
        guild_id = str(interaction.guild_id)
        
        self.bot.guild_repo.set(
            guild_id,
            {"channel_id": str(canal.id), "enabled": True},
        )
        self.bot.log_repo.add(guild_id, "configured", f"Canal: {canal.name}", str(interaction.user.id))

        embed = discord.Embed(
            title="✅ Bot Configurado com Sucesso!",
            description=f"As notificações de editais serão enviadas em {canal.mention}.",
            color=discord.Color.green(),
        )
        embed.add_field(name="💡 Próximo Passo", value="Use `/adicionar_cargo` para que eu possa mencionar os cargos desejados.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="pausar", description="Pausa as notificações de editais")
    async def pause(self, interaction: discord.Interaction):
        """Pausa as notificações no servidor."""
        guild_id = str(interaction.guild_id)
        self.bot.guild_repo.set(guild_id, {"enabled": False})
        self.bot.log_repo.add(guild_id, "paused", user_id=str(interaction.user.id))
        await interaction.response.send_message("⏸️ Notificações pausadas.", ephemeral=True)

    @app_commands.command(name="retomar", description="Retoma as notificações de editais")
    async def resume(self, interaction: discord.Interaction):
        """Retoma as notificações no servidor."""
        guild_id = str(interaction.guild_id)
        settings = self.bot.guild_repo.get(guild_id)
        if not settings or not settings.get("channel_id"):
            await interaction.response.send_message("❌ O bot precisa ser configurado primeiro com `/configurar`.", ephemeral=True)
            return

        self.bot.guild_repo.set(guild_id, {"enabled": True})
        self.bot.log_repo.add(guild_id, "resumed", user_id=str(interaction.user.id))
        await interaction.response.send_message("▶️ Notificações retomadas.", ephemeral=True)


async def setup(bot: UEPABot):
    await bot.add_cog(ConfigCog(bot))