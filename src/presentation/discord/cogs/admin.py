"""Cog para comandos administrativos e de depuração."""

import logging
import discord

from dependency_injector.wiring import inject, Provide
from discord import app_commands
from discord.ext import commands

from src.containers import Container
from src.core.repositories.interfaces import IAllEditaisRepository, ILogRepository
from src.presentation.discord.bot import UEPABot

logger = logging.getLogger(__name__)


@app_commands.default_permissions(administrator=True)
class AdminCog(commands.Cog):
    """Cog para comandos administrativos e de depuração."""

    def __init__(
        self,
        bot: UEPABot,
        all_editais_repo: IAllEditaisRepository,
        log_repo: ILogRepository,
    ):
        self.bot = bot
        self.all_editais_repo = all_editais_repo
        self.log_repo = log_repo

    @app_commands.command(
        name="verificar_agora", description="Força uma verificação de novos editais"
    )
    async def check_now(self, interaction: discord.Interaction):
        """Força uma verificação de novos editais e reinicia a tarefa."""
        await interaction.response.defer(ephemeral=True)

        guild_name = interaction.guild.name if interaction.guild else "DM"
        logger.info(
            "Verificação manual solicitada por %s no servidor %s",
            interaction.user,
            guild_name,
        )
        self.bot.check_editais_task.restart()
        self.log_repo.add(
            str(interaction.guild_id),
            "manual_check",
            "Verificação manual forçada",
            str(interaction.user.id),
        )

        embed = discord.Embed(
            title="✅ Verificação Forçada",
            description="A tarefa de verificação foi reiniciada. Novos editais, se houver, serão postados em breve.",
            color=discord.Color.green(),
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="limpar_historico",
        description="[PERIGOSO] Limpa todo o histórico de editais do bot.",
    )
    async def clear_history(self, interaction: discord.Interaction):
        """Limpa o histórico GLOBAL de editais do bot."""

        class ConfirmView(discord.ui.View):
            """View para confirmar a limpeza do histórico global."""

            @inject
            def __init__(
                self,
                all_editais_repo: IAllEditaisRepository = Provide[
                    Container.all_editais_repo
                ],
                log_repo: ILogRepository = Provide[Container.log_repo],
                bot: UEPABot = Provide[Container.bot],
            ):
                """Inicializa a view."""
                super().__init__(timeout=30)
                self.all_editais_repo = all_editais_repo
                self.log_repo = log_repo
                self.bot = bot

            @discord.ui.button(
                label="Confirmar e Limpar TUDO", style=discord.ButtonStyle.danger
            )
            async def confirm(self, view_interaction: discord.Interaction, button: discord.ui.Button):
                """Confirma a limpeza do histórico global."""
                button.disabled = True
                cleared_count = self.all_editais_repo.clear_all()
                self.bot.is_first_check = True

                self.log_repo.add(
                    None,
                    "history_cleared",
                    f"{cleared_count} registros removidos do histórico GLOBAL",
                    str(interaction.user.id),
                )

                embed = discord.Embed(
                    title="✅ Histórico Global Limpo",
                    description=(
                        f"O histórico de **{cleared_count}** editais foi completamente apagado.\n\n"
                        "Na próxima verificação, o bot irá registrar os editais atuais sem postá-los "
                        "e só notificará sobre novos editais a partir de então."
                    ),
                    color=discord.Color.green(),
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
            color=discord.Color.red(),
        )
        await interaction.response.send_message(
            embed=embed, view=ConfirmView(), ephemeral=True
        )


async def setup(bot: UEPABot):
    """Configura o cog de administração."""
    if not bot.container:
        logger.error("Container do bot não foi inicializado.")
        return

    cog = AdminCog(
        bot=bot,
        all_editais_repo=bot.container.all_editais_repo(),
        log_repo=bot.container.log_repo(),
    )
    await bot.add_cog(cog)
