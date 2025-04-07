import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
import os

# Cargar el archivo .env
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID'))  # ID del dueño del bot

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents, owner_id=OWNER_ID)

# Función para manejar los comandos de la terminal
async def run_terminal_commands():
    while True:
        print("\nComandos disponibles:")
        print("1. Banear usuario en un servidor")
        print("2. Mutear usuario en un servidor")
        print("3. Salir")
        command = input("Introduce un número de comando: ")

        if command == "1":
            # Comando de ban
            guild_id = input("Introduce el ID del servidor: ")
            user_id = input("Introduce la ID del usuario a banear: ")
            reason = input("Introduce la razón del ban: ")
            await ban_user(guild_id, user_id, reason)

        elif command == "2":
            # Comando de mute
            guild_id = input("Introduce el ID del servidor: ")
            user_id = input("Introduce la ID del usuario a mutear: ")
            duration = input("Introduce la duración (minutos(m), horas(h), días(d)): ")
            await mute_user(guild_id, user_id, duration)

        elif command == "3":
            print("Saliendo del programa...")
            break  # Salir del bucle

        else:
            print("Comando no reconocido. Intenta de nuevo.")

# Función de banear un usuario
async def ban_user(guild_id, user_id, reason):
    try:
        guild = bot.get_guild(int(guild_id))
        if not guild:
            print("Servidor no encontrado.")
            return

        # Verificar si el usuario que ejecuta el comando es el dueño del bot
        if bot.owner_id != OWNER_ID:
            print("No tienes permisos para ejecutar este comando.")
            return

        # Encontrar el miembro a banear por su ID
        member = guild.get_member(int(user_id))
        if member:
            await member.ban(reason=reason)
            print(f"Usuario con ID {user_id} ha sido baneado en el servidor {guild.name} por: {reason}.")
        else:
            print("Usuario no encontrado.")
    except Exception as e:
        print(f"Error al banear al usuario: {e}")

# Función de mutear un usuario
async def mute_user(guild_id, user_id, duration):
    try:
        guild = bot.get_guild(int(guild_id))
        if not guild:
            print("Servidor no encontrado.")
            return

        # Verificar si el usuario que ejecuta el comando es el dueño del bot
        if bot.owner_id != OWNER_ID:
            print("No tienes permisos para ejecutar este comando.")
            return

        member = guild.get_member(int(user_id))
        if member:
            role = discord.utils.get(guild.roles, name="Muted")
            if not role:
                role = await guild.create_role(name="Muted")
                for channel in guild.channels:
                    await channel.set_permissions(role, speak=False, send_messages=False)

            await member.add_roles(role)
            print(f"Usuario con ID {user_id} ha sido muteado en el servidor {guild.name} por {duration}.")
        else:
            print("Usuario no encontrado.")
    except Exception as e:
        print(f"Error al mutear al usuario: {e}")

# Evento de inicio del bot
@bot.event
async def on_ready():
    print(f'Bot {bot.user} ha iniciado.')
    # Ejecutar los comandos de la terminal después de conectar el bot
    asyncio.create_task(run_terminal_commands())

# Función principal asincrónica para ejecutar el bot
async def main():
    # Ejecutar el bot de Discord
    await bot.start(TOKEN)

# Ejecutar el código asincrónico
if __name__ == "__main__":
    asyncio.run(main())  # Ejecutar la función principal asincrónica
