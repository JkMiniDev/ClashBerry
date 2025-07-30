import disnake
import os

def setup(bot):
    @bot.tree.command(name="help", description="Get bot command details")
    async def help_command(interaction: disnake.Interaction):
        embed = disnake.Embed(
            description=(
                "## ClashBerry Commands\n\n"
                "**/clan**\nGet info about a clan.\n\n"
                "**/player**\nGet info about a playe.\n\n"
                "**/addclan**\nLink a clan to this server.\n\n"
                "**/linkaccount**\nLink your account to your Discord.\n\n"
                "**/war**\nShow current war info for a clan.\n\n"
                "**/removeclan**\nRemove a clan linked to this server.\n\n"
                "**/setup_ticket**\nSetup the clan application ticket panel.\n\n"
                "**/unlinkaccount**\nUnlink one of your linked accounts."
            ),
            color=disnake.Color.blurple()
        )

        embed.set_image(url="attachment://file.jpg")
        embed.set_footer(text="If you need more help or facing any error or have any suggestions join our support server to report.")

        class SupportButton(disnake.ui.View):
            def __init__(self):
                super().__init__()
                self.add_item(
                    disnake.ui.Button(
                        label="Support Server",
                        url="https://disnake.gg/WVvqR7ysBZ",
                        style=disnake.ButtonStyle.link
                    )
                )

        image_path = os.path.join(os.path.dirname(__file__), "assets", "file.jpg")
        file = disnake.File(image_path, filename="file.jpg")

        await interaction.response.send_message(
            embed=embed,
            view=SupportButton(),
            file=file
        )
