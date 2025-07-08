import aiohttp
from bs4 import BeautifulSoup
import hashlib
from typing import List
import logging

from src.core.entities.edital import Edital
from src.config import settings

logger = logging.getLogger(__name__)


class UepaScraper:
    """Responsável por buscar e processar editais do site da UEPA."""

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.url = settings.UEPA_EDITAIS_URL

    def _generate_edital_hash(self, title: str, link: str) -> str:
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
            logger.error(f"Erro de HTTP ao acessar o site da UEPA: {e}")
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar editais: {e}")
        return []

    def _parse_html(self, html: str) -> List[Edital]:
        """Extrai informações dos editais do HTML."""
        soup = BeautifulSoup(html, "lxml")
        editais = []
        
        # Seletores atualizados baseados na estrutura atual do site da UEPA
        selectors = [
            ".views-field-title a",
            ".field-content a", 
            "a[href*='edital']",
        ]

        links = []
        for selector in selectors:
            links = soup.select(selector)
            if links:
                logger.info(f"Encontrados {len(links)} links com seletor: {selector}")
                break

        # Filtrar apenas links que são realmente editais
        edital_links = []
        for link in links:
            href = link.get("href", "")
            text = link.get_text(strip=True)
            if href and ("edital" in href.lower() or "edital" in text.lower()):
                edital_links.append(link)

        for link_elem in edital_links[:20]:  # Limita aos 20 mais recentes
            title = link_elem.get_text(strip=True)
            link = link_elem.get("href")

            if not link.startswith("http"):
                link = f"https://www.uepa.br{link}"

            # Para editais em PDF, geralmente não há data na página de listagem
            # Vamos tentar extrair do contexto ou usar "Data não disponível"
            date_elem = None
            parent = link_elem.parent
            while parent and not date_elem:
                date_elem = parent.select_one(".date, .field-date, time, .views-field-created")
                parent = parent.parent
            
            date = date_elem.get_text(strip=True) if date_elem else "Data não disponível"
            
            if title and link:
                edital_hash = self._generate_edital_hash(title, link)
                try:
                    editais.append(
                        Edital(
                            title=title,
                            link=link,
                            date=date,
                            hash=edital_hash
                        )
                    )
                except Exception as e:
                    logger.warning(f"Erro ao validar dados do edital '{title}': {e}")

        logger.info(f"Total de {len(editais)} editais parseados com sucesso.")
        return editais 