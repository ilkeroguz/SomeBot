import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

# yt-dlp seçenekleri
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.send(f'{channel} kanalına bağlandım.')
        else:
            await ctx.send("Bir ses kanalında değilsiniz!")

    @commands.command()
    async def play(self, ctx, url):
        try:
            if not ctx.author.voice:
                await ctx.send("Ses kanalında değilsin!")
                return

            channel = ctx.author.voice.channel
            voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

            if voice_client is None:
                await channel.connect()
                voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            voice_client.play(player, after=lambda e: print(f'Error: {e}') if e else None)

            await ctx.send(f'Çalınıyor: {player.title}')

        except Exception as e:
            await ctx.send(f"Bir hata oluştu: {str(e)}")

    @commands.command()
    async def stop(self, ctx):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await voice_client.disconnect()
            await ctx.send("Müzik durduruldu ve bot ses kanalından ayrıldı.")
        else:
            await ctx.send("Şu anda müzik çalmıyor.")

    @commands.command()
    async def pause(self, ctx):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await ctx.send("Müzik durduruldu.")
        else:
            await ctx.send("Şu anda müzik çalmıyor.")

    @commands.command()
    async def resume(self, ctx):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client:
            voice_client.resume()
            await ctx.send("Müzik devam ettirildi.")
        else:
            await ctx.send("Bir hata meydana geldi.")

    @commands.command()
    async def disconnect(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("Ses kanalından ayrıldım.")
        else:
            await ctx.send("Zaten bir ses kanalında değilim!")
