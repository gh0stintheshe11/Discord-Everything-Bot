import asyncio
from functools import wraps
import discord

# Decorators
def delete_user_msg_after(seconds):
    def decorator(func):
        @wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            result = await func(ctx, *args, **kwargs)
            await asyncio.sleep(seconds)
            await ctx.message.delete()
            return result
        return wrapper
    return decorator

def delete_bot_msg_after(seconds):
    def decorator(func):
        @wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            response = await func(ctx, *args, **kwargs)
            if isinstance(response, discord.Message):
                await asyncio.sleep(seconds)
                await response.delete()
            return response
        return wrapper
    return decorator
