import os
import discord
from discord.ext import commands, tasks
from discord import app_commands, ui
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

# --- Anti-spam / anti-küfür ---
BAD_WORDS = ["küfür1","küfür2"]

# --- Çekilişler / sec katılım ---
active_giveaways = {}  # {message_id: {"katilanlar": set(), "kazanan_id": int, "odul": str}}

# --- Modallar ---
class HileModal(ui.Modal, title="Hile Paylaşım Formu"):
    isim = ui.TextInput(label="Hile İsmi", max_length=100)
    surum = ui.TextInput(label="Hile Sürümü", max_length=50)
    aciklama = ui.TextInput(label="Açıklama", style=discord.TextStyle.paragraph, max_length=500)
    foto = ui.TextInput(label="Hile Foto Linki", placeholder="https://", max_length=200)
    link = ui.TextInput(label="Hile Linki", placeholder="https://", max_length=200)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🧪 Hile Paylaşımı | Project", color=0xe74c3c)
        embed.add_field(name="Hile İsmi", value=self.isim.value, inline=False)
        embed.add_field(name="Sürüm", value=self.surum.value, inline=False)
        embed.add_field(name="Açıklama", value=self.aciklama.value, inline=False)
        embed.set_image(url=self.foto.value)
        button = ui.Button(label="İndir", url=self.link.value, style=discord.ButtonStyle.link)
        view = ui.View()
        view.add_item(button)
        await interaction.response.send_message(embed=embed, view=view)

class PackModal(ui.Modal, title="Pack Paylaşım Formu"):
    isim = ui.TextInput(label="Pack İsmi", max_length=100)
    surum = ui.TextInput(label="Pack Sürümü", max_length=50)
    foto = ui.TextInput(label="Pack Foto Linki", placeholder="https://", max_length=200)
    link = ui.TextInput(label="Pack Linki", placeholder="https://", max_length=200)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📦 Pack Paylaşımı | Project", color=0x3498db)
        embed.add_field(name="Pack İsmi", value=self.isim.value, inline=False)
        embed.add_field(name="Sürüm", value=self.surum.value, inline=False)
        embed.set_image(url=self.foto.value)
        button = ui.Button(label="İndir", url=self.link.value, style=discord.ButtonStyle.link)
        view = ui.View()
        view.add_item(button)
        await interaction.response.send_message(embed=embed, view=view)

# --- Yetkili kontrol ---
def kullanici_yetkili(mi):
    def predicate(interaction: discord.Interaction):
        return any(role.id in YETKILI_ROLLER for role in interaction.user.roles)
    return app_commands.check(predicate)

# --- Events ---
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot hazır: {bot.user}")

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="giris-cikis")
    if channel:
        await channel.send(f"👋 Hoş geldin {member.mention}! | Üye sayısı: {member.guild.member_count}")

@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.text_channels, name="giris-cikis")
    if channel:
        await channel.send(f"👋 {member.name} ayrıldı | Üye sayısı: {member.guild.member_count}")

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

# --- Slash commands ---
@bot.tree.command(name="hilepaylas", description="Hile paylaşım formu açar")
@kullanici_yetkili(True)
async def hilepaylas(interaction: discord.Interaction):
    await interaction.response.send_modal(HileModal())

@bot.tree.command(name="packpaylas", description="Pack paylaşım formu açar")
@kullanici_yetkili(True)
async def packpaylas(interaction: discord.Interaction):
    await interaction.response.send_modal(PackModal())

@bot.tree.command(name="eglence", description="Rastgele eğlence mesajı")
async def eglence(interaction: discord.Interaction):
    sozler = ["Bugün şanslı günün 😎","Bir blok daha kır 💎","Admin seni izliyor 👀"]
    await interaction.response.send_message(random.choice(sozler))

# --- Sec ve Cekilis komutları ---
class KatilButton(ui.View):
    def __init__(self, msg_id, kazanan_id=None):
        super().__init__(timeout=None)
        self.msg_id = msg_id
        self.kazanan_id = kazanan_id

    @ui.button(label="Katıl", style=discord.ButtonStyle.green, custom_id="katil_button")
    async def katil(self, interaction: discord.Interaction, button: ui.Button):
        data = active_giveaways.get(self.msg_id)
        if not data:
            return await interaction.response.send_message("❌ Geçersiz çekiliş!", ephemeral=True)
        data["katilanlar"].add(interaction.user.id)
        await interaction.response.send_message("✅ Katıldın!", ephemeral=True)

@bot.tree.command(name="sec", description="Rastgele seçim yapar (butonlu)")
@app_commands.describe(secenekler="Virgülle ayır")
async def sec(interaction: discord.Interaction, secenekler: str):
    secenek_list = [s.strip() for s in secenekler.split(",") if s.strip()]
    if not secenek_list:
        await interaction.response.send_message("En az bir seçenek yaz.")
        return

    # Kazananı rastgele seç (isteğe bağlı)
    kazanan_id = random.choice([interaction.user.id])  # default senin seçtiğin kişi yerine koyabilirsin

    # Embed ve buton
    embed = discord.Embed(title="🎯 Sec Katılım", description="Butona basarak katıl!", color=0xffc107)
    view = KatilButton(interaction.id, kazanan_id)
    active_giveaways[interaction.id] = {"katilanlar": set(), "kazanan_id": kazanan_id}
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="cekilis", description="Çekiliş başlatır")
@app_commands.describe(odul="Çekiliş ödülü", kazanan="Seçilen kişi ID")
async def cekilis(interaction: discord.Interaction, odul: str, kazanan: discord.Member):
    embed = discord.Embed(title=f"🎉 ÇEKİLİŞ! Ödül: {odul}", description="Butona basarak katılabilirsiniz", color=0x00ff00)
    view = KatilButton(interaction.id, kazanan.id)
    active_giveaways[interaction.id] = {"katilanlar": set(), "kazanan_id": kazanan.id, "odul": odul}
    await interaction.response.send_message(embed=embed, view=view)

# --- Error handling ---
@hilepaylas.error
@packpaylas.error
async def modal_yetki_hatasi(interaction: discord.Interaction, error):
    from discord import app_commands
    if isinstance(error, app_commands.errors.CheckFailure):
        await interaction.response.send_message("Bu komutu kullanmak için yetkiniz yok ❌", ephemeral=True)

bot.run(TOKEN)
