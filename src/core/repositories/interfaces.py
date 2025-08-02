"""Interfaces para os repositórios."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Set

from src.core.entities.edital import Edital


class IAllEditaisRepository(ABC):
    """Interface para o repositório global de editais vistos."""

    @abstractmethod
    def get_all_hashes(self) -> Set[str]:
        """Retorna um conjunto com todos os hashes de editais já vistos."""

    @abstractmethod
    def add_many(self, editais: List[Edital]) -> bool:
        """Adiciona múltiplos editais ao repositório."""

    @abstractmethod
    def is_empty(self) -> bool:
        """Verifica se o repositório de editais está vazio."""

    @abstractmethod
    def clear_all(self) -> int:
        """Limpa completamente o repositório de editais."""

    @abstractmethod
    def count_all(self) -> int:
        """Conta o total de editais vistos."""


class IRoleRepository(ABC):
    """Interface para o repositório de cargos a serem mencionados."""

    @abstractmethod
    def add(self, guild_id: str, role_id: str, role_name: str, added_by: str) -> bool:
        """Adiciona um cargo."""

    @abstractmethod
    def remove(self, guild_id: str, role_id: str) -> bool:
        """Remove um cargo."""

    @abstractmethod
    def get_all(self, guild_id: str) -> List[Any]:
        """Retorna todos os cargos de um servidor."""

    @abstractmethod
    def clear(self, guild_id: str) -> int:
        """Remove todos os cargos de um servidor."""


class IGuildSettingsRepository(ABC):
    """Interface para o repositório de configurações do servidor."""

    @abstractmethod
    def get(self, guild_id: str) -> Optional[Any]:
        """Obtém as configurações de um servidor."""

    @abstractmethod
    def set(self, guild_id: str, settings: Dict[str, Any]) -> None:
        """Define as configurações de um servidor."""

    @abstractmethod
    def get_all_guilds(self) -> List[Any]:
        """Retorna as configurações de todos os servidores."""


class ILogRepository(ABC):
    """Interface para o repositório de logs."""

    @abstractmethod
    def add(
        self,
        guild_id: Optional[str],
        action: str,
        details: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """Adiciona uma entrada de log."""