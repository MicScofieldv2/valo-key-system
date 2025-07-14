import discord
from discord.ext import commands
import time

TOKEN = "MTM5NDI3MzEyOTk1Mzc1OTM2Mw.GbdFhL.Vfg9KC4BJy-iLvVeTngz8EZOdIc33cLIAMktyo"
ACCOUNTS_FILE = "accounts.txt"
VALID_CHANNEL_ID = 1394274345198682226  # Hedef kanal ID

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)

cooldown_map = {}  # (user_id, channel_id): timestamp
COOLDOWN_SECONDS = 15 * 60  # 15 dakika

def get_accounts():
    try:
        with open(ACCOUNTS_FILE, "r") as f:
            lines = f.read().splitlines()
        return [line for line in lines if line.strip()]
    except FileNotFoundError:
        return []

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, "w") as f:
        f.write("\n".join(accounts))

@bot.event
async def on_ready():
    print(f"{bot.user} olarak giriş yapıldı!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id != VALID_CHANNEL_ID:
        return

    now = time.time()
    key = (message.author.id, message.channel.id)

    if key in cooldown_map:
        diff = now - cooldown_map[key]
        if diff < COOLDOWN_SECONDS:
            kalan = int((COOLDOWN_SECONDS - diff) // 60)
            await message.channel.send(
                f"{message.author.mention}, bu kanalda tekrar yazabilmek için **{kalan} dakika** beklemelisin."
            )
            return

    if message.content.strip() == ".acc":
        accounts = get_accounts()
        if not accounts:
            await message.channel.send(f"{message.author.mention}, maalesef hesap kalmadı.")
            return

        account = accounts.pop(0)
        try:
            username, password = account.split(":", 1)
            msg = (
                "🎉 Hesabın hazır!\n\n"
                f"🧑 Kullanıcı Adı: `{username}`\n"
                f"🔑 Şifre: `{password}`\n\n"
                "⚡ İyi kullanımlar!"
            )
            await message.author.send(msg)
            save_accounts(accounts)

            await message.channel.send(
                f"{message.author.mention}, hesabın DM'den gönderildi!\n📦 Stok: **{len(accounts)}** hesap kaldı."
            )
        except Exception as e:
            await message.channel.send(f"{message.author.mention}, bir hata oluştu: {e}")

    # Her ne yazarsa yazsın, o kullanıcıya 15 dakikalık kanal cooldown koy
    cooldown_map[key] = now

    await bot.process_commands(message)

bot.run(TOKEN)
