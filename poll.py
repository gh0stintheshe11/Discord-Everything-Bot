import discord
from discord.ext import commands
import uuid
import matplotlib.pyplot as plt
import asyncio
import os
from utils import delete_user_msg_after, delete_bot_msg_after

# Store poll data
poll_data = {}

def poll_commands(bot):
    @bot.command()
    async def poll(ctx, question: str, *options: str):
        if len(options) < 2:
            return await ctx.send('You need at least two options to start a poll.')
        if len(options) > 10:
            return await ctx.send('You cannot have more than 10 options in a poll.')

        poll_id = str(uuid.uuid4())[:8]
        poll_data[poll_id] = {
            'question': question,
            'options': options,
            'votes': {option: 0 for option in options},
            'voters': {},
            'active': True
        }

        description = '\n'.join([f'{i+1}. {option}' for i, option in enumerate(options)])
        embed = discord.Embed(title=f"Poll ID: {poll_id}\n{question}", description=description, color=discord.Color.blue())
        msg = await ctx.send(embed=embed)

        for i in range(len(options)):
            await msg.add_reaction(f'{i+1}\u20e3')

    @bot.event
    async def on_reaction_add(reaction, user):
        if user.bot:
            return

        for poll_id, poll in poll_data.items():
            if poll['active'] and reaction.message.embeds and f"Poll ID: {poll_id}" in reaction.message.embeds[0].title:
                options = poll['options']
                if reaction.emoji not in [f'{i+1}\u20e3' for i in range(len(options))]:
                    return

                # Remove previous reactions
                for other_reaction in reaction.message.reactions:
                    if other_reaction != reaction and user in await other_reaction.users().flatten():
                        await reaction.message.remove_reaction(other_reaction.emoji, user)
                        index = int(other_reaction.emoji[0]) - 1
                        previous_option = options[index]
                        poll['votes'][previous_option] -= 1

                index = int(reaction.emoji[0]) - 1
                option = options[index]

                poll['votes'][option] += 1
                poll['voters'][user.id] = option
                break

    @bot.command()
    async def endpoll(ctx, poll_id: str):
        if poll_id not in poll_data or not poll_data[poll_id]['active']:
            return await ctx.send('Invalid or already ended poll ID.')

        poll_data[poll_id]['active'] = False
        await ctx.send(f'Poll {poll_id} has been ended.')
        await show_poll_result(ctx, poll_id, final=True)

    @bot.command()
    @delete_user_msg_after(10)
    @delete_bot_msg_after(10)
    async def result(ctx, poll_id: str):
        if poll_id not in poll_data:
            return await ctx.send('Invalid poll ID.')

        await show_poll_result(ctx, poll_id, final=False)

    async def show_poll_result(ctx, poll_id: str, final: bool):
        data = poll_data[poll_id]
        options = data['options']
        votes = data['votes']

        labels = options
        sizes = [votes[option] for option in options]

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')

        if final:
            plt.title(f'Final Results for Poll ID: {poll_id}')
            poll_data.pop(poll_id)
        else:
            plt.title(f'Current Results for Poll ID: {poll_id}')

        plt.savefig('poll_result.png')
        await ctx.send(file=discord.File('poll_result.png'))
        os.remove('poll_result.png')

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            response = await ctx.send('Please provide all required arguments.')
        elif isinstance(error, commands.BadArgument):
            response = await ctx.send('Please provide valid arguments.')
        else:
            response = await ctx.send('An error occurred.')
        await asyncio.sleep(10)
        await ctx.message.delete()
        await asyncio.sleep(10)
        await response.delete()
