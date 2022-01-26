import os
import json
import datetime

import disnake
from disnake.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

bot = commands.Bot(
    commands_prefix="-",
    help_command=None,
    case_sensitive=True
    )

# Load command cogs
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

# Simply on_ready event
@bot.listen()
async def on_ready():
    obliterator_loop.start()
    print(f"{bot.user} is connected and ready!")


@tasks.loop(hours=2)
async def obliterator_loop():
    """
    Loop runs once every 7 days, about 168 hours.  Runs first time on first time the bot loads,
    then waits the configured time to run again.  It will check the monitor channel that's been
    configured and remove any messges that do not meet the minimum reaction limit.  Upon completion
    of it's scan, a message will be submitted to the channel showing how many messages have been removed,
    this message deletes itself after 30 seconds.
    """

    # open the config file to get the min limit, channel, and last run
    with open("./config/config.json") as f:
        config = json.load(f)

    min_limit = config["min_limit"]
    channel = config["channel"]
    time_delta = datetime.timedelta(hours=7)
    today = datetime.datetime.now(datetime.timezone.utc)
    last_run = config["last_run"]
    count = 0
    pin_count = 0
    pin_mbrs = []

    if channel is None:
        print("No channel has been configured")
        return
    if last_run is None:
        limit = None
    else:
        limit = 100

    channel = await bot.fetch_channel(channel)
    # iterate through text channel messages - if no last run, iterate whole channel.  if last run, only iterate last 100 messages
    async for message in channel.history(limit=limit):
        created_at = message.created_at
        max_age = created_at + time_delta
        # Only check if messages are older than 7 days.
        if len(message.attachments) > 0:
            if max_age < today:
                # delete messages that do no meet min requiremnts - increase counter
                if len(message.reactions) < min_limit:
                    count += 1
                    await message.delete()
                # pin messages that aren't pinned an dhave exceeded reaction requirement - increase counter
                elif len(message.reactions) >= 10 and not messaged.pinned:
                    pin_count += 1
                    pin_mbrs.append(f"<@!{message.author.id}>")
                    await message.pin()

    # Check how many messages were deleted/pinned - send messages if more than 0
    if count > 0:
        await channel.send(
            f"{count} messages were removed for not meeting the minimum reaction limit of {min_limit} reactions.",
            delete_after=20,
        )
    if pin_count > 0:
        # join pinned members list by new line and submit in single message
        members = "\n".join(pin_mbrs)
        await channel.send(
            f"{pin_count} messages were pinned for exceeding the 10 reaction limit!."
        )
        await channel.send(
            f"Congrats to these members for submitting such popular memes!\n\n{members}"
        )

    # generate last_run and store in json
    last_run = datetime.datetime.now(datetime.timezone.utc)
    config["last_run"] = last_run
    with open("./config/config.json", "w") as f:
        json.dump(config, f, indent=4, default=str)


bot.run(os.getenv("TOKEN"))
