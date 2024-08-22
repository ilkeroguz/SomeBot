import discord
from discord.ext import commands
import asyncio  # asyncio modülü eklendi
from music import Music
from meme import Meme

# Bot'u tanımlama
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)

# Bot hazır olduğunda çağrılır
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

# Cogs eklemek için bir asenkron fonksiyon kullanıyoruz
async def load_cogs():
    await bot.add_cog(Music(bot))
    await bot.add_cog(Meme(bot))

# Ana fonksiyonu başlat
async def main():
    await load_cogs()
    await bot.start('Your Bot Token')

# Eğer mevcut bir etkinlik döngüsü varsa
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError:  # Eğer etkin bir event loop varsa
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())


