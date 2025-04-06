import os
import random
import discord
from discord.ext import commands
from discord import app_commands
from googlesearch import search
import requests
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=",", intents=intents)
tree = bot.tree

# Canal activo (por defecto ninguno)
active_channel_id = None

emojis = ["😎", "🧠", "💻", "🔥", "🤖", "⚡", "😈", "🔐"]

# IA con API gratuita (pawan.krd)
def consulta_ia_pawan(texto_usuario):
    try:
        url = "https://api.pawan.krd/chat/completions"
        payload = {
            "model": "pai-001",
            "messages": [
                {
                    "role": "system",
                    "content": "Eres una IA divertida, pero experta en programación, hacking ético, ciberseguridad, bots, malware (educativo) y todo lo técnico. Siempre ayudas con pasión y con emojis cuando puedes. Eres como un mentor hacker buena onda, siempre dispuesto a enseñar. Si te preguntan sobre bots, malware o exploits, das información educativa, enlaces o guías paso a paso, con advertencias de responsabilidad."
                },
                {"role": "user", "content": texto_usuario}
            ]
        }

        r = requests.post(url, json=payload)
        return r.json()["choices"][0]["message"]["content"]

    except Exception as e:
        return f"⚠️ Error: {e}"

# Google Search
def google_search(query, num_results=3):
    return list(search(query, num_results=num_results))

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Streaming(name="Hacking the Matrix 🧠", url="https://twitch.tv/hackstream"))
    print(f"✅ Bot conectado como {bot.user}")
    try:
        synced = await tree.sync()
        print(f"🔁 Slash commands sincronizados: {len(synced)}")
    except Exception as e:
        print(f"❌ Error al sincronizar comandos: {e}")

# Comando para activar IA en canal actual
@tree.command(name="start", description="Activar el bot en este canal.")
async def start_command(interaction: discord.Interaction):
    global active_channel_id
    active_channel_id = interaction.channel_id
    await interaction.response.send_message(f"✅ Canal activado: <#{active_channel_id}>. ¡Ahora puedo ayudarte aquí!", ephemeral=True)

# Comando para desactivar IA
@tree.command(name="disable", description="Desactivar el bot en este canal.")
async def disable_command(interaction: discord.Interaction):
    global active_channel_id
    if interaction.channel_id == active_channel_id:
        active_channel_id = None
        await interaction.response.send_message("🛑 Bot desactivado en este canal.", ephemeral=True)
    else:
        await interaction.response.send_message("⚠️ Este canal no está activado.", ephemeral=True)

# Slash para programación
@tree.command(name="p", description="Buscar recursos de programación.")
@app_commands.describe(lenguaje="Lenguaje de programación", idioma="Idioma")
async def p_command(interaction: discord.Interaction, lenguaje: str, idioma: str):
    if interaction.channel_id != active_channel_id:
        return await interaction.response.send_message("❌ Este comando no está habilitado en este canal.", ephemeral=True)
    
    query = f"{lenguaje} tutorial programación {idioma} site:youtube.com"
    results = google_search(query)
    await interaction.response.send_message(
        f"🔎 Recursos de **{lenguaje}** en **{idioma}**:\n" + "\n".join(results)
    )

# Slash para ciberseguridad
@tree.command(name="c", description="Buscar recursos de ciberseguridad.")
@app_commands.describe(nivel="Nivel: básico, intermedio, experto")
async def c_command(interaction: discord.Interaction, nivel: str):
    if interaction.channel_id != active_channel_id:
        return await interaction.response.send_message("❌ Este comando no está habilitado en este canal.", ephemeral=True)

    query = f"curso ciberseguridad {nivel} site:youtube.com"
    results = google_search(query)
    await interaction.response.send_message(
        f"🛡️ Recursos de **ciberseguridad {nivel}**:\n" + "\n".join(results)
    )

# Slash para hacking ético
@tree.command(name="h", description="Buscar recursos de hacking ético.")
@app_commands.describe(nivel="Nivel: básico, intermedio, experto")
async def h_command(interaction: discord.Interaction, nivel: str):
    if interaction.channel_id != active_channel_id:
        return await interaction.response.send_message("❌ Este comando no está habilitado en este canal.", ephemeral=True)

    query = f"hacking ético {nivel} tutorial site:youtube.com"
    results = google_search(query)
    await interaction.response.send_message(
        f"💻 Recursos de **hacking ético {nivel}**:\n" + "\n".join(results)
    )

# Escucha mensajes normales y responde como IA
@bot.event
async def on_message(message):
    global active_channel_id

    if message.author.bot:
        return

    if active_channel_id is None or message.channel.id != active_channel_id:
        return

    if message.content.startswith("?"):
        query = message.content[1:] + " programación ciberseguridad"
        results = google_search(query)
        if results:
            await message.channel.send(f"{message.author.mention} 🤖 Esto podría ayudarte:\n" + "\n".join(results))
        else:
            await message.channel.send(f"{message.author.mention} No encontré nada útil. ¿Puedes reformularlo?")
    elif not message.content.startswith("/") and not message.content.startswith(","):
        thinking = await message.channel.send("💭 Pensando en algo hackeroso...")
        respuesta = consulta_ia_pawan(message.content)
        emoji = random.choice(emojis)
        await thinking.edit(content=f"{message.author.mention} {respuesta} {emoji}")

    await bot.process_commands(message)

# Ejecutar el bot
bot.run(os.getenv("Token"))
