import os
import hikari
import lightbulb
import asyncio
from dotenv import load_dotenv, find_dotenv

load_dotenv(dotenv_path=find_dotenv(usecwd=True))

bot = lightbulb.BotApp(
	os.environ.get('DISCORD_TOKEN'),
    intents=hikari.Intents.ALL,
)

@bot.command
@lightbulb.command("ping", description = "Returns bot's latency")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def ping(ctx: lightbulb.Context) -> None:
	await ctx.respond(f"Pong! Latency: {bot.heartbeat_latency * 1000:.2f}ms")

if __name__ == "__main__":
	# Checking if host is *nix OS
	if os.name != "nt":
		import uvloop
		uvloop.install()

	bot.load_extensions_from("./plugins/", must_exist=True)
	bot.run()