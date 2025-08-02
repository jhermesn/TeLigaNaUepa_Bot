#!/usr/bin/env python
"""Ponto de entrada principal para iniciar o bot."""
import asyncio

from src.application import Application


def main():
    """Inicia a aplicação."""
    app = Application()
    asyncio.run(app.start())


if __name__ == "__main__":
    main()
