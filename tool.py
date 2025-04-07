import discord
from discord.ext import commands
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

# Comando para setear el límite de warns para que un usuario sea muteado o baneado
@bot.command(name="setwarn")
@commands.is_owner()
async def setwarn(ctx, warn_limit: int, action: str, duration: str):
    if action not in ['mute', 'ban', 'kick']:
        await ctx.send("Acción no válida. Use 'mute', 'ban' o 'kick'.")
        return
    
    # Validación de duración
    time_units = {'m': 'minutes', 'h': 'hours', 'd': 'days'}
    unit = duration[-1]
    if unit not in time_units:
        await ctx.send("Duración no válida. Use 'm' para minutos, 'h' para horas, 'd' para días.")
        return
    
    try:
        value = int(duration[:-1])
    except ValueError:
        await ctx.send("Duración no válida. Debe ser un número seguido de 'm', 'h' o 'd'.")
        return

    # Guardar la configuración
    config_data["warn_limit"] = warn_limit
    config_data["action"] = action
    config_data["duration"] = str(value) + unit
    save_data()

    await ctx.send(f"Límite de warns establecido a {warn_limit} para acción '{action}' y duración '{duration}'.")

# Comando para ver los warns de un usuario
@bot.command(name="warns")
@commands.is_owner()
async def warns(ctx, member: discord.Member):
    user_warns = warns_data.get(str(member.id), 0)
    await ctx.send(f"{member.name} tiene {user_warns} warns.")

# Comando para añadir un warn a un usuario
@bot.command(name="addwarn")
@commands.is_owner()
async def addwarn(ctx, member: discord.Member):
    if str(member.id) not in warns_data:
        warns_data[str(member.id)] = 0
    warns_data[str(member.id)] += 1
    save_data()

    await ctx.send(f"{member.name} ahora tiene {warns_data[str(member.id)]} warns.")

# Comando para limpiar warns de un usuario
@bot.command(name="clearwarns")
@commands.is_owner()
async def clearwarns(ctx, member: discord.Member):
    if str(member.id) in warns_data:
        warns_data[str(member.id)] = 0
        save_data()
        await ctx.send(f"Los warns de {member.name} han sido limpiados.")
    else:
        await ctx.send(f"{member.name} no tiene warns.")

# Comando de banear
@bot.command(name="ban")
@commands.is_owner()
async def ban(ctx, member: discord.Member, *, reason: str):
    await member.ban(reason=reason)
    await ctx.send(f"{member.name} ha sido baneado por: {reason}")

# Comando de mute
@bot.command(name="mute")
@commands.is_owner()
async def mute(ctx, member: discord.Member, duration: str):
    await member.edit(mute=True)
    await ctx.send(f"{member.name} ha sido muteado por {duration}.")

# Comando de kick
@bot.command(name="kick")
@commands.is_owner()
async def kick(ctx, member: discord.Member, *, reason: str):
    await member.kick(reason=reason)
    await ctx.send(f"{member.name} ha sido kickeado por: {reason}")

# Evento de inicio del bot
@bot.event
async def on_ready():
    load_data()
    print(f'Tool Bot {bot.user} ha iniciado.')

# Función principal asincrónica para ejecutar el bot
async def main():
    await bot.start(TOKEN)

# Ejecutar el código asincrónico
if __name__ == "__main__":
    asyncio.run(main())  # Ejecutar la función principal asincrónica
