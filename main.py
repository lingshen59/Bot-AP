import os
import discord
from discord.ext import commands
from discord import app_commands
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("Token")
API_KEY = os.getenv("PAWAN_API_KEY")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

active_channel = None

# ======================== FUNCIONES ========================

def ask_pawan(message):
    url = "https://api.pawan.krd/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": message}],
        "temperature": 0.9
    }
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"❌ Error del modelo: {response.json().get('error', {}).get('message', 'Respuesta no válida.')}"

# ======================== EVENTOS ========================

@bot.event
async def on_ready():
    print(f"✅ Conectado como {bot.user}")
    try:
        synced = await tree.sync()
        print(f"🔁 Slash commands sincronizados: {len(synced)}")
    except Exception as e:
        print(f"Error al sincronizar: {e}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    global active_channel
    if active_channel != message.channel.id:
        return

    if bot.user in message.mentions or message.content.strip() != "":
        prompt = f"Responde de forma educativa y divertida sobre temas como ciberseguridad, hacking ético, programación o lo que te pregunten. Mensaje: {message.content}"
        await message.channel.typing()
        try:
            response = ask_pawan(prompt)
            await message.reply(response[:2000])
        except Exception as e:
            await message.reply(f"⚠️ Error procesando la respuesta: {e}")

# ======================== COMANDOS SLASH ========================

@tree.command(name="start", description="Activa el bot en este canal")
async def start_command(interaction: discord.Interaction):
    global active_channel
    active_channel = interaction.channel_id
    await interaction.response.send_message("✅ Bot activado en este canal. Puedes hablarme libremente 😉")

@tree.command(name="disable", description="Desactiva el bot en este canal")
async def disable_command(interaction: discord.Interaction):
    global active_channel
    if active_channel == interaction.channel_id:
        active_channel = None
        await interaction.response.send_message("❌ Bot desactivado en este canal.")
    else:
        await interaction.response.send_message("⚠️ Este canal no está activo.")

@tree.command(name="p", description="Recursos para aprender un lenguaje de programación")
@app_commands.describe(lenguaje="Lenguaje de programación", idioma="Idioma (español, inglés...)")
async def p_command(interaction: discord.Interaction, lenguaje: str, idioma: str):
    await interaction.response.defer()
    prompt = f"Dame enlaces útiles en {idioma} para aprender {lenguaje}, incluyendo sitios web y videos si es posible."
    resultado = ask_pawan(prompt)
    await interaction.followup.send(resultado[:2000])

@tree.command(name="c", description="Recursos de ciberseguridad")
@app_commands.describe(nivel="Nivel de conocimiento: básico, intermedio o experto")
async def c_command(interaction: discord.Interaction, nivel: str):
    await interaction.response.defer()
    prompt = f"Dame una lista de recursos de ciberseguridad para el nivel {nivel}, incluyendo cursos, libros, laboratorios online y videos si es posible."
    resultado = ask_pawan(prompt)
    await interaction.followup.send(resultado[:2000])

@tree.command(name="h", description="Recursos de hacking ético")
@app_commands.describe(nivel="Nivel de conocimiento: básico, intermedio o experto")
async def h_command(interaction: discord.Interaction, nivel: str):
    await interaction.response.defer()
    prompt = f"Recomiéndame recursos para aprender hacking ético a nivel {nivel}, que incluyan sitios web, videos, libros o laboratorios prácticos."
    resultado = ask_pawan(prompt)
    await interaction.followup.send(resultado[:2000])

# ======================== EJECUCIÓN ========================

bot.run(TOKEN)
