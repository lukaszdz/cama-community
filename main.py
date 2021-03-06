""" FastAPI App for Camaraderous Community """

import asyncio
import ctypes
import logging
import os
import os.path
import random
import string
import time
from datetime import datetime

import discord  # type: ignore
import uvicorn  # type: ignore
from discord.ext.commands import Bot  # type: ignore
from fastapi import FastAPI, Request  # type: ignore
from fastapi_cache import caches, close_caches  # type: ignore
from fastapi_cache.backends.redis import CACHE_KEY, RedisCacheBackend  # type: ignore
from pydantic import BaseModel
from redis import Redis

import responses
from meme import build_meme, find_meme
from sheets import (
    distribute_coin_to_camarron_with_name,
    get_balance_for_name,
    spend_coin,
)

logging.basicConfig(
    format="%(custom_attribute)s:%(levelname)s\t%(asctime)s\t%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
old_factory = logging.getLogRecordFactory()


def record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    record.custom_attribute = os.environ["ENV"].upper()
    return record


logging.setLogRecordFactory(record_factory)
logger = logging.getLogger()


class InteractionType:
    PING = 1


class InteractionResponseType:
    PONG = 1


class Ping(BaseModel):
    type: int


api = FastAPI(debug=True)


@api.middleware("http")
async def add_process_time_header(request: Request, call_next):
    idem = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    await dlog(f"rid={idem} start request path={request.url.path}")
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    formatted_process_time = "{0:.2f}".format(process_time)
    await dlog(
        f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}"
    )
    response.headers["X-Process-Time"] = str(process_time)
    return response


intents = discord.Intents.default()
intents.members = False


bot = Bot(command_prefix=os.environ["BOT_COMMAND_PREFIX"].strip(), intents=intents)


async def dlog(msg):
    logger.info(msg)
    try:
        channel = bot.get_channel(int(os.environ["DISCORD_LOGGING_CHANNEL"]))
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        fmt_msg = f"{os.environ['ENV'].upper()}:INFO\t{dt_string}\t{msg}"
        await channel.send(fmt_msg)
    except Exception as e:
        logger.error(f"Unable to log to discord: {str(e)}")


@bot.check
async def debugging_middleware(ctx):
    log_msg = f"{ctx.author.name} requested {ctx.invoked_with} from {ctx.me.name}"
    await dlog(log_msg)
    return True


@bot.event
async def on_ready():
    await dlog(f"Logged in as {bot.user.name}")


def test_redis_connection():
    r = Redis.from_url(
        os.environ["REDIS_URL"], socket_connect_timeout=1
    )  # short timeout for the test
    r.ping()


def redis_cache():
    return caches.get(CACHE_KEY)


async def make_noise_in_current_channel(context, sound_file):
    try:
        noise_channel = context.author.voice.channel
        if noise_channel is not None:
            if context.voice_client is not None:
                await context.voice_client.move_to(noise_channel)
            else:
                await noise_channel.connect()

        audio_source = discord.FFmpegOpusAudio(sound_file)
        if not context.voice_client.is_playing():
            context.voice_client.play(audio_source, after=None)
    except Exception as e:
        dlog(f"Error playing sound file: {str(e)}")


async def play_cash_register(context):
    await make_noise_in_current_channel(
        context, "./sounds/CashRegisterOpen_SFXB.2496.wav"
    )


async def play_blacksmith(context):
    await make_noise_in_current_channel(
        context,
        "./sounds/SPLC-5315_FX_Oneshot_Blacksmith_Metal_Hits_Resonant_Water.wav",
    )


async def play_scream(context):
    await make_noise_in_current_channel(
        context,
        "./sounds/WilhelmScream.wav",
    )


@bot.command(name="spend")
async def _spend(ctx):
    author_roles = [r.name for r in ctx.author.roles]
    feeling_sassy = random.randint(0, 100) > 95
    if feeling_sassy and "Gold" not in author_roles and "admin" not in author_roles:
        await ctx.send(random.choice(responses.PISSED))
        return

    successfully_spent = spend_coin(ctx.author.display_name)
    if successfully_spent:
        await play_cash_register(ctx)
        await ctx.send("Transaction complete.")
    else:
        await ctx.send("Insufficient JopaCoin(s) for transaction.")


@bot.command(name="tip")
async def _tip(ctx):
    author_roles = [r.name for r in ctx.author.roles]
    feeling_sassy = random.randint(0, 100) > 95
    if feeling_sassy and "Gold" not in author_roles and "admin" not in author_roles:
        await ctx.send(random.choice(responses.PISSED))
        return
    mentions = ctx.message.mentions
    if len(mentions) == 0:
        successfully_spent = spend_coin(ctx.author.display_name)
        await ctx.send("You tipped nobody, and lost a coin! XD")
        return
    if len(mentions) > 1:
        await ctx.send("You can only tip a JopaCoin to one person!")
        return
    else:
        successfully_spent = spend_coin(ctx.author.display_name)
        if successfully_spent:
            mention = mentions[0]
            distribute_coin_to_camarron_with_name(mention.display_name)
            await play_cash_register(ctx)
            await ctx.send(f"Tipped {mention} a JopaCoin!")
        else:
            await ctx.send("Insufficient JopaCoin(s) for transaction.")


@bot.command(name="reserves")
async def _reserves(ctx):
    author_roles = [r.name for r in ctx.author.roles]
    feeling_sassy = random.randint(0, 100) > 95
    if feeling_sassy and "Gold" not in author_roles and "admin" not in author_roles:
        await ctx.send(random.choice(responses.PISSED))
        return
    balance = get_balance_for_name("TREASURY")
    await ctx.send(f"{balance}")


