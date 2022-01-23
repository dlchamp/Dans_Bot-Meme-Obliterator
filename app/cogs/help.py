import disnake
from disnake.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="help", description=f"View information and commands.")
    @commands.has_permissions(administrator=True)
    async def help_command(self, inter):
        embed = disnake.Embed(
            title=f"{self.bot.user.name} Help!",
            description="Use `/` to see available commands",
        )
        embed.add_field(
            name="Admin Commands:",
            value=f"`/config reaction-limit <limit>` - Configure the minimum reactions limit a message must meet to not be deleted\n \
            `/config channel <channel>` - Configures the channel for the bot to monitor for auto-deleting messages.",
        )
        await inter.response.send_message(embed=embed, ephemeral=True)

    @help_command.error
    async def help_command_error(inter, error):
        if isinstance(error, MissingPermissions):
            await inter.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )
            return
        raise error


def setup(bot):
    bot.add_cog(Help(bot))
