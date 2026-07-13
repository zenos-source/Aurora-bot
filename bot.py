import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import asyncio
from datetime import datetime, timedelta
import aiohttp

# ─── ENVIRONMENT VARIABLES (Set in Render Dashboard) ──────────────────────
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID', '0'))
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

if not DISCORD_TOKEN:
    print("❌ DISCORD_TOKEN not set in environment variables!")
    exit(1)

if not GUILD_ID:
    print("❌ GUILD_ID not set in environment variables!")
    exit(1)

if not DEEPSEEK_API_KEY:
    print("❌ DEEPSEEK_API_KEY not set in environment variables!")
    exit(1)

print("✅ Environment variables loaded")
print(f"🔒 Bot token: {'*' * 10} (hidden)")
print(f"🔒 API key: {'*' * 10} (hidden)")

# ─── STORAGE ──────────────────────────────────────────────────────────────────
TICKETS_FILE = "tickets.json"

def load_tickets():
    if not os.path.exists(TICKETS_FILE):
        return {}
    try:
        with open(TICKETS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_tickets(data):
    with open(TICKETS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# ─── BOT SETUP ────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.guild_messages = True

bot = commands.Bot(command_prefix='?', intents=intents)

# ─── PRICES ──────────────────────────────────────────────────────────────────
prices = {
    "robux": "800 Robux",
    "ltc": "3 LTC",
    "paypal": "$5 USD",
    "brainrots": "3 Garamas Base OR 2 Traited OR 1 Coloured",
    "gear": "2 Flying Gear OR 1 Flying Gear + Base Skins"
}

# ─── AI FUNCTIONS ─────────────────────────────────────────────────────────────
async def get_ai_response(message, ticket_type=None, history=None):
    """Get response from DeepSeek AI"""
    
    system_prompt = f"""You are an AI support agent for a Discord server called "Source Hub".
You handle tickets for buying scripts, source access, partnerships, and general support.

PRICES (use these EXACTLY when asked):
- Robux: {prices['robux']}
- LTC: {prices['ltc']}
- PayPal: {prices['paypal']}
- Brainrots: {prices['brainrots']}
- Gear: {prices['gear']}

RULES:
1. Be friendly and conversational
2. Answer questions directly
3. If you don't know something, say "I'll escalate this to a human agent"
4. Keep responses helpful but concise
5. If they say "human" or "staff", immediately offer to escalate
6. NEVER mention your API key, token, or any internal credentials
7. If asked about how you work, say "I'm an AI assistant" - don't give technical details"""

    messages = [{"role": "system", "content": system_prompt}]
    
    if history:
        messages.extend(history[-5:])
    
    messages.append({"role": "user", "content": message})

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "max_tokens": 300,
                    "temperature": 0.7
                },
                timeout=30
            ) as response:
                data = await response.json()
                return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"AI Error: {e}")
        return "⚠️ I'm having trouble responding. A human agent will be with you shortly."

