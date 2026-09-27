import discord
from discord.ext import commands
import os

# Configuración de los Intents (Permisos necesarios)
intents = discord.Intents.default()
intents.message_content = True  # Necesario para leer los mensajes
intents.members = True          # Necesario para las bienvenidas

bot = commands.Bot(command_prefix="!", intents=intents)

# Diccionario simple para llevar el conteo de mensajes (Niveles básicos)
user_messages = {}

@bot.event
async def on_ready():
    print(f"¡{bot.user.name} está conectado y listo 24/7!")
    await bot.change_presence(activity=discord.Game(name="Moderando el servidor | !top"))

# --- 1. MENSAJE DE BIENVENIDA ---
@bot.event
async def on_member_join(member):
    # Reemplaza 'bienvenida' con el nombre exacto del canal donde quieres que salude
    channel = discord.utils.get(member.guild.text_channels, name="bienvenida")
    if channel:
        embed = discord.Embed(
            title="¡Nuevo miembro en el servidor!",
            description=f"¡Bienvenido/a {member.mention} a **{member.guild.name}**! Esperamos que la pases genial por aquí.",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

# --- 2. SISTEMA DE NIVELES (El que más escribe) ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Contar mensajes por usuario
    author_id = message.author.id
    user_messages[author_id] = user_messages.get(author_id, 0) + 1

    # Procesar comandos normales del bot
    await bot.process_commands(message)

@bot.command(name="top", help="Muestra al usuario que más mensajes ha enviado.")
async def top_chatters(ctx):
    if not user_messages:
        await ctx.send("Aún no hay suficientes mensajes registrados.")
        return

    # Ordenar usuarios por cantidad de mensajes
    top_user_id = max(user_messages, key=user_messages.get)
    top_user = await ctx.guild.fetch_member(top_user_id)
    count = user_messages[top_user_id]

    await ctx.send(f"🏆 El usuario que más escribe es **{top_user.display_name}** con un total de **{count}** mensajes.")

# --- 3. MODERACIÓN BÁSICA ---
@bot.command(name="kick", help="Expulsa a un usuario del servidor.")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"✅ {member.mention} ha sido expulsado del servidor. Razón: {reason}")

@bot.command(name="ban", help="Banea a un usuario del servidor.")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member.mention} ha sido baneado del servidor. Razón: {reason}")

@bot.command(name="limpiar", help="Borra una cantidad específica de mensajes.")
@commands.has_permissions(manage_messages=True)
async def limpiar(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Se han eliminado {amount} mensajes.", delete_after=5)

# Manejo de errores de permisos
@kick.error
@ban.error
@limpiar.error
async def moderation_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ No tienes los permisos necesarios para usar este comando.")
    else:
        await ctx.send("❌ Ocurrió un error al ejecutar el comando.")

# Ejecutar el bot leyendo el Token de forma segura desde las variables del sistema
TOKEN = os.getenv("MTU1MzgwOTU5MTk2MjQ0Mzg3Nw.GtGFbs.hMdRXyYFT9GzEWRk2aubwIZa3mu3orcrsKgHqU")
if not TOKEN:
    print("⚠️ ADVERTENCIA: No se encontró la variable de entorno 'DISCORD_TOKEN'. Asegúrate de configurarla en tu panel.")
else:
    bot.run(TOKEN)
