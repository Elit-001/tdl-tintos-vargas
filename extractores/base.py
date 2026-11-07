"""Clase base ExtractorEtico y registro de fiabilidad para AgroPulse TDL.

Cumple los criterios de Ingeniería de Datos (extracción ética con verificación
de robots.txt, User-Agent académico, pausa y backoff exponencial) y de Calidad
en SI (bitácora automática para cálculo de MTBF, MTTR y Disponibilidad).
"""

import csv
import time
from pathlib import Path
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import requests

from config import (
    COLUMNAS_BITACORA,
    MAX_REINTENTOS_HTTP,
    PAUSA_MINIMA_SEGUNDOS,
    RUTA_BITACORA,
    TIMEOUT_HTTP_SEGUNDOS,
    USER_AGENT_ACADEMICO,
)


class ExtractorEtico:
    """Cliente HTTP ético que respeta robots.txt, pausas de cortesía y reintentos."""

    def __init__(
        self,
        url_base: str,
        user_agent: str = USER_AGENT_ACADEMICO,
        pausa_minima: float = PAUSA_MINIMA_SEGUNDOS,
    ) -> None:
        """Inicializa sesión HTTP con User-Agent académico y carga robots.txt."""
        self.url_base: str = url_base.rstrip("/")
        self.user_agent: str = user_agent
        self.pausa_minima: float = pausa_minima
        self.pausa_efectiva: float = pausa_minima
        self.robots_disponible: bool = False
        self.sesion: requests.Session = requests.Session()
        self.sesion.headers.update({"User-Agent": self.user_agent})
        self.parser_robots: RobotFileParser = RobotFileParser()
        self._cargar_robots()

    def _cargar_robots(self) -> None:
        """Descarga y analiza el archivo robots.txt del dominio objetivo."""
        url_robots = urljoin(f"{self.url_base}/", "robots.txt")
        self.parser_robots.set_url(url_robots)
        try:
            respuesta = self.sesion.get(url_robots, timeout=TIMEOUT_HTTP_SEGUNDOS)
            if respuesta.status_code == 200:
                self.parser_robots.parse(respuesta.text.splitlines())
                self.robots_disponible = True
                demora_sitio = self.parser_robots.crawl_delay(self.user_agent)
                if demora_sitio is not None:
                    self.pausa_efectiva = max(self.pausa_minima, float(demora_sitio))
        except requests.RequestException:
            # Si el servidor gubernamental no responde a robots.txt, operamos en modo conservador
            self.robots_disponible = False

    def puede_extraer(self, url: str) -> bool:
        """Verifica en robots.txt si el User-Agent académico tiene permiso para la URL."""
        if not self.robots_disponible:
            return True
        return self.parser_robots.can_fetch(self.user_agent, url)

    def obtener_pagina(
        self,
        url: str,
        parametros: dict[str, str] | None = None,
        max_reintentos: int = MAX_REINTENTOS_HTTP,
    ) -> requests.Response:
        """Realiza una petición GET ética con pausa obligatoria y espera exponencial."""
        if not self.puede_extraer(url):
            raise PermissionError(f"Acceso prohibido por robots.txt para la URL: {url}")

        ultimo_error: Exception | None = None
        for intento in range(1, max_reintentos + 1):
            time.sleep(self.pausa_efectiva)
            try:
                respuesta = self.sesion.get(
                    url, params=parametros, timeout=TIMEOUT_HTTP_SEGUNDOS
                )
                respuesta.raise_for_status()
                return respuesta
            except requests.RequestException as error:
                ultimo_error = error
                if intento < max_reintentos:
                    espera_exponencial = self.pausa_efectiva * (2 ** (intento - 1))
                    time.sleep(espera_exponencial)

        raise ConnectionError(
            f"Fallo tras {max_reintentos} intentos en {url}: {ultimo_error}"
        )


def registrar_ejecucion_bitacora(
    timestamp_inicio: str,
    timestamp_fin: str,
    fuente: str,
    estado: str,
    registros_obtenidos: int,
    tiempo_segundos: float,
    mensaje_error: str = "",
    ruta_bitacora: Path = RUTA_BITACORA,
) -> None:
    """Agrega un registro de ejecución en calidad/bitacora_captura.csv para MTBF/MTTR."""
    ruta_bitacora.parent.mkdir(parents=True, exist_ok=True)
    nuevo = not ruta_bitacora.exists() or ruta_bitacora.stat().st_size == 0
    fila = {
        "timestamp_inicio": timestamp_inicio,
        "timestamp_fin": timestamp_fin,
        "fuente": fuente,
        "estado": estado,
        "registros_obtenidos": registros_obtenidos,
        "tiempo_segundos": round(tiempo_segundos, 3),
        "mensaje_error": mensaje_error.replace("\n", " ").replace("\r", " ").strip(),
    }
    with ruta_bitacora.open(mode="a", encoding="utf-8", newline="") as archivo_csv:
        escritor = csv.DictWriter(archivo_csv, fieldnames=COLUMNAS_BITACORA)
        if nuevo:
            escritor.writeheader()
        escritor.writerow(fila)


# Alias de compatibilidad con la documentación maestra del proyecto
registrar_bitacora = registrar_ejecucion_bitacora