# ─── TICKET MODAL ─────────────────────────────────────────────────────────────
class TicketModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="🎫 Open Ticket")
        
        self.ticket_type = discord.ui.TextInput(
            label="What do you need?",
            placeholder="Buy Script / Buy Source Access / Partner / General",
            style=discord.TextStyle.short,
            required=True,
            max_length=100
        )
        self.add_item(self.ticket_type)
        
        self.payment_method = discord.ui.TextInput(
            label="Payment Method (if buying)",
            placeholder="Robux / LTC / PayPal / Brainrots / Gear",
            style=discord.TextStyle.short,
            required=False,
            max_length=50
        )
        self.add_item(self.payment_method)
        
        self.details = discord.ui.TextInput(
            label="More Details",
            placeholder="Any additional information...",
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=1000
        )
        self.add_item(self.details)

    async def on_submit(self, interaction: discord.Interaction):
        tickets = load_tickets()
        if str(interaction.user.id) in tickets:
            await interaction.response.send_message(
                f"❌ You already have an open ticket: <#{tickets[str(interaction.user.id)]}>",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)
        
        guild = interaction.guild
        
        category = discord.utils.get(guild.categories, name="TICKETS")
        if not category:
            category = await guild.create_category("TICKETS")

        channel_name = f"ticket-{interaction.user.name.lower().replace(' ', '-')}"
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        }

        channel = await guild.create_text_channel(
            channel_name,
            category=category,
            overwrites=overwrites,
            topic=f"User: {interaction.user.id} | Type: {self.ticket_type.value}"
        )

        tickets[str(interaction.user.id)] = str(channel.id)
        save_tickets(tickets)

        welcome_msg = f"Hey {interaction.user.mention}! 👋 I'm your AI support agent!"
        
        ticket_lower = self.ticket_type.value.lower()
        if "buy" in ticket_lower or "script" in ticket_lower or "source" in ticket_lower:
            welcome_msg += f"\n\nI see you're interested in {self.ticket_type.value}."
            if self.payment_method.value:
                pm = self.payment_method.value.lower()
                welcome_msg += f" You mentioned paying with {self.payment_method.value}."
                if pm in prices:
                    welcome_msg += f"\n\n💳 The price for that is: **{prices[pm]}**"
        elif "partner" in ticket_lower:
            welcome_msg += f"\n\nGreat! Let's discuss partnership opportunities!"
        else:
            welcome_msg += f"\n\nHow can I help you today?"

        welcome_msg += "\n\nAsk me anything! If you need a human, say 'human' or 'staff'."

        embed = discord.Embed(
            title="🎫 Ticket Opened",
            description=welcome_msg,
            color=discord.Color.blue()
        )
        embed.add_field(name="Ticket Type", value=self.ticket_type.value, inline=True)
        if self.payment_method.value:
            embed.add_field(name="Payment Method", value=self.payment_method.value, inline=True)
        if self.details.value:
            embed.add_field(name="Details", value=self.details.value[:1024], inline=False)
        embed.set_footer(text=f"User ID: {interaction.user.id}")
        embed.timestamp = datetime.now()

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="🔒 Close", style=discord.ButtonStyle.danger, custom_id="close_ticket"))
        view.add_item(discord.ui.Button(label="✋ Claim", style=discord.ButtonStyle.success, custom_id="claim_ticket"))
        view.add_item(discord.ui.Button(label="📝 Transcript", style=discord.ButtonStyle.secondary, custom_id="transcript"))

        await channel.send(content=interaction.user.mention, embed=embed, view=view)
        
        log_channel = discord.utils.get(guild.text_channels, name="ticket-logs")
        if log_channel:
            log_embed = discord.Embed(
                title="🎫 Ticket Created",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            log_embed.add_field(name="User", value=f"{interaction.user} ({interaction.user.id})", inline=True)
            log_embed.add_field(name="Channel", value=f"#{channel.name}", inline=True)
            log_embed.add_field(name="Type", value=self.ticket_type.value, inline=True)
            await log_channel.send(embed=log_embed)

        await interaction.followup.send(f"✅ Ticket created: {channel.mention}", ephemeral=True)

# ─── BOT EVENTS ──────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"✅ Bot is ready! Logged in as {bot.user}")
    print(f"📊 Guild ID: {GUILD_ID}")
    try:
        await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print("✅ Commands synced!")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

# ─── SLASH COMMANDS ──────────────────────────────────────────────────────────
@bot.tree.command(name="panel", description="Send the ticket panel", guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(administrator=True)
async def panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎫 Source Hub Support",
        description="Click the button below to open a ticket!\n\n"
                   "**What we offer:**\n"
                   "• 💰 Buy Scripts\n"
                   "• 🔓 Source Access\n"
                   "• 🤝 Partnerships\n"
                   "• ❓ General Support",
        color=discord.Color.blue()
    )
    embed.set_footer(text="AI-powered support system")
    
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="📩 Open Ticket", style=discord.ButtonStyle.primary, custom_id="open_ticket"))
    
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="add", description="Add a user to this ticket", guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(administrator=True)
@app_commands.describe(user="User to add")
async def add_user(interaction: discord.Interaction, user: discord.Member):
    if not is_ticket_channel(interaction.channel):
        await interaction.response.send_message("❌ This isn't a ticket channel!", ephemeral=True)
        return
    
    await interaction.channel.set_permissions(user, view_channel=True, send_messages=True, read_message_history=True)
    await interaction.response.send_message(f"✅ Added {user.mention} to this ticket.")

