"""Implementação do scraper para o site da UEPA."""

import hashlib
import logging
import re
from typing import List

import aiohttp
from bs4 import BeautifulSoup
from pydantic import ValidationError, HttpUrl


from src.config import settings
from src.core.entities.edital import Edital

logger = logging.getLogger(__name__)


class UepaScraper:
    """Responsável por buscar e processar editais do site da UEPA."""

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.url = settings.UEPA_EDITAIS_URL

    @staticmethod
    def _generate_edital_hash(title: str, link: str) -> str:
        """Gera um hash MD5 para um edital a partir do título e link."""
        content = f"{title}:{link}"
        return hashlib.md5(content.encode()).hexdigest()

    async def fetch_editais(self) -> List[Edital]:
        """
        Busca os editais mais recentes do site da UEPA.

        Returns:
            Uma lista de objetos Edital.
        """
        try:
            async with self.session.get(self.url) as response:
                response.raise_for_status()
                html = await response.text()
                return self._parse_html(html)
        except aiohttp.ClientError as e:
            logger.error("Erro de HTTP ao acessar o site da UEPA: %s", e)
        except IOError as e:
            logger.error("Erro inesperado ao buscar editais: %s", e)
        return []

    def _parse_html(self, html: str) -> List[Edital]:
        """Extrai informações dos editais do HTML."""
        soup = BeautifulSoup(html, "lxml")
        editais = []

        accordion_buttons = soup.select("button.accordion-button")

        for button in accordion_buttons:
            title = button.get_text(strip=True)

            target_id_attr = button.get("data-bs-target")
            if not target_id_attr:
                continue

            target_id = target_id_attr
            if isinstance(target_id_attr, list):
                target_id = target_id_attr[0] if target_id_attr else None

            if not target_id or not isinstance(target_id, str):
                continue

            body = soup.select_one(target_id)
            if not body:
                continue

            link_elem = body.select_one("a[href*='/sites/default/files/editais/']")
            link = None
            if link_elem:
                href = link_elem.get("href")
                if isinstance(href, list):
                    link = href[0] if href else None
                else:
                    link = str(href) if href else None

            if not link:
                match = re.search(r'Edital\s*(\d+)-(\d{4})', title, re.IGNORECASE)
                if match:
                    number, year = match.groups()
                    link = f"https://www.uepa.br/sites/default/files/editais/edital{number}{year}.pdf"

            if not link:
                logger.warning("Não foi possível encontrar ou construir o link para o edital: %s", title)
                continue

            if not link.startswith("http"):
                link = f"https://www.uepa.br{link}"

            date = "Data não disponível"
            date_elem = body.find(string=re.compile(r'Belém, \d+ de \w+ de \d{4}'))
            if date_elem:
                date = str(date_elem).strip()

            if title and link:
                edital_hash = self._generate_edital_hash(title, link)
                try:
                    editais.append(
                        Edital(
                            title=title,
                            link=HttpUrl(link),
                            date=date,
                            hash=edital_hash
                        )
                    )
                except ValidationError as e:
                    logger.warning("Erro ao validar dados do edital '%s': %s", title, e)

        if not editais:
            logger.warning("Nenhum edital encontrado com a estrutura de accordion. A estrutura do site pode ter mudado ou requer JavaScript.")

        logger.info("Total de %s editais parseados com sucesso.", len(editais))
        return editais[:20]