@bot.command(name="balance")
async def _balance(ctx):
    author_roles = [r.name for r in ctx.author.roles]
    feeling_sassy = random.randint(0, 100) > 95
    if feeling_sassy and "Gold" not in author_roles and "admin" not in author_roles:
        await ctx.send(random.choice(responses.PISSED))
        return

    mentions = ctx.message.mentions
    if len(mentions) > 0:
        mentioned_names = [c.display_name for c in mentions]
        for mentioned_name in mentioned_names:
            await ctx.send(f"{mentioned_name}: {get_balance_for_name(mentioned_name)}")
    else:
        await ctx.send(get_balance_for_name(ctx.author.display_name))


@bot.command(name="mint")
async def _mint(ctx, arg):
    cache = caches.get(CACHE_KEY)
    author_command_cache_key = f"command-mint-{ctx.author.display_name}"
    in_cache = await cache.get(author_command_cache_key)
    if not in_cache:
        expiration_seconds = 60 * 12
        await cache.set(author_command_cache_key, "value", expire=expiration_seconds)
    else:
        await ctx.send(random.choice(responses.WHAT))
        return

    author_roles = [r.name for r in ctx.author.roles]
    feeling_sassy = random.randint(0, 100) > 70
    if feeling_sassy and "Gold" not in author_roles and "admin" not in author_roles:
        await ctx.send(random.choice(responses.PISSED))
        return

    if "balance" in arg:
        mentions = ctx.message.mentions
        if len(mentions) > 0:
            mentioned_names = [c.display_name for c in mentions]
            for mentioned_name in mentioned_names:
                await ctx.send(
                    f"{mentioned_name}: {get_balance_for_name(mentioned_name)}"
                )
        else:
            await ctx.send(get_balance_for_name(ctx.author.display_name))
        return

    mentions = ctx.message.mentions
    if len(mentions) > 0:
        mentioned_names = [c.display_name for c in mentions]
        author_name = ctx.author.display_name
        if author_name in mentioned_names:
            await ctx.send(random.choice(responses.PISSED))
            return

        await ctx.send(random.choice(responses.ACTION))

        for idx, mention in enumerate(mentions):
            if idx > 2:
                return
            distribute_coin_to_camarron_with_name(mention.display_name)
            await play_blacksmith(ctx)


@bot.command(name="scream")
async def _scream(ctx):
    author_roles = [r.name for r in ctx.author.roles]
    feeling_sassy = random.randint(0, 100) > 50
    if feeling_sassy and "Gold" not in author_roles and "admin" not in author_roles:
        await ctx.send(random.choice(responses.PISSED))
        return

    await play_scream(ctx)
    await ctx.send(random.choice(responses.SCREAM))


@bot.command(name="ping")
async def _ping(ctx):
    await ctx.send(random.choice(responses.READY))


@bot.command(name="hello")
async def _hello(ctx):
    await ctx.send("Hello, John")


@bot.command(name="hi")
async def _hello(ctx):
    await ctx.send("Well, hi there")


@bot.command(name="mmm")
async def _mmm(ctx, arg):
    message = ctx.message.content.split(
        f"{os.environ['BOT_COMMAND_PREFIX'].strip()}mmm"
    )[1].strip()
    if "says" not in message:
        await ctx.send("What do they say?")
        return

    search_term = message.split("says")[0].strip()
    meme_text = message.split("says")[1].strip()
    if "/" not in meme_text:
        await ctx.send("Gotta split meme text with dat slash (/)")
        return

    meme_top_text = meme_text.split("/")[0].strip()
    meme_bot_text = meme_text.split("/")[1].strip()
    meme = find_meme(search_term)
    if meme is None:
        await ctx.send(
            f"Your meme ({search_term}) isn't in the library yet (https://github.com/lukaszdz/cama-community/blob/main/meme.py)"
        )
        return

    try:
        img = build_meme(meme["templateID"], meme_top_text, meme_bot_text)
        await ctx.send(img)
    except Exception:
        await ctx.send(random.choice(responses.PISSED))


@api.get("/")
def base():
    return {"message": "Systems online."}


@api.post("/")
def base(ping):
    if ping.type == InteractionType.PING:
        return {"type": InteractionResponseType.PONG}
    else:
        return {
            "type": 4,
            "data": {
                "tts": False,
                "content": "Congrats on sending your command!",
                "embeds": [],
                "allowed_mentions": {"parse": []},
            },
        }


async def load_opus():
    try:
        opus_path = ctypes.util.find_library("opus")
        discord.opus.load_opus(opus_path)
    except Exception:
        dlog("Failed to initialize opus (for playing audio)")


@api.on_event("startup")
async def startup_event():
    asyncio.create_task(bot.start(os.environ["DISCORD_BOT_TOKEN"]))
    await load_opus()
    test_redis_connection()
    redis_cache_backend = RedisCacheBackend(os.environ["REDIS_URL"])
    caches.set(CACHE_KEY, redis_cache_backend)

    await asyncio.sleep(4)  # optional sleep for established connection with discord
    await dlog(f"{bot.user} has connected to Discord!")


@api.on_event("shutdown")
async def on_shutdown() -> None:
    await dlog("Shutting down.")
    await close_caches()


if __name__ == "__main__":
    import doctest

    doctest.testmod()
    test_redis_connection()

    if os.environ.get("ENV") == "prod":
        uvicorn.run("main:api", host="0.0.0.0", port=8001, reload=True)
    else:
        uvicorn.run("main:api", host="0.0.0.0", port=8000, reload=True)