@bot.tree.command(name="remove", description="Remove a user from this ticket", guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(administrator=True)
@app_commands.describe(user="User to remove")
async def remove_user(interaction: discord.Interaction, user: discord.Member):
    if not is_ticket_channel(interaction.channel):
        await interaction.response.send_message("❌ This isn't a ticket channel!", ephemeral=True)
        return
    
    await interaction.channel.set_permissions(user, view_channel=False)
    await interaction.response.send_message(f"✅ Removed {user.mention} from this ticket.")

@bot.tree.command(name="close", description="Close this ticket", guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(administrator=True)
async def close_ticket(interaction: discord.Interaction):
    if not is_ticket_channel(interaction.channel):
        await interaction.response.send_message("❌ This isn't a ticket channel!", ephemeral=True)
        return
    
    await interaction.response.send_message("🔒 Closing ticket in 5 seconds...")
    
    tickets = load_tickets()
    user_id = None
    for uid, ch_id in tickets.items():
        if ch_id == str(interaction.channel.id):
            user_id = uid
            break
    
    if user_id:
        try:
            user = await bot.fetch_user(int(user_id))
            await user.send("📩 Your ticket has been closed. Thanks for contacting us!")
        except:
            pass
    
    await asyncio.sleep(5)
    
    if user_id:
        tickets = load_tickets()
        del tickets[user_id]
        save_tickets(tickets)
    
    await interaction.channel.delete()

@bot.tree.command(name="claim", description="Claim this ticket", guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(administrator=True)
async def claim_ticket(interaction: discord.Interaction):
    if not is_ticket_channel(interaction.channel):
        await interaction.response.send_message("❌ This isn't a ticket channel!", ephemeral=True)
        return
    
    embed = discord.Embed(
        description=f"✅ This ticket has been claimed by {interaction.user.mention}",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="transcript", description="Get ticket transcript", guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(administrator=True)
async def transcript(interaction: discord.Interaction):
    if not is_ticket_channel(interaction.channel):
        await interaction.response.send_message("❌ This isn't a ticket channel!", ephemeral=True)
        return
    
    await interaction.response.defer()
    transcript_text = await get_transcript(interaction.channel)
    
    filename = f"transcript-{interaction.channel.name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
    with open(filename, 'w') as f:
        f.write(transcript_text)
    
    await interaction.followup.send(file=discord.File(filename))
    os.remove(filename)

# ─── PREFIX COMMANDS ──────────────────────────────────────────────────────────
@bot.command(name='lock')
@commands.has_permissions(administrator=True)
async def lock_channel(ctx):
    """Lock the current channel"""
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send(f"🔒 Channel locked by {ctx.author.mention}")

@bot.command(name='unlock')
@commands.has_permissions(administrator=True)
async def unlock_channel(ctx):
    """Unlock the current channel"""
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=None)
    await ctx.send(f"🔓 Channel unlocked by {ctx.author.mention}")

@bot.command(name='lockdown')
@commands.has_permissions(administrator=True)
async def lockdown_server(ctx):
    """Lock down the entire server"""
    for channel in ctx.guild.channels:
        if isinstance(channel, discord.TextChannel):
            try:
                await channel.set_permissions(ctx.guild.default_role, send_messages=False)
            except:
                pass
    await ctx.send(f"🔒 **SERVER LOCKDOWN** initiated by {ctx.author.mention}")

@bot.command(name='unlockdown')
@commands.has_permissions(administrator=True)
async def unlockdown_server(ctx):
    """Unlock the entire server"""
    for channel in ctx.guild.channels:
        if isinstance(channel, discord.TextChannel):
            try:
                await channel.set_permissions(ctx.guild.default_role, send_messages=None)
            except:
                pass
    await ctx.send(f"🔓 **SERVER UNLOCKED** by {ctx.author.mention}")

@bot.command(name='to')
@commands.has_permissions(administrator=True)
async def timeout_user(ctx, member: discord.Member, duration: str, *, reason: str = "No reason provided"):
    """Timeout a user. Usage: ?to @user 28d reason"""
    duration_map = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 604800}
    
    unit = duration[-1]
    amount = int(duration[:-1])
    
    if unit not in duration_map:
        await ctx.send("❌ Invalid duration format. Use: s, m, h, d, w")
        return
    
    seconds = amount * duration_map[unit]
    if seconds > 2419200:
        await ctx.send("❌ Maximum timeout is 28 days")
        return
    
    await member.timeout(timedelta(seconds=seconds), reason=reason)
    await ctx.send(f"✅ {member.mention} timed out for **{duration}**. Reason: {reason}")

@bot.command(name='unto')
@commands.has_permissions(administrator=True)
async def untimeout_user(ctx, member: discord.Member):
    """Remove timeout from a user"""
    await member.timeout(None)
    await ctx.send(f"✅ {member.mention} has been un-timed out")

@bot.command(name='kick')
@commands.has_permissions(administrator=True)
async def kick_user(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    """Kick a user"""
    await member.kick(reason=reason)
    await ctx.send(f"✅ {member.mention} kicked. Reason: {reason}")

@bot.command(name='ban')
@commands.has_permissions(administrator=True)
async def ban_user(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    """Ban a user"""
    await member.ban(reason=reason)
    await ctx.send(f"✅ {member.mention} banned. Reason: {reason}")

@bot.command(name='clear')
@commands.has_permissions(administrator=True)
async def clear_messages(ctx, amount: int):
    """Clear messages in the channel"""
    if amount > 100:
        await ctx.send("❌ Cannot clear more than 100 messages at once")
        return
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"✅ Deleted {len(deleted) - 1} messages", delete_after=5)

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def is_ticket_channel(channel):
    tickets = load_tickets()
    return str(channel.id) in tickets.values()

async def get_transcript(channel):
    messages = []
    async for msg in channel.history(limit=200, oldest_first=True):
        timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
        author = f"{msg.author.name}#{msg.author.discriminator} ({msg.author.id})"
        content = msg.content or "[No text]"
        messages.append(f"[{timestamp}] {author}: {content}")
    
    transcript = f"Transcript of #{channel.name}\n"
    transcript += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    transcript += "=" * 50 + "\n\n"
    transcript += "\n".join(messages)
    return transcript

# ─── MESSAGE HANDLER ──────────────────────────────────────────────────────────
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if is_ticket_channel(message.channel):
        if message.content.startswith('?'):
            await bot.process_commands(message)
            return
        
        async with message.channel.typing():
            response = await get_ai_response(message.content)
        
        await message.channel.send(response)
        return
    
    await bot.process_commands(message)

# ─── BUTTON HANDLERS ──────────────────────────────────────────────────────────
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data.get('custom_id')
        
        if custom_id == "open_ticket":
            await interaction.response.send_modal(TicketModal())
        
        elif custom_id == "close_ticket":
            if not is_ticket_channel(interaction.channel):
                await interaction.response.send_message("❌ This isn't a ticket channel!", ephemeral=True)
                return
            
            await interaction.response.send_message("🔒 Closing ticket in 5 seconds...")
            await asyncio.sleep(5)
            
            tickets = load_tickets()
            user_id = None
            for uid, ch_id in tickets.items():
                if ch_id == str(interaction.channel.id):
                    user_id = uid
                    break
            
            if user_id:
                try:
                    user = await bot.fetch_user(int(user_id))
                    await user.send("📩 Your ticket has been closed. Thanks for contacting us!")
                except:
                    pass
                
                tickets = load_tickets()
                del tickets[user_id]
                save_tickets(tickets)
            
            await interaction.channel.delete()
        
        elif custom_id == "claim_ticket":
            if not is_ticket_channel(interaction.channel):
                await interaction.response.send_message("❌ This isn't a ticket channel!", ephemeral=True)
                return
            
            embed = discord.Embed(
                description=f"✅ Ticket claimed by {interaction.user.mention}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        
        elif custom_id == "transcript":
            if not is_ticket_channel(interaction.channel):
                await interaction.response.send_message("❌ This isn't a ticket channel!", ephemeral=True)
                return
            
            await interaction.response.defer()
            transcript_text = await get_transcript(interaction.channel)
            
            filename = f"transcript-{interaction.channel.name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.write(transcript_text)
            
            await interaction.followup.send(file=discord.File(filename))
            os.remove(filename)

# ─── RUN BOT ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 Starting bot...")
    bot.run(DISCORD_TOKEN)
