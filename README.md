# Sims 4 Discord Rich Presence

The Sims 4 mod utilizing Discord Rich Presence.
<br>**Compatible with World Rename Mod**

## Features
  - Shows current world & Household Name
  - Shows when in Build/Buy (with small images for gamemode (build/buy & live))
  - Shows household funds and updates when it changes
  - Shows when in CAS in game(not New Game or modded CAS(MCCC))
  - Config file for customizing what is shown
 
![preview_gif](https://github.com/Otakubuns/Sims4-DRP/assets/77337386/7cca21f3-935d-4d47-b710-f40e1f436b6c)

### Compatibility
Mac has not been tested but should work fine.

## Getting Started
### Installing
1. Make sure you have Rich Presence enabled in: Discord -> User Settings -> Activity Privacy -> Display current activity as a status message.
2. Go to [releases](https://github.com/Otakubuns/Sims4-DRP/releases) and download the latest release.
3. I have included a folder to easier drop into your mods folder with the config file, but if you so choose you can just drop the the files into your mods folder.

### Configuration
The configuration file should be in the same folder as the `.ts4script`. It is called `discordRPC.cfg`. There are instructions in the file as well as here. If the file is not there, the mod will just use the default settings built into the mod.

```
[Config]
details = {World_Name}
state = {Household_Name} | {Household_Funds}
largeIconText = {Lot_Name}
showWorldIcon = true
showModeIcon = true
```

There are some built in variables that can be used in the config file:
- `{World_Name}` - The name of the world the household is in.
- `{Household_Name}` - The name of the household.
- `{Household_Funds}` - The amount of money the household has.
- `{Lot_Name}` - The name of the lot the household is on.

### Issues
These are a list of issues that I am aware of ATM and either cannot fix or have no plans to:
- If using Better Exceptions, when an exception occurs and it is scanning your mods folder, the presence will break. It will come back once Better Exceptions is done scanning your mods folder.

### Disclaimer
I am not well versed in Sims 4 modding and my Python knowledge as well is not amazing so there may be better ways to do this. If you do notice something wrong feel free to let me know.

## Acknowledgments
I would have never had this done without the **amazing** Sims 4 Modding community and their posts/documentation.
 - https://github.com/niveshbirangal/discord-rpc for a simple Discord API wrapper that works with Sims limited libraries.
 - https://modthesims.info/showthread.php?p=4751246 for help with hooking into functions and injecting the discord code.
 - https://lot51.cc/ for Sims 4 injector for on_load, buildbuy functions.
 - https://github.com/qwertyquerty/pypresence for a few edits of the code to make it runner better & easier.
 - https://sims4studio.com/thread/15145/started-python-scripting for the Python Script Workspace & learning how to get started with this.
