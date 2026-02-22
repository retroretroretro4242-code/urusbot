import os
import discord
from discord.ext import commands
from discord import app_commands
import random

TOKEN = os.environ["TOKEN"]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

YETKILI_ROLLER = [
    1474568875634065428,
    1425485552504799341,
    1425962500351856693,
    1472172964198744210,
    1425485552504799342
]

class HileModal(discord.ui.Modal, title="Hile Paylaşım Formu"):
    isim = discord.ui.TextInput(label="Hile İsmi", max_length=100)
    surum = discord.ui.TextInput(label="Hile Sürümü", max_length=50)
    aciklama = discord.ui.TextInput(label="Açıklama", style=discord.TextStyle.paragraph, max_length=500)
    foto = discord.ui.TextInput(label="Hile Foto Linki", placeholder="https://", max_length=200)
    link = discord.ui.TextInput(label="Hile Linki", placeholder="https://", max_length=200)
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🧪 Hile Paylaşımı | Project", color=0xe74c3c)
        embed.add_field(name="Hile İsmi", value=self.isim.value, inline=False)
        embed.add_field(name="Sürüm", value=self.surum.value, inline=False)
        embed.add_field(name="Açıklama", value=self.aciklama.value, inline=False)
        embed.add_field(name="Link", value=self.link.value, inline=False)
        embed.set_image(url=self.foto.value)
        await interaction.response.send_message(embed=embed)

class PackModal(discord.ui.Modal, title="Pack Paylaşım Formu"):
    isim = discord.ui.TextInput(label="Pack İsmi", max_length=100)
    surum = discord.ui.TextInput(label="Pack Sürümü", max_length=50)
    foto = discord.ui.TextInput(label="Pack Foto Linki", placeholder="https://", max_length=200)
    link = discord.ui.TextInput(label="Pack Linki", placeholder="https://", max_length=200)
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📦 Pack Paylaşımı | Project", color=0x3498db)
        embed.add_field(name="Pack İsmi", value=self.isim.value, inline=False)
        embed.add_field(name="Sürüm", value=self.surum.value, inline=False)
        embed.add_field(name="Link", value=self.link.value, inline=False)
        embed.set_image(url=self.foto.value)
        await interaction.response.send_message(embed=embed)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot hazır: {bot.user}")

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="giris-cikis")
    if channel:
        await channel.send(f"👋 Hoş geldin {member.mention}! | Project Üye sayısı: {member.guild.member_count}")

@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.text_channels, name="giris-cikis")
    if channel:
        await channel.send(f"👋 {member.name} ayrıldı | Project Üye sayısı: {member.guild.member_count}")

BAD_WORDS = ["küfür1","küfür2"]

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if len(message.content) > 6 and message.content.isupper():
        await message.delete()
        await message.channel.send(f"{message.author.mention} CAPS LOCK kapalı pls 😄", delete_after=5)
    for word in BAD_WORDS:
        if word in message.content.lower():
            await message.delete()
            await message.channel.send(f"{message.author.mention} küfür yasak ❌", delete_after=5)
    await bot.process_commands(message)

def kullanici_yetkili(mi):
    def predicate(interaction: discord.Interaction):
        return any(role.id in YETKILI_ROLLER for role in interaction.user.roles)
    return app_commands.check(predicate)

@bot.tree.command(name="hilepaylas", description="Hile paylaşım formu açar")
@kullanici_yetkili(True)
async def hilepaylas(interaction: discord.Interaction):
    await interaction.response.send_modal(HileModal())

@bot.tree.command(name="packpaylas", description="Pack paylaşım formu açar")
@kullanici_yetkili(True)
async def packpaylas(interaction: discord.Interaction):
    await interaction.response.send_modal(PackModal())

@bot.tree.command(name="sec", description="Rastgele seçim yapar")
@app_commands.describe(secenekler="Virgülle ayır")
async def sec(interaction: discord.Interaction, secenekler: str):
    secenek_list = [s.strip() for s in secenekler.split(",") if s.strip()]
    if not secenek_list:
        await interaction.response.send_message("En az bir seçenek yaz.")
        return
    await interaction.response.send_message(f"🎯 Seçilen: **{random.choice(secenek_list)}**")

@bot.tree.command(name="cekilis", description="Çekiliş başlatır")
@app_commands.describe(odul="Çekiliş ödülü")
async def cekilis(interaction: discord.Interaction, odul: str):
    await interaction.response.send_message(f"🎉 ÇEKİLİŞ BAŞLADI! Ödül: **{odul}** ")

@bot.tree.command(name="eglence", description="Rastgele eğlence mesajı")
async def eglence(interaction: discord.Interaction):
    sozler = ["Bugün şanslı günün ","Bir blok daha kır ","Admin seni izliyor "]
    await interaction.response.send_message(random.choice(sozler))

@hilepaylas.error
@packpaylas.error
async def modal_yetki_hatasi(interaction: discord.Interaction, error):
    from discord import app_commands
    if isinstance(error, app_commands.errors.CheckFailure):
        await interaction.response.send_message("Bu komutu kullanmak için yetkiniz yok ❌", ephemeral=True)

bot.run(TOKEN)
