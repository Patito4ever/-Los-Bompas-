import discord
from discord.ext import commands
from discord import app_commands
import os
from io import BytesIO

# Configuración de los Intents necesarios
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Diccionario para llevar el conteo de mensajes (Niveles básicos)
user_messages = {}

# Código secreto administrativo actualizado
ADMIN_SECRET_CODE = "grupo bompa_10"

@bot.event
async def on_ready():
    print(f"¡{bot.user.name} está conectado y listo 24/7!")
    # Sincronizar los comandos de barra (Slash Commands) con Discord
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizados {len(synced)} comandos de barra (/)")
    except Exception as e:
        print(e)
    
    await bot.change_presence(activity=discord.Game(name="Roblox Rivals ⚔️ | /top"))

# --- 1. MENSAJE DE BIENVENIDA ---
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="bienvenida")
    if channel:
        embed = discord.Embed(
            title="¡Nuevo miembro en Los Bompas! 🎮",
            description=f"¡Bienvenido/a {member.mention}! Prepárate para romperla en **Roblox Rivals** ⚔️.",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

# --- 2. SISTEMA DE NIVELES (El que más escribe) ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    author_id = message.author.id
    user_messages[author_id] = user_messages.get(author_id, 0) + 1

    await bot.process_commands(message)

@bot.tree.command(name="top", description="Muestra al usuario que más mensajes ha enviado en el servidor.")
async def slash_top(interaction: discord.Interaction):
    if not user_messages:
        await interaction.response.send_message("Aún no hay suficientes mensajes registrados.", ephemeral=True)
        return

    top_user_id = max(user_messages, key=user_messages.get)
    top_user = await interaction.guild.fetch_member(top_user_id)
    count = user_messages[top_user_id]

    await interaction.response.send_message(f"🏆 El usuario que más escribe en Los Bompas es **{top_user.display_name}** con un total de **{count}** mensajes.")

# --- 3. SISTEMA DE MODERACIÓN AVANZADO CON CÓDIGO SECRETO Y DURACIÓN ---
class BanModal(discord.ui.Modal, title="Verificación de Seguridad - Ban"):
    codigo = discord.ui.TextInput(
        label="Código Secreto Administrativo",
        placeholder="Introduce el código secreto...",
        style=discord.TextStyle.short,
        required=True
    )

    def __init__(self, member: discord.Member, duration: str, reason: str):
        super().__init__()
        self.member = member
        self.duration = duration
        self.reason = reason

    async def on_submit(self, interaction: discord.Interaction):
        # Verificar si el código ingresado es correcto
        if self.codigo.value.strip() == ADMIN_SECRET_CODE:
            try:
                full_reason = f"Duración: {self.duration} | Razón: {self.reason} | Ejecutado por: {interaction.user}"
                await self.member.ban(reason=full_reason)
                await interaction.response.send_message(
                    f"🔨 {self.member.mention} ha sido baneado exitosamente.\n⏱️ **Duración:** {self.duration}\n📝 **Razón:** {self.reason}",
                    ephemeral=False
                )
            except Exception as e:
                await interaction.response.send_message(f"❌ Ocurrió un error al intentar banear al usuario: {e}", ephemeral=True)
        else:
            await interaction.response.send_message(
                "❌ **Acceso Denegado:** El código secreto administrativo es incorrecto.",
                ephemeral=True
            )

@bot.tree.command(name="ban", description="Banea a un usuario con verificación de código y duración.")
@app_commands.describe(
    member="El usuario a banear",
    duration="Selecciona la duración de la sanción",
    reason="Razón del baneo"
)
@app_commands.choices(duration=[
    app_commands.Choice(name="Permanentemente", value="Permanentemente"),
    app_commands.Choice(name="1 Día", value="1 Día"),
    app_commands.Choice(name="5 Días", value="5 Días"),
    app_commands.Choice(name="2 Semanas", value="2 Semanas"),
    app_commands.Choice(name="1 Mes", value="1 Mes")
])
async def slash_ban(interaction: discord.Interaction, member: discord.Member, duration: app_commands.Choice[str], reason: str = "Sin razón especificada"):
    modal = BanModal(member=member, duration=duration.value, reason=reason)
    await interaction.response.send_modal(modal)

@bot.tree.command(name="kick", description="Expulsa a un usuario del servidor.")
@app_commands.describe(member="Usuario a expulsar", reason="Razón de la expulsión")
async def slash_kick(interaction: discord.Interaction, member: discord.Member, reason: str = "Sin razón"):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
        return
    
    await member.kick(reason=reason)
    await interaction.response.send_message(f"✅ {member.mention} fue expulsado. Razón: {reason}")

@bot.tree.command(name="limpiar", description="Borra una cantidad específica de mensajes.")
@app_commands.describe(cantidad="Número de mensajes a borrar (1-100)")
async def slash_limpiar(interaction: discord.Interaction, cantidad: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ No tienes permisos para gestionar mensajes.", ephemeral=True)
        return
    
    await interaction.channel.purge(limit=cantidad + 1)
    await interaction.response.send_message(f"🧹 Se han eliminado {cantidad} mensajes.", ephemeral=True)


# --- 4. CREACIÓN DE CANALES, ROLES Y COPIA DE SEGURIDAD (BACKUP) ---
@bot.tree.command(name="setup_bompa", description="Crea los canales y roles iniciales para Los Bompas (Solo Admin).")
async def setup_bompa(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Necesitas ser Administrador para ejecutar esto.", ephemeral=True)
        return

    await interaction.response.defer(thinking=True)
    guild = interaction.guild

    roles_a_crear = [
        {"name": "Owner 👑", "color": discord.Color.red()},
        {"name": "Admin 🛡️", "color": discord.Color.gold()},
        {"name": "Moderador ⚔️", "color": discord.Color.blue()},
        {"name": "Miembro Pro ⭐", "color": discord.Color.green()}
    ]
    
    for r in roles_a_crear:
        if not discord.utils.get(guild.roles, name=r["name"]):
            await guild.create_role(name=r["name"], color=r["color"])

    categoria = await guild.create_category("— 【 🎮 】 ROBLOX RIVALS —")
    canales = ["general-rivals", "clips-y-jugadas", "anuncios", "bienvenida"]
    for canal_nombre in canales:
        if not discord.utils.get(guild.text_channels, name=canal_nombre):
            await guild.create_text_channel(canal_nombre, category=categoria)

    await interaction.followup.send("✅ ¡Estructura de canales, roles y configuración inicial de **Los Bompas** creada con éxito!")


@bot.tree.command(name="backup", description="Genera una copia de seguridad rápida de la estructura del servidor.")
async def backup_server(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Necesitas permisos de Administrador.", ephemeral=True)
        return

    guild = interaction.guild
    backup_texto = f"=== COPIA DE SEGURIDAD: {guild.name} ===\n\nROLES:\n"
    
    for role in guild.roles:
        if role.name != "@everyone":
            backup_texto += f"- {role.name} (Color: {role.color})\n"
            
    backup_texto += "\nCANALES DE TEXTO:\n"
    for channel in guild.text_channels:
        backup_texto += f"- #{channel.name} (Categoría: {channel.category.name if channel.category else 'Ninguna'})\n"

    file = discord.File(fp=BytesIO(backup_texto.encode('utf-8')), filename=f"backup_{guild.name}.txt")
    await interaction.response.send_message("📁 Aquí tienes la copia de seguridad de la estructura del servidor:", file=file, ephemeral=True)

# Ejecutar el bot de forma segura
TOKEN = os.getenv("MTU1MzgwOTU5MTk2MjQ0Mzg3Nw.GZB1dB.kAXKLkYiF9pMiVGhgVSxq7odrLEhV2AOCLeg8Y")
if not TOKEN:
    print("⚠️ ADVERTENCIA: No se encontró la variable de entorno 'DISCORD_TOKEN'.")
else:
    bot.run(TOKEN)
