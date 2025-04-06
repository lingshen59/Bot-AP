import discord
from discord import app_commands
from dotenv import load_dotenv
import aiohttp
import asyncio
import os

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("DEFAULT_MODEL")

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

enabled_channels = set()

@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot conectado como {client.user}")

@tree.command(name="start", description="Activar el modo conversación del bot en este canal.")
async def start(interaction: discord.Interaction):
    enabled_channels.add(interaction.channel.id)
    await interaction.response.send_message("🟢 Chat activado en este canal.")

@tree.command(name="disable", description="Desactiva el modo conversación del bot en este canal.")
async def disable(interaction: discord.Interaction):
    enabled_channels.discard(interaction.channel.id)
    await interaction.response.send_message("🔴 Chat desactivado en este canal.")

@tree.command(name="model", description="Cambiar el modelo de IA.")
@app_commands.describe(name="Nombre del modelo (gpt-4o, gpt-3.5-turbo, cosmosrp-pro, etc.)")
async def change_model(interaction: discord.Interaction, name: str):
    global MODEL
    MODEL = name
    await interaction.response.send_message(f"⚙️ Modelo cambiado a: `{name}`")

@tree.command(name="p", description="Recursos para aprender un lenguaje de programación.")
@app_commands.describe(lenguaje="Ej: Python, JavaScript", idioma="Ej: español, inglés")
async def recursos_programacion(interaction: discord.Interaction, lenguaje: str, idioma: str):
    await interaction.response.send_message(
        f"📘 Recursos para aprender {lenguaje} en {idioma}:\n"
        f"- YouTube: https://www.youtube.com/results?search_query=curso+{lenguaje}+{idioma}\n"
        f"- W3Schools: https://www.w3schools.com/\n"
        f"- FreeCodeCamp: https://www.freecodecamp.org/"
    )

@tree.command(name="c", description="Recursos de ciberseguridad.")
@app_commands.describe(nivel="básico, intermedio o experto")
async def recursos_ciberseguridad(interaction: discord.Interaction, nivel: str):
    await interaction.response.send_message(
        f"🛡️ Ciberseguridad ({nivel}):\n"
        f"- TryHackMe: https://tryhackme.com\n"
        f"- HackTheBox: https://www.hackthebox.com/\n"
        f"- YouTube: https://www.youtube.com/results?search_query=curso+ciberseguridad+{nivel}"
    )

@tree.command(name="h", description="Recursos de hacking ético.")
@app_commands.describe(nivel="básico, intermedio o experto")
async def recursos_hacking(interaction: discord.Interaction, nivel: str):
    await interaction.response.send_message(
        f"💻 Hacking ético ({nivel}):\n"
        f"- YouTube: https://www.youtube.com/results?search_query=hacking+ético+{nivel}\n"
        f"- HackTheBox Academy: https://academy.hackthebox.com/\n"
        f"- Cybrary: https://www.cybrary.it/"
    )

async def get_response(prompt):
    url = "https://api.pawan.krd/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            async for line in response.content:
                if line:
                    try:
                        text = line.decode("utf-8").replace("data: ", "").strip()
                        if text and text != "[DONE]":
                            yield eval(text)["choices"][0]["delta"].get("content", "")
                    except:
                        continue

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id in enabled_channels and client.user in message.mentions:
        prompt = message.content.replace(f"<@{client.user.id}>", "").strip()
        msg = await message.channel.send("💭 Pensando...")

        response_text = ""
        async for chunk in get_response(prompt):
            response_text += chunk
            await msg.edit(content=response_text)
            await asyncio.sleep(0.05)

client.run(TOKEN)
