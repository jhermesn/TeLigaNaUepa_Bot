import discord
from discord import app_commands
from discord.ext import commands
import logging

from src.presentation.discord.bot import UEPABot

logger = logging.getLogger(__name__)

@app_commands.default_permissions(administrator=True)
class AdminCog(commands.Cog):
    """Cog para comandos administrativos e de depuração."""

    def __init__(self, bot: UEPABot):
        self.bot = bot

    @app_commands.command(name="verificar_agora", description="Força uma verificação de novos editais")
    async def check_now(self, interaction: discord.Interaction):
        """Força uma verificação de novos editais e reinicia a tarefa."""
        await interaction.response.defer(ephemeral=True)

        logger.info(f"Verificação manual solicitada por {interaction.user} no servidor {interaction.guild.name}")
        self.bot.check_editais_task.restart()
        self.bot.log_repo.add(str(interaction.guild_id), "manual_check", "Verificação manual forçada", str(interaction.user.id))
        
        embed = discord.Embed(
            title="✅ Verificação Forçada",
            description="A tarefa de verificação foi reiniciada. Novos editais, se houver, serão postados em breve.",
            color=discord.Color.green(),
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="limpar_historico", description="[PERIGOSO] Limpa todo o histórico de editais do bot.")
    async def clear_history(self, interaction: discord.Interaction):
        """Limpa o histórico GLOBAL de editais do bot."""
        
        class ConfirmView(discord.ui.View):
            def __init__(self, bot: UEPABot):
                super().__init__(timeout=30)
                self.bot = bot

            @discord.ui.button(label="Confirmar e Limpar TUDO", style=discord.ButtonStyle.danger)
            async def confirm(self, view_interaction: discord.Interaction, button: discord.ui.Button):
                cleared_count = self.bot.all_editais_repo.clear_all()
                self.bot.is_first_check = True 
                
                self.bot.log_repo.add(
                    None, 
                    "history_cleared", 
                    f"{cleared_count} registros removidos do histórico GLOBAL", 
                    str(interaction.user.id)
                )
                
                embed = discord.Embed(
                    title="✅ Histórico Global Limpo",
                    description=(
                        f"O histórico de **{cleared_count}** editais foi completamente apagado.\n\n"
                        "Na próxima verificação, o bot irá registrar os editais atuais sem postá-los "
                        "e só notificará sobre novos editais a partir de então."
                    ),
                    color=discord.Color.green()
                )
                await view_interaction.response.edit_message(embed=embed, view=None)
                self.stop()
        
        embed = discord.Embed(
            title="⚠️ AÇÃO DESTRUTIVA - CONFIRMAÇÃO NECESSÁRIA",
            description=(
                "Este comando apagará **TODO** o histórico de editais que o bot já viu, **PARA TODOS OS SERVIDORES**.\n\n"
                "**Efeito:** O bot irá redefinir sua base de conhecimento. Ele **não** irá repostar os editais antigos, "
                "mas irá estabelecer uma nova linha de base na próxima verificação.\n\n"
                "**Use este comando apenas se o bot estiver com comportamento inesperado ou para uma reinicialização completa.**"
            ),
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, view=ConfirmView(self.bot), ephemeral=True)


async def setup(bot: UEPABot):
    await bot.add_cog(AdminCog(bot))