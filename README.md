# Sims 4 Discord Rich Presence

This is a mod for The Sims 4 utilizing Discord Rich Presence.

It currently:
  - Shows current world & Household Name
  - Shows when in Build/Buy (with small images for gamemode(build/buy & live))
  - Shows household money and updates when it changes
  - Shows when in CAS in game(not New Game(yet))
 
![preview_gif](https://github.com/Otakubuns/Sims4-DRP/assets/77337386/7cca21f3-935d-4d47-b710-f40e1f436b6c)





### Compatibility
Mac has not been tested but should work fine.

## Getting Started
### Installing
Make sure you have Rich Presence enabled in: Discord -> User Settings -> Activity Privacy -> Display current activity as a status message.<br><br>
Go to [releases](https://github.com/Otakubuns/Sims4-DRP/releases) and download the latest release.

## Future Plans for it are:
- ~~Show when in CAS(have no clue on this yet).~~ Have it working for in Game CAS(mirror, testingcheats) but New Game CAS is still a mystery.
- Configuration file for choosing to show household name, funds etc(already started just been lazy).
- ~~Allow Discord to be open after TS4 and still update presence.~~ Implemented in [1.0.6](https://github.com/Otakubuns/Sims4-DRP/releases/tag/1.0.6)

### Issues
These are a list of issues that I am aware of ATM and either cannot fix or have no plans to:
- ~~Switching from build/buy to live very quickly will cause the presence to not update those states(everything else will still change accordingly). There is no way to fix this as it's just a matter of the presence update not being sent quick enough as it's changing so quick.~~ Haven't come across these issues anymore but i'll leave here in case it does pop up again.

### Disclaimer
I am not well versed in Sims 4 modding and my Python knowledge as well is not amazing(C# lover) so there may be better ways to do this. If you do notice something wrong feel free to let me know.

## Acknowledgments
I would have never had this done without the **amazing** Sims 4 Modding community and their posts/documentation.
 - https://github.com/niveshbirangal/discord-rpc for a simple Discord API wrapper that works with Sims limited libraries.
 - https://modthesims.info/showthread.php?p=4751246 for help with hooking into functions and injecting the discord code.
 - https://lot51.cc/ for Sims 4 injector for on_load, buildbuy functions.
 - https://github.com/qwertyquerty/pypresence for a few edits of the code to make it runner better & easier.
 - https://sims4studio.com/thread/15145/started-python-scripting for the Python Script Workspace & learning how to get started with this.
