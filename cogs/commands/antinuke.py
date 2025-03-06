import discord
from discord.ext import commands
import aiosqlite
import asyncio
from utils.Tools import *


class Antinuke(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.bot.loop.create_task(self.initialize_db())

  async def initialize_db(self):
    self.db = await aiosqlite.connect('db/anti.db')
    await self.db.execute('''
        CREATE TABLE IF NOT EXISTS antinuke (
            guild_id INTEGER PRIMARY KEY,
            status BOOLEAN
        )
    ''')
    await self.db.commit()

    
  async def enable_limit_settings(self, guild_id):
    default_limits = DEFAULT_LIMITS
    for action, limit in default_limits.items():
      await self.db.execute('INSERT OR REPLACE INTO limit_settings (guild_id, action_type, action_limit, time_window) VALUES (?, ?, ?, ?)', (guild_id, action, limit, TIME_WINDOW))
      await self.db.commit()

  async def disable_limit_settings(self, guild_id):
    await self.db.execute('DELETE FROM limit_settings WHERE guild_id = ?', (guild_id,))
    await self.db.commit()


  @commands.hybrid_command(name='antinuke', aliases=['antiwizz', 'anti'], help="Enables/Disables Anti-Nuke Module in the server")
  
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 4, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def antinuke(self, ctx, option: str = None):
    guild_id = ctx.guild.id
    pre=ctx.prefix

    async with self.db.execute('SELECT status FROM antinuke WHERE guild_id = ?', (guild_id,)) as cursor:
      row = await cursor.fetchone()

    async with self.db.execute(
            "SELECT owner_id FROM extraowners WHERE guild_id = ? AND owner_id = ?",
            (ctx.guild.id, ctx.author.id)
        ) as cursor:
            check = await cursor.fetchone()

    is_owner = ctx.author.id == ctx.guild.owner_id
    if not is_owner and not check:
      embed = discord.Embed(title="<:icon_cross:1345041135156072541> Access Denied",
                color=0x000000,
                description="Only Server Owner or Extra Owner can Run this Command!"
            )
      return await ctx.send(embed=embed)

    is_activated = row[0] if row else False

    if option is None:
      embed = discord.Embed(
        title='__**Antinuke**__',
        description="Boost your server security with Antinuke! It automatically bans any admins involved in suspicious activities, ensuring the safety of your whitelisted members. Strengthen your defenses – activate Antinuke today!",
        color=0x000000
      )
      embed.add_field(name='__**Antinuke Enable**__', value=f'To Enable Antinuke, Use - `{pre}antinuke enable`')
      embed.add_field(name='__**Antinuke Disable**__', value=f'To Disable Antinuke, Use - `{pre}antinuke disable`')
      

      embed.set_thumbnail(url=self.bot.user.avatar.url)
      await ctx.send(embed=embed)

    elif option.lower() == 'enable':
      if is_activated:
        embed = discord.Embed(
          description=f'**Security Settings For {ctx.guild.name}**\nYour server __**already has Antinuke enabled.**__\n\nCurrent Status: <:cm_on:1345295105309020171> Enabled\nTo Disable use `antinuke disable`',
          color=0x000000
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        await ctx.send(embed=embed)
      else:
        
        setup_embed = discord.Embed(
          title="<a:antinuke:1345243426878394439>",
          description="<a:buffering:1347211646115905579> | Initializing Quick Setup!",
          color=0x000000
        )
        setup_message = await ctx.send(embed=setup_embed)

        
        if not ctx.guild.me.guild_permissions.administrator:
          setup_embed.description += "\n<:icons_error:1345041194467721327> | Setup failed: Missing **Administrator** permission."
          await setup_message.edit(embed=setup_embed)
          return

        await asyncio.sleep(1)
        setup_embed.description += "\n<:tick_icons:1345041197483298856> | Checking Kranton role position for optimal configuration..."
        await setup_message.edit(embed=setup_embed)

        await asyncio.sleep(1)
        setup_embed.description += "\n<:tick_icons:1345041197483298856> | Crafting and configuring the Kranton Supreme role..."
        await setup_message.edit(embed=setup_embed)
        
        try:
          role = await ctx.guild.create_role(
            name="Kranton Supreme™",
            color=0xdc143c,
            permissions=discord.Permissions(administrator=True),
            hoist=False,
            mentionable=False,
            reason="Antinuke setup Role Creation"
          )
          await ctx.guild.me.add_roles(role)
        except discord.Forbidden:
          setup_embed.description += "\n<:icons_error:1345041194467721327> | Setup failed: Insufficient permissions to create role."
          await setup_message.edit(embed=setup_embed)
          return
        except discord.HTTPException as e:
          setup_embed.description += f"\n<:icons_error:1345041194467721327> | Setup failed: HTTPException: {e}\nCheck Guild **Audit Logs**."
          await setup_message.edit(embed=setup_embed)
          return

        await asyncio.sleep(1)
        setup_embed.description += "\n<:tick_icons:1345041197483298856> | Ensuring precise placement of the Kranton Supreme role..."
        await setup_message.edit(embed=setup_embed)
        try:
          await ctx.guild.edit_role_positions(positions={role: 1})
        except discord.Forbidden:
          setup_embed.description += "\n<:icons_error:1345041194467721327> | Setup failed: Insufficient permissions to move role."
          await setup_message.edit(embed=setup_embed)
          return
        except discord.HTTPException as e:
          setup_embed.description += f"\n<:icons_error:1345041194467721327> | Setup failed: HTTPException: {e}."
          await setup_message.edit(embed=setup_embed)
          return

        await asyncio.sleep(1)
        setup_embed.description += "\n<:tick_icons:1345041197483298856> | Safeguarding your changes..."
        await setup_message.edit(embed=setup_embed)

        await asyncio.sleep(1)
        setup_embed.description += "\n<:tick_icons:1345041197483298856> | Activating the Antinuke Modules for enhanced security...!!"
        await setup_message.edit(embed=setup_embed)

        await self.db.execute('INSERT OR REPLACE INTO antinuke (guild_id, status) VALUES (?, ?)', (guild_id, True))
        await self.db.commit()

        await asyncio.sleep(1)
        await setup_message.delete()

        embed = discord.Embed(
          description=f"**Security Settings For {ctx.guild.name} <a:antinuke:1345243426878394439>**\n\nTip: For optimal functionality of the AntiNuke Module, please ensure that my role has **Administration** permissions and is positioned at the **Top** of the roles list\n\n<:settings:1345041189178576946> __**Modules Enabled**__\n>>> <:cm_on:1345295105309020171> **Anti Ban**\n<:cm_on:1345295105309020171> **Anti Kick**\n<:cm_on:1345295105309020171> **Anti Bot**\n<:cm_on:1345295105309020171> **Anti Channel Create**\n<:cm_on:1345295105309020171> **Anti Channel Delete**\n<:cm_on:1345295105309020171> **Anti Channel Update**\n<:cm_on:1345295105309020171> **Anti Everyone/Here**\n<:cm_on:1345295105309020171> **Anti Role Create**\n<:cm_on:1345295105309020171> **Anti Role Delete**\n<:cm_on:1345295105309020171> **Anti Role Update**\n<:cm_on:1345295105309020171> **Anti Member Update**\n<:cm_on:1345295105309020171> **Anti Guild Update**\n<:cm_on:1345295105309020171> **Anti Integration**\n<:cm_on:1345295105309020171> **Anti Webhook Create**\n<:cm_on:1345295105309020171> **Anti Webhook Delete**\n<:cm_on:1345295105309020171> **Anti Webhook Update**",
          color=0x000000
        )

        embed.add_field(name='', value="<:cm_on:1345295105309020171> **Anti Prune**\n<:cm_on:1345295105309020171> **Auto Recovery**")

        embed.set_author(name="Kranton Antinuke", icon_url=self.bot.user.avatar.url)

        embed.set_footer(text="Successfully Enabled Antinuke for this server | Powered by Kranton Development™", icon_url=self.bot.user.avatar.url)
        embed.set_thumbnail(url=self.bot.user.avatar.url)

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Show Punishment Type", custom_id="show_punishment"))

        await ctx.send(embed=embed, view=view)

    elif option.lower() == 'disable':
      if not is_activated:
        embed = discord.Embed(
          description=f'**Security Settings For {ctx.guild.name}**\nUhh, looks like your server hasn\'t enabled Antinuke.\n\nCurrent Status: <:cm_off:1345295117082169354> Disabled\n\nTo Enable use `antinuke enable`',
          color=0x000000
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
      else:
        await self.db.execute('DELETE FROM antinuke WHERE guild_id = ?', (guild_id,))
        await self.db.commit()
        embed = discord.Embed(
          description=f'**Security Settings For {ctx.guild.name}**\nSuccessfully disabled Antinuke for this server.\n\nCurrent Status: <:cm_off:1345295117082169354> Disabled\n\nTo Enable use `antinuke enable`',
          color=0x000000
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
      await ctx.send(embed=embed)
    else:
      embed = discord.Embed(
        description='Invalid option. Please use `enable` or `disable`.',
        color=0x000000
      )
      await ctx.send(embed=embed)


  @commands.Cog.listener()
  async def on_interaction(self, interaction: discord.Interaction):
    if interaction.data.get('custom_id') == 'show_punishment':
    
      embed = discord.Embed(
        title="Punishment Types for Changes Made by Unwhitelisted Admins/Mods",
        description=(
          "**Anti Ban:** Ban\n"
          "**Anti Kick:** Ban\n"
          "**Anti Bot:** Ban the bot Inviter\n"
          "**Anti Channel Create/Delete/Update:** Ban\n"
          "**Anti Everyone/Here:** Remove the message & 1 hour timeout\n"
          "**Anti Role Create/Delete/Update:** Ban\n"
          "**Anti Member Update:** Ban\n"
          "**Anti Guild Update:** Ban\n"
          "**Anti Integration:** Ban\n"
          "**Anti Webhook Create/Delete/Update:** Ban\n"
          "**Anti Prune:** Ban\n"
          "**Auto Recovery:** Automatically recover damaged channels, roles, and settings\n\n"
          "Note: In the case of member updates, action will be taken only if the role contains dangerous permissions such as Ban Members, Administrator, Manage Guild, Manage Channels, Manage Roles, Manage Webhooks, or Mention Everyone"
        ),
        color=0x000000
      )
      embed.set_footer(text="These punishment types are fixed and assigned as required to ensure guild security/protection", icon_url=self.bot.user.avatar.url)
      await interaction.response.send_message(embed=embed, ephemeral=True)

"""
@Author: Stxrz
    + Discord: stxrzz.py
    + Community: https://discord.gg/hjSV93j93j (Kranton Development)
    + for any queries reach out Community or DM me."""
