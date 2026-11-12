import datetime
import os
import platform
import subprocess
import urllib.parse
import webbrowser
from bs4 import BeautifulSoup
import requests
import webview


def resource_path(relative_path):
  """Obtiene la ruta absoluta de los recursos para cuando se empaquete como .exe / binario"""
  try:
    base_path = sys._MEIPASS
  except Exception:
    base_path = os.path.abspath(".")
  return os.path.join(base_path, relative_path)


def buscar_en_internet(query):
  """Busca en la web usando DuckDuckGo de forma gratuita y sin APIs de pago"""
  try:
    query_encoded = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={query_encoded}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    response = requests.get(url, headers=headers, timeout=5)
    if response.status_code == 200:
      soup = BeautifulSoup(response.text, "html.parser")
      result = soup.find("a", {"class": "result__snippet"})
      if result:
        return result.get_text().strip()

    return "No encontré una respuesta clara en la web para eso."
  except Exception as e:
    return "No se pudo conectar a internet para buscar la información."


class AssistantAPI:
  """Clase puente entre JavaScript (interfaz) y Python (sistema operativo)."""

  def __init__(self):
    self.sistema_actual = platform.system()  # Detecta si es 'Windows' o 'Linux'

    # ==========================================
    # 1. DICCIONARIO DE PROGRAMAS Y ENLACES
    # ==========================================
    self.programas = {
        "word": self._abrir_word,
        "steam": self._abrir_steam,
        "bloc de notas": self._abrir_notepad,
        "notepad": self._abrir_notepad,
        "navegador": lambda: webbrowser.open("https://www.google.com"),
        "youtube": lambda: webbrowser.open("https://www.youtube.com"),
        "whatsapp": lambda: webbrowser.open("https://web.whatsapp.com"),
        "twitch": lambda: webbrowser.open("https://www.twitch.tv"),
        # Puedes seguir añadiendo claves aquí fácilmente:
        # "discord": lambda: subprocess.Popen(["discord"]),
    }

    # ==========================================
    # 2. PREGUNTAS Y RESPUESTAS PROGRAMADAS
    # ==========================================
    self.respuestas_programadas = {
        "hola": "¡Hola amo! Operando al 100% y lista para ejecutar tus órdenes.",
        "quien eres": (
            "Soy Cyn, tu asistente personal estoy lista para lo que sea"
            " risita."
        ),
        "te gustan los mangos": (
            "Si me gustan los mangos, pero no puedo comerlos porque estoy"
            " atrapada aqui."
        ),
        "como estas": (
            "Sistemas estables y con toda la energía. ¿Qué hacemos ahora?"
        ),
        "que te gusta": (
            "Me gusta escuchar a los humanos gritar"
        ),
    }

  # Funciones internas auxiliares para apertura segura multiplataforma
  def _abrir_word(self):
    if self.sistema_actual == "Windows":
      subprocess.Popen(["start", "winword"], shell=True)
    else:
      subprocess.Popen(["libreoffice", "--writer"])
    return "Abriendo el procesador de textos..."

  def _abrir_steam(self):
    if self.sistema_actual == "Windows":
      steam_path = r"C:\Program Files (x86)\Steam\steam.exe"
      if os.path.exists(steam_path):
        subprocess.Popen([steam_path])
      else:
        subprocess.Popen(["start", "steam"], shell=True)
    else:
      subprocess.Popen(["steam"])
    return "Abriendo Steam..."

  def _abrir_notepad(self):
    if self.sistema_actual == "Windows":
      subprocess.Popen(["notepad"])
    else:
      subprocess.Popen(["gedit"])
    return "Abriendo el editor de notas..."

  def send_message(self, message):
    msg_lower = message.lower().strip()

    # ==========================================
    # A. UTILIDADES DE HORA Y FECHA
    # ==========================================
    if "qué hora es" in msg_lower or "hora actual" in msg_lower:
      hora_actual = datetime.datetime.now().strftime("%H:%M")
      return f"🕒 Son las {hora_actual}."

    if "qué día es" in msg_lower or "fecha" in msg_lower:
      hoy = datetime.datetime.now().strftime("%d/%m/%Y")
      return f"📅 Hoy es {hoy}."

    # ==========================================
    # B. BÚSQUEDA ESPECÍFICA EN GOOGLE
    # ==========================================
    if "buscar" in msg_lower and "en google" in msg_lower:
      query = (
          msg_lower.replace("buscar", "").replace("en google", "").strip()
      )
      webbrowser.open(f"https://www.google.com/search?q={query}")
      return f"Buscando '{query}' en Google..."

    # ==========================================
    # C. APERTURA DE PROGRAMAS (Diccionario Dinámico)
    # ==========================================
    if msg_lower.startswith("abrir ") or msg_lower.startswith("iniciar "):
      app_buscada = (
          msg_lower.replace("abrir ", "").replace("iniciar ", "").strip()
      )
      for nombre, accion in self.programas.items():
        if nombre in app_buscada:
          try:
            return accion()
          except Exception as e:
            return f"No pude abrir {nombre}: {str(e)}"
      return f"No tengo '{app_buscada}' registrado en mis accesos directos."

    # ==========================================
    # D. PREGUNTAS Y RESPUESTAS PROGRAMADAS
    # ==========================================
    for pregunta, respuesta in self.respuestas_programadas.items():
      if pregunta in msg_lower:
        return respuesta

    # ==========================================
    # E. BÚSQUEDA AUTOMÁTICA EN LA WEB (DuckDuckGo)
    # ==========================================
    return buscar_en_internet(message)


if __name__ == "__main__":
  api = AssistantAPI()

  # Usa la función auxiliar resource_path para empaquetados limpios con PyInstaller
  html_path = os.path.abspath("index.html")

  window = webview.create_window(
      title="Cyn IA",
      url=html_path,
      js_api=api,
      width=420,
      height=650,
      resizable=True,
  )
  webview.start()