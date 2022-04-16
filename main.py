""" FastAPI App for Camaraderous Community """

import asyncio
import ctypes
import os
import os.path
import random

import discord  # type: ignore
import uvicorn  # type: ignore
from discord.ext.commands import Bot  # type: ignore
from dotenv import dotenv_values
from fastapi import FastAPI, HTTPException, Request, status  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.security import HTTPBasic
from fastapi_cache import caches, close_caches  # type: ignore
from fastapi_cache.backends.redis import CACHE_KEY, RedisCacheBackend  # type: ignore
from nacl.signing import VerifyKey
from pydantic import BaseModel

import responses
from sheets import (
    distribute_coin_to_camarron_with_name,
    get_balance_for_name,
    spend_coin,
)


class InteractionType:
    PING = 1


class InteractionResponseType:
    PONG = 1


class Ping(BaseModel):
    type: int


try:
    CONFIG = dotenv_values(".env")
except:
    CONFIG = dict(os.environ)

AUDIO_ENABLED = CONFIG.get("AUDIO_ENABLED") == 1

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()

intents = discord.Intents.default()
intents.members = False


bot = Bot(command_prefix="$", intents=intents)


def redis_cache():
    return caches.get(CACHE_KEY)


@bot.command(name="spend")
async def _spend(ctx):
    author_roles = [r.name for r in ctx.author.roles]
    feeling_sassy = random.randint(0, 100) > 95
    if feeling_sassy and "Gold" not in author_roles and "admin" not in author_roles:
        await ctx.send(random.choice(responses.PISSED))
        return

    successfully_spent = spend_coin(ctx.author.display_name)
    if successfully_spent:
        if AUDIO_ENABLED:
            noise_channel = ctx.author.voice.channel
            if noise_channel is not None:
                if ctx.voice_client is not None:
                    await ctx.voice_client.move_to(noise_channel)
                else:
                    await noise_channel.connect()

            audio_source = discord.FFmpegOpusAudio(
                "./audio/CashRegisterOpen_SFXB.2496.wav"
            )
            if not ctx.voice_client.is_playing():
                ctx.voice_client.play(audio_source, after=None)

        await ctx.send("Transaction complete.")
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
        if AUDIO_ENABLED:
            noise_channel = ctx.author.voice.channel
            if noise_channel is not None:
                if ctx.voice_client is not None:
                    await ctx.voice_client.move_to(noise_channel)
                else:
                    await noise_channel.connect()

        for idx, mention in enumerate(mentions):
            if idx > 2:
                return
            if AUDIO_ENABLED:
                audio_source = discord.FFmpegOpusAudio(
                    "./audio/SPLC-5315_FX_Oneshot_Blacksmith_Metal_Hits_Resonant_Water.wav"
                )
                if not ctx.voice_client.is_playing():
                    ctx.voice_client.play(audio_source, after=None)

            distribute_coin_to_camarron_with_name(mention.display_name)


@bot.command(name="ping")
async def _ping(ctx):
    await ctx.send(random.choice(responses.READY))


@bot.command(name="hello")
async def _hello(ctx):
    await ctx.send("Hello, John")


@app.get("/")
def base():
    return {"message": "Systems online."}


##
# Makes sure the request was sent from Discord
# https://discord.com/developers/docs/interactions/receiving-and-responding#security-and-authorization
#
def verify_request_from_discord(
    raw_body: bytes, signature: str, timestamp: str, client_public_key: str
) -> bool:
    if not signature or not timestamp or not client_public_key:
        return False

    message = timestamp.encode() + raw_body
    try:
        verify_key = VerifyKey(bytes.fromhex(client_public_key))
        verify_key.verify(message, bytes.fromhex(signature))
        return True
    except Exception as exception:
        print(exception)
    return False


@app.post("/interactions", status_code=200)
async def interactions(ping: Ping, request: Request):
    request_body = b""
    async for chunk in request.stream():
        request_body += chunk
    if not verify_request_from_discord(
        raw_body=request_body,
        signature=request.headers.get("X-Signature-Ed25519"),
        timestamp=request.headers.get("X-Signature-Timestamp"),
        client_public_key=str(CONFIG.get("DISCORD_APP_PUBLIC_KEY", "")),
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )

    if ping.type == InteractionType.PING:
        return {"type": InteractionResponseType.PONG}


@app.on_event("startup")
async def startup_event():
    opus_path = ctypes.util.find_library("opus")
    discord.opus.load_opus(opus_path)
    asyncio.create_task(bot.start(CONFIG.get("DISCORD_BOT_TOKEN")))
    redis_cache_backend = RedisCacheBackend(CONFIG["REDIS_URL"])
    caches.set(CACHE_KEY, redis_cache_backend)
    print("Backend locked & loaded.")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await close_caches()


if __name__ == "__main__":
    import doctest

    doctest.testmod()

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)