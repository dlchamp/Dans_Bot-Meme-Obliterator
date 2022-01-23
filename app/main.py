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
    case_sensitive=True,
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


@tasks.loop(hours=168)
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
    if not channel is None:
        channel = await bot.fetch_channel(config["channel"])
        if not last_run is None:
            last_run = datetime.datetime.strptime(
                config["last_run"], "%Y-%m-%d %H:%M:%S.%f%z"
            )
        count = 0

        # iterate through channel messages and remove any messages that do not meet the min limit
        async for message in channel.history(limit=100):
            created_at = message.created_at
            if created_at > last_run:
                if len(message.reactions) < min_limit:
                    count += 1
                    await message.delete()

        if count > 0:
            await channel.send(
                f"{count} messages were removed for not meeting the minimum reaction limit of {min_limit} reactions.",
                delete_after=30,
            )

        last_run = datetime.datetime.now(datetime.timezone.utc)
        config["last_run"] = last_run
        with open("./config/config.json", "w") as f:
            json.dump(config, f, indent=4, default=str)
    else:
        print("No channel has been configured.")


bot.run(os.getenv("TOKEN"))
