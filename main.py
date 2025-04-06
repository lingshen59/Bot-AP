import discord
from discord.ext import commands
from discord import app_commands
from googlesearch import search
import dotenv

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=",", intents=intents)
tree = bot.tree

load_dotenv()

# Solo responderá en este canal
CHANNEL_ID = 1358302860734890004

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    try:
        synced = await tree.sync()
        print(f"🔁 Slash commands sincronizados: {len(synced)}")
    except Exception as e:
        print(f"Error al sincronizar comandos: {e}")

# Función para buscar en Google
def google_search(query, num_results=3):
    results = []
    for result in search(query, num_results=num_results):
        results.append(result)
    return results

# Slash command: /p lenguaje idioma
@tree.command(name="p", description="Buscar recursos de programación.")
@app_commands.describe(lenguaje="Lenguaje de programación", idioma="Idioma (ej: español, inglés, etc.)")
async def p_command(interaction: discord.Interaction, lenguaje: str, idioma: str):
    if interaction.channel_id != CHANNEL_ID:
        return await interaction.response.send_message("❌ Este comando solo puede usarse en el canal autorizado.", ephemeral=True)
    
    query = f"{lenguaje} tutorial programación {idioma} site:youtube.com"
    results = google_search(query)

    if results:
        await interaction.response.send_message(f"🔎 Aquí tienes algunos recursos para **{lenguaje}** en **{idioma}**:\n" + "\n".join(results))
    else:
        await interaction.response.send_message("😕 No encontré resultados, intenta con otros términos.")

# Slash command: /c nivel
@tree.command(name="c", description="Buscar recursos de ciberseguridad.")
@app_commands.describe(nivel="Nivel: básico, intermedio, experto")
async def c_command(interaction: discord.Interaction, nivel: str):
    if interaction.channel_id != CHANNEL_ID:
        return await interaction.response.send_message("❌ Este comando solo puede usarse en el canal autorizado.", ephemeral=True)

    query = f"curso ciberseguridad {nivel} site:youtube.com"
    results = google_search(query)

    if results:
        await interaction.response.send_message(f"🛡️ Recursos de **ciberseguridad {nivel}**:\n" + "\n".join(results))
    else:
        await interaction.response.send_message("😕 No encontré resultados para ese nivel.")

# Slash command: /h nivel
@tree.command(name="h", description="Buscar recursos de hacking ético.")
@app_commands.describe(nivel="Nivel: básico, intermedio, experto")
async def h_command(interaction: discord.Interaction, nivel: str):
    if interaction.channel_id != CHANNEL_ID:
        return await interaction.response.send_message("❌ Este comando solo puede usarse en el canal autorizado.", ephemeral=True)

    query = f"hacking ético {nivel} tutorial site:youtube.com"
    results = google_search(query)

    if results:
        await interaction.response.send_message(f"💻 Recursos de **hacking ético {nivel}**:\n" + "\n".join(results))
    else:
        await interaction.response.send_message("😕 No encontré recursos para ese nivel.")

# "IA" básica que responde preguntas de programación/ciber
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id != CHANNEL_ID:
        return

    if message.content.startswith("?"):
        query = message.content[1:] + " programación ciberseguridad"
        results = google_search(query)
        if results:
            await message.channel.send("🤖 Esto podría ayudarte:\n" + "\n".join(results))
        else:
            await message.channel.send("No encontré nada útil. ¿Puedes reformular tu pregunta?")
    
    await bot.process_commands(message)

# Reemplaza este token con el de tu bot
bot.run(os.getenv(Token))
