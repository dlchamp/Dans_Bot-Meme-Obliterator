import json
import datetime
import disnake
from disnake.ext import commands


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_config(self):
        with open("./config/config.json") as f:
            config = json.load(f)
        return config

    def update_config(self, config):
        with open("./config/config.json", "w") as f:
            json.dump(config, f, indent=4, default=str)

    @commands.slash_command(name="config", description="View the current configuration")
    @commands.has_permissions(administrator=True)
    async def config_command(self, inter):
        pass

    @config_command.sub_command(name="view", description="View current configuration.")
    @commands.has_permissions(administrator=True)
    async def config_view(self, inter):

        config = self.get_config()

        channel_id = config["channel"]
        min_limit = config["min_limit"]
        last_run = datetime.datetime.strptime(
            config["last_run"], "%Y-%m-%d %H:%M:%S.%f%z"
        ).date()
        next_run = last_run + datetime.timedelta(hours=168)

        channel = inter.guild.get_channel(channel_id)
        message = f'Current Channel: {channel}\nMinimum Reaction Limit: {min_limit}\nLast Run: {last_run.strftime("%m/%d/%y")}\nExpected next run: {next_run.strftime("%m/%d/%y")}'

        await inter.response.send_message(message, ephemeral=True)

    @config_command.sub_command(
        name="reaction-limit", description="Set the minimum reaction limit."
    )
    @commands.has_permissions(administrator=True)
    async def config_limit(self, inter, limit: int):

        config = self.get_config()
        if config["min_limit"] == limit:
            await inter.response.send_message(
                f"{limit} is already the minimum reactions limit.", ephemeral=True
            )
        elif config["min_limit"] != limit:
            config["min_limit"] = limit
            self.update_config(config)
            await inter.response.send_message(
                f"Minimum reaction limit has been updated to {limit} reactions.",
                ephemeral=True,
            )
        else:
            await inter.response.send_message(
                "There was an error. Please check the log.", ephemeral=True
            )

    @config_command.sub_command(
        name="channel", description="Set the channel to be monitored."
    )
    @commands.has_permissions(administrator=True)
    async def config_channel(self, inter, channel: disnake.TextChannel):

        channel_id = channel.id
        config = self.get_config()
        if config["channel"] == channel_id:
            await inter.response.send_message(
                f"We are already monitoring {channel.name}", ephemeral=True
            )
        elif config["channel"] != channel_id:
            config["channel"] = channel_id
            self.update_config(config)
            await inter.response.send_message(
                f"Channel has been updated to {channel.name}.", ephemeral=True
            )
        else:
            await inter.response.send_message(
                "There was an error. Please check the log.", ephemeral=True
            )

    @config_limit.error
    @config_channel.error
    @config_command.error
    @config_view.error
    async def command_missing_permission(self, inter, error):
        if isinstance(error, commands.MissingPermissions):
            await inter.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )
            return
        raise error


def setup(bot):
    bot.add_cog(Config(bot))
