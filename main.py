import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
import asyncio
from dotenv import load_dotenv

# Cargar el archivo .env
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID'))  # ID del dueño del bot

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix=',', intents=intents, owner_id=OWNER_ID)

# Cargar los datos de warns y configuración
warns_data = {}
config_data = {}

# Cargar warn data y configuraciones desde archivos JSON
def load_data():
    global warns_data, config_data
    if os.path.exists('warns.json'):
        with open('warns.json', 'r') as file:
            warns_data = json.load(file)
    if os.path.exists('config.json'):
        with open('config.json', 'r') as file:
            config_data = json.load(file)

# Guardar los datos de warns y configuración en archivos JSON
def save_data():
    with open('warns.json', 'w') as file:
        json.dump(warns_data, file)
    with open('config.json', 'w') as file:
        json.dump(config_data, file)

# Custom check to verify if the user has the required permissions
def has_required_permissions():
    def predicate(interaction: discord.Interaction):
        if interaction.user.id == OWNER_ID:
            return True
        return interaction.permissions.ban_members or interaction.permissions.kick_members or interaction.permissions.mute_members
    return app_commands.check(predicate)

# Comando para setear el límite de warns para que un usuario sea muteado o baneado
@bot.tree.command(name="setwarn", description="Establecer límite de warns y duración para acciones")
@app_commands.describe(warn_limit="Límite de warns", action="Acción a realizar (mute, ban, kick)", duration="Duración (ej: 1h)")
@has_required_permissions()
async def setwarn(interaction: discord.Interaction, warn_limit: int, action: str, duration: str):
    if action not in ['mute', 'ban', 'kick']:
        await interaction.response.send_message("Acción no válida. Use 'mute', 'ban' o 'kick'.")
        return
    
    # Validación de duración
    time_units = {'m': 'minutes', 'h': 'hours', 'd': 'days'}
    unit = duration[-1]
    if unit not in time_units:
        await interaction.response.send_message("Duración no válida. Use 'm' para minutos, 'h' para horas, 'd' para días.")
        return
    
    try:
        value = int(duration[:-1])
    except ValueError:
        await interaction.response.send_message("Duración no válida. Debe ser un número seguido de 'm', 'h' o 'd'.")
        return

    # Guardar la configuración
    config_data["warn_limit"] = warn_limit
    config_data["action"] = action
    config_data["duration"] = str(value) + unit
    save_data()

    await interaction.response.send_message(f"Límite de warns establecido a {warn_limit} para acción '{action}' y duración '{duration}'.")

# Comando para ver los warns de un usuario
@bot.tree.command(name="warns", description="Ver los warns de un usuario")
@app_commands.describe(member="Miembro del servidor")
@has_required_permissions()
async def warns(interaction: discord.Interaction, member: discord.Member):
    user_warns = warns_data.get(str(member.id), 0)
    await interaction.response.send_message(f"{member.name} tiene {user_warns} warns.")

# Comando para añadir un warn a un usuario
@bot.tree.command(name="addwarn", description="Añadir un warn a un usuario")
@app_commands.describe(member="Miembro del servidor")
@has_required_permissions()
async def addwarn(interaction: discord.Interaction, member: discord.Member):
    if str(member.id) not in warns_data:
        warns_data[str(member.id)] = 0
    warns_data[str(member.id)] += 1
    save_data()

    await interaction.response.send_message(f"{member.name} ahora tiene {warns_data[str(member.id)]} warns.")

# Comando para limpiar warns de un usuario
@bot.tree.command(name="clearwarns", description="Limpiar todos los warns de un usuario")
@app_commands.describe(member="Miembro del servidor")
@has_required_permissions()
async def clearwarns(interaction: discord.Interaction, member: discord.Member):
    if str(member.id) in warns_data:
        warns_data[str(member.id)] = 0
        save_data()
        await interaction.response.send_message(f"Los warns de {member.name} han sido limpiados.")
    else:
        await interaction.response.send_message(f"{member.name} no tiene warns.")

# Comando de banear
@bot.tree.command(name="ban", description="Banear a un usuario")
@app_commands.describe(member="Miembro del servidor", reason="Razón del ban")
@has_required_permissions()
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"{member.name} ha sido baneado por: {reason}")

@bot.tree.command(name="unban", description="Desbanear a un usuario")
@app_commands.describe(member="Miembro del servidor")
@has_required_permissions()
async def unban(interaction: discord.Interaction, member: discord.Member):
    await member.unban()
    await interaction.response.send_message(f"{member.name} ha sido desbaneado")

# Comando de mute
@bot.tree.command(name="mute", description="Mute a un usuario")
@app_commands.describe(member="Miembro del servidor", duration="Duración del mute (ej: 1h)")
@has_required_permissions()
async def mute(interaction: discord.Interaction, member: discord.Member, duration: str):
    await member.edit(mute=True)
    await interaction.response.send_message(f"{member.name} ha sido muteado por {duration}.")

# Comando de kick
@bot.tree.command(name="kick", description="Kick a un usuario")
@app_commands.describe(member="Miembro del servidor", reason="Razón del kick")
@has_required_permissions()
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"{member.name} ha sido kickeado por: {reason}")

# Evento de inicio del bot
@bot.event
async def on_ready():
    load_data()
    print(f'Bot {bot.user} ha iniciado.')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

# Función principal asincrónica para ejecutar el bot
async def main():
    await bot.start(TOKEN)

# Ejecutar el código asincrónico
if __name__ == "__main__":
    asyncio.run(main())  # Ejecutar la función principal asincrónica
