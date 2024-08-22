import discord
from discord.ext import commands
import asyncio  
from music import Music
from meme import Meme

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

async def load_cogs():
    await bot.add_cog(Music(bot))
    await bot.add_cog(Meme(bot))

async def main():
    await load_cogs()
    await bot.start('Your Bot Token')

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError:  
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())


