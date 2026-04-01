import discord
from discord.ext import commands
from discord import app_commands
import os

# ===== KEEP ALIVE =====
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ======================

# ===== CONFIG =====
TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
ADMIN_CHANNEL_ID = int(os.getenv("ADMIN_CHANNEL_ID"))
# ==================

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ===== ACCEPT / DENY VIEW =====
class ReviewView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.add_field(name="Status", value=f"✅ Accepted by {interaction.user}", inline=False)

        await interaction.message.edit(embed=embed, view=None)
        await interaction.response.send_message("Application accepted.", ephemeral=True)

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()
        embed.add_field(name="Status", value=f"❌ Denied by {interaction.user}", inline=False)

        await interaction.message.edit(embed=embed, view=None)
        await interaction.response.send_message("Application denied.", ephemeral=True)

# ===== MODAL =====
class RegistrationModal(discord.ui.Modal, title="📋 Member Application"):
    roblox_username = discord.ui.TextInput(label="Roblox Username", required=True)
    display_name = discord.ui.TextInput(label="Display Name", required=True)
    timezone = discord.ui.TextInput(label="Timezone", required=True)
    availability = discord.ui.TextInput(label="Availability (e.g. Weekends 3-6PM UTC)", required=True)
    account_age = discord.ui.TextInput(label="Account Age (13+ / <13)", required=True)
    pronouns = discord.ui.TextInput(label="Pronouns (Optional)", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        admin_channel = bot.get_channel(ADMIN_CHANNEL_ID)

        embed = discord.Embed(
            title="📥 New Application",
            color=discord.Color.blurple()
        )

        embed.add_field(name="👤 User", value=f"{interaction.user} ({interaction.user.id})", inline=False)
        embed.add_field(name="Roblox Username", value=self.roblox_username.value, inline=True)
        embed.add_field(name="Display Name", value=self.display_name.value, inline=True)
        embed.add_field(name="Timezone", value=self.timezone.value, inline=True)
        embed.add_field(name="Availability", value=self.availability.value, inline=False)
        embed.add_field(name="Account Age", value=self.account_age.value, inline=True)
        embed.add_field(name="Pronouns", value=self.pronouns.value or "Not provided", inline=True)

        await admin_channel.send(embed=embed, view=ReviewView())
        await interaction.response.send_message("✅ Application submitted!", ephemeral=True)

# ===== BUTTON =====
class RegisterView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Register", style=discord.ButtonStyle.green)
    async def register(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RegistrationModal())

# ===== COMMAND =====
@bot.tree.command(name="setup_register", description="Setup the registration panel")
async def setup_register(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📋 Server Registration",
        description="Click the button below to apply.",
        color=discord.Color.blue()
    )

    await interaction.response.send_message("⏳ Setting up...", ephemeral=True)
    await interaction.channel.send(embed=embed, view=RegisterView())

# ===== READY =====
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

    print(f"Logged in as {bot.user}")

keep_alive()
bot.run(TOKEN)
