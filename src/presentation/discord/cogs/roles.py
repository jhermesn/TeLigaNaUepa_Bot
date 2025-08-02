"""Cog para comandos de gerenciamento de cargos."""

import logging

import discord
from discord import app_commands
from discord.ext import commands

from dependency_injector.wiring import inject, Provide

from src.containers import Container
from src.core.repositories.interfaces import ILogRepository, IRoleRepository
from src.presentation.discord.bot import UEPABot

logger = logging.getLogger(__name__)


@app_commands.default_permissions(manage_guild=True)
class RolesCog(commands.Cog):
    """Cog para comandos de gerenciamento de cargos."""

    @inject
    def __init__(
        self,
        bot: UEPABot,
        container: Container = Provide[Container],
    ):
        """Inicializa o cog."""
        self.bot = bot
        self.role_repo: IRoleRepository = container.role_repo()
        self.log_repo: ILogRepository = container.log_repo()

    @app_commands.command(
        name="adicionar_cargo",
        description="Adiciona um cargo para ser mencionado nas notificações",
    )
    @app_commands.describe(cargo="O cargo a ser adicionado")
    async def add_role(self, interaction: discord.Interaction, cargo: discord.Role):
        """Adiciona um cargo à lista de menções."""
        guild_id = str(interaction.guild_id)

        success = self.role_repo.add(
            guild_id, str(cargo.id), cargo.name, str(interaction.user.id)
        )

        if success:
            self.log_repo.add(
                guild_id, "role_added", f"Cargo: {cargo.name}", str(interaction.user.id)
            )
            embed = discord.Embed(
                title="✅ Cargo Adicionado",
                description=f"O cargo {cargo.mention} será mencionado nas próximas notificações.",
                color=discord.Color.green(),
            )
        else:
            embed = discord.Embed(
                title="⚠️ Cargo já Existe",
                description=f"O cargo {cargo.mention} já está na lista.",
                color=discord.Color.yellow(),
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="remover_cargo", description="Remove um cargo da lista de menções"
    )
    @app_commands.describe(cargo="O cargo a ser removido")
    async def remove_role(self, interaction: discord.Interaction, cargo: discord.Role):
        """Remove um cargo da lista de menções."""
        guild_id = str(interaction.guild_id)

        success = self.role_repo.remove(guild_id, str(cargo.id))

        if success:
            self.log_repo.add(
                guild_id,
                "role_removed",
                f"Cargo: {cargo.name}",
                str(interaction.user.id),
            )
            embed = discord.Embed(
                title="✅ Cargo Removido",
                description=f"O cargo {cargo.mention} não será mais mencionado.",
                color=discord.Color.green(),
            )
        else:
            embed = discord.Embed(
                title="⚠️ Cargo não Encontrado",
                description=f"O cargo {cargo.mention} não estava na lista de menções.",
                color=discord.Color.yellow(),
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="listar_cargos", description="Lista todos os cargos configurados para menção"
    )
    async def list_roles(self, interaction: discord.Interaction):
        """Lista os cargos configurados para menção."""
        if not interaction.guild:
            await interaction.response.send_message("Este comando só pode ser usado em um servidor.", ephemeral=True)
            return

        guild_id = str(interaction.guild_id)
        roles = self.role_repo.get_all(guild_id)

        embed = discord.Embed(
            title="👥 Cargos Configurados para Menção", color=discord.Color.blue()
        )

        if not roles:
            embed.description = "Nenhum cargo configurado. Use `/adicionar_cargo`."
        else:
            lines = []
            for r in roles:
                role = interaction.guild.get_role(int(r.role_id))
                lines.append(
                    f"• {role.mention}"
                    if role
                    else f"• ~~{r.role_name}~~ (cargo removido)"
                )
            embed.description = "\n".join(lines)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="limpar_cargos", description="Remove TODOS os cargos da lista de menções"
    )
    async def clear_roles(self, interaction: discord.Interaction):
        """Remove todos os cargos da lista de menções."""
        if not interaction.guild:
            await interaction.response.send_message("Este comando só pode ser usado em um servidor.", ephemeral=True)
            return

        guild_id = str(interaction.guild_id)

        class ConfirmView(discord.ui.View):
            """View para confirmar a remoção de todos os cargos."""
            @inject
            def __init__(
                self,
                container: Container = Provide[Container],
            ):
                """Inicializa a view."""
                super().__init__(timeout=30)
                self.role_repo: IRoleRepository = container.role_repo()
                self.log_repo: ILogRepository = container.log_repo()

            @discord.ui.button(
                label="Confirmar e Limpar", style=discord.ButtonStyle.danger
            )
            async def confirm(
                self, view_interaction: discord.Interaction, button: discord.ui.Button
            ):
                """Confirma a remoção de todos os cargos."""
                button.disabled = True
                cleared_count = self.role_repo.clear(guild_id)
                self.log_repo.add(
                    guild_id,
                    "roles_cleared",
                    f"{cleared_count} cargos removidos",
                    str(interaction.user.id),
                )

                embed = discord.Embed(
                    title="✅ Cargos Removidos",
                    description=f"Todos os {cleared_count} cargos foram removidos com sucesso.",
                    color=discord.Color.green(),
                )
                await view_interaction.response.edit_message(embed=embed, view=None)
                self.stop()

        embed = discord.Embed(
            title="⚠️ Confirmação Necessária",
            description="Isso removerá **TODOS** os cargos da lista de menções. Deseja continuar?",
            color=discord.Color.yellow(),
        )
        await interaction.response.send_message(
            embed=embed, view=ConfirmView(), ephemeral=True
        )


async def setup(bot: UEPABot):
    """Configura o cog de gerenciamento de cargos."""
    await bot.add_cog(RolesCog(bot))
