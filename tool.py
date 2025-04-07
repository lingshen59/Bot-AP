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

# Custom check to verify if the user has the required permissions
def has_required_permissions():
    async def predicate(ctx):
        if ctx.author.id == OWNER_ID:
            return True
        return ctx.author.guild_permissions.ban_members or ctx.author.guild_permissions.kick_members or ctx.author.guild_permissions.mute_members
    return commands.check(predicate)

# Función para mostrar la lista de usuarios con sus números
async def show_user_list(ctx):
    guild = ctx.guild
    if not guild:
        await ctx.send("No estoy en un servidor.")
        return None
    
    members = guild.members
    if not members:
        await ctx.send("No hay miembros en este servidor.")
        return None
    
    user_list = "\n".join([f"{i+1}. {member.name} (ID: {member.id})" for i, member in enumerate(members)])
    await ctx.send(f"Lista de miembros:\n{user_list}")
    return members

# Función para obtener el usuario por número
async def get_user_by_number(ctx, number: int, members):
    if number < 1 or number > len(members):
        await ctx.send("Número de usuario no válido.")
        return None
    return members[number - 1]

# Comando para setear el límite de warns para que un usuario sea muteado o baneado
@bot.command(name="setwarn")
@has_required_permissions()
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
@has_required_permissions()
async def warns(ctx, user_number: int):
    members = await show_user_list(ctx)
    if not members:
        return
    
    member = await get_user_by_number(ctx, user_number, members)
    if not member:
        return
    
    user_warns = warns_data.get(str(member.id), 0)
    await ctx.send(f"{member.name} tiene {user_warns} warns.")

# Comando para añadir un warn a un usuario
@bot.command(name="addwarn")
@has_required_permissions()
async def addwarn(ctx, user_number: int):
    members = await show_user_list(ctx)
    if not members:
        return
    
    member = await get_user_by_number(ctx, user_number, members)
    if not member:
        return
    
    if str(member.id) not in warns_data:
        warns_data[str(member.id)] = 0
    warns_data[str(member.id)] += 1
    save_data()

    await ctx.send(f"{member.name} ahora tiene {warns_data[str(member.id)]} warns.")

# Comando para limpiar warns de un usuario
@bot.command(name="clearwarns")
@has_required_permissions()
async def clearwarns(ctx, user_number: int):
    members = await show_user_list(ctx)
    if not members:
        return
    
    member = await get_user_by_number(ctx, user_number, members)
    if not member:
        return
    
    if str(member.id) in warns_data:
        warns_data[str(member.id)] = 0
        save_data()
        await ctx.send(f"Los warns de {member.name} han sido limpiados.")
    else:
        await ctx.send(f"{member.name} no tiene warns.")

# Comando de banear
@bot.command(name="ban")
@has_required_permissions()
async def ban(ctx, user_number: int, *, reason: str):
    members = await show_user_list(ctx)
    if not members:
        return
    
    member = await get_user_by_number(ctx, user_number, members)
    if not member:
        return
    
    await member.ban(reason=reason)
    await ctx.send(f"{member.name} ha sido baneado por: {reason}")
    
# Comando de desbanear
@bot.command(name="unban")
@has_required_permissions()
async def ban(ctx, user_number: int):
    members = await show_user_list(ctx)
    if not members:
        return
    
    member = await get_user_by_number(ctx, user_number, members)
    if not member:
        return
    
    await member.unban()
    await ctx.send(f"{member.name} ha sido desbaneado")

# Comando de mute
@bot.command(name="mute")
@has_required_permissions()
async def mute(ctx, user_number: int, duration: str):
    members = await show_user_list(ctx)
    if not members:
        return
    
    member = await get_user_by_number(ctx, user_number, members)
    if not member:
        return
    
    await member.edit(mute=True)
    await ctx.send(f"{member.name} ha sido muteado por {duration}.")

# Comando de kick
@bot.command(name="kick")
@has_required_permissions()
async def kick(ctx, user_number: int, *, reason: str):
    members = await show_user_list(ctx)
    if not members:
        return
    
    member = await get_user_by_number(ctx, user_number, members)
    if not member:
        return
    
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
