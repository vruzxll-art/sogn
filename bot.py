import discord
from discord.ext import commands
from discord import app_commands
import os

# ===== KEEP ALIVE (Render Web Service) =====
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
# ===========================================

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
ADMIN_CHANNEL_ID = int(os.getenv("ADMIN_CHANNEL_ID"))
# ==========================================

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -------- MODAL (FORM) --------
class RegistrationModal(discord.ui.Modal, title="Member Registration Form"):
    roblox_username = discord.ui.TextInput(label="Roblox Username", required=True)
    display_name = discord.ui.TextInput(label="Roblox Display Name", required=True)
    timezone = discord.ui.TextInput(label="Timezone (e.g., UTC, GMT+2)", required=True)
    account_age = discord.ui.TextInput(label="Roblox Account Age Group (13+ / <13)", required=True)
    pronouns = discord.ui.TextInput(label="Pronouns (Optional)", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        admin_channel = bot.get_channel(ADMIN_CHANNEL_ID)

        embed = discord.Embed(
            title="📥 New Registration Submission",
            color=discord.Color.blue()
        )

        embed.add_field(name="Roblox Username", value=self.roblox_username.value, inline=False)
        embed.add_field(name="Display Name", value=self.display_name.value, inline=False)
        embed.add_field(name="Timezone", value=self.timezone.value, inline=True)
        embed.add_field(name="Account Age Group", value=self.account_age.value, inline=True)
        embed.add_field(name="Pronouns", value=self.pronouns.value or "Not provided", inline=True)

        embed.set_footer(text=f"Submitted by {interaction.user} | ID: {interaction.user.id}")

        await admin_channel.send(embed=embed)
        await interaction.response.send_message("✅ Your registration has been submitted!", ephemeral=True)

# -------- BUTTON --------
class RegisterView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Register", style=discord.ButtonStyle.green)
    async def register_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RegistrationModal())

# -------- SLASH COMMAND (FINAL FIX) --------
@bot.tree.command(name="setup_register", description="Send the registration button")
async def setup_register(interaction: discord.Interaction):
    await interaction.response.send_message("⏳ Setting up...", ephemeral=True)

    view = RegisterView()
    await interaction.channel.send("Click below to register:", view=view)

# -------- READY --------
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
