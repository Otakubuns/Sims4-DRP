# Sims 4 Discord Rich Presence

This is a mod for The Sims 4 utilizing Discord Rich Presence.

It currently:
  - Shows current world & Household Name
  - Shows when in Build/Buy (with small images for gamemode(build/buy & live))
  - Shows household money and updates when it changes
  - Shows when in CAS in game(not New Game(yet))
 
![image](https://user-images.githubusercontent.com/77337386/205202833-4c7063cb-64b8-4679-93a7-2aeac75948fb.png)

## Getting Started
### Installing

Go to [releases](https://github.com/Otakubuns/Sims4-DRP/releases) and download the latest release.

Unzip the file and drag the .ts4script into the Mods folder.

After that just run up the game and you should be good!

Mac has not been tested but should work fine.

## Acknowledgments

 - https://github.com/niveshbirangal/discord-rpc for a simple Discord API wrapper that works with Sims limited libraries.
 - https://modthesims.info/showthread.php?p=4751246 for help with hooking into functions and injecting the discord code.
 - https://lot51.cc/ for Sims 4 injector for on_load, buildbuy functions.
 - https://github.com/qwertyquerty/pypresence for a few edits of the code to make it runner better & easier.
 - https://sims4studio.com/thread/15145/started-python-scripting for the Python Script Workspace & learning how to get started with this.


## Future Plans for it are:
- ~~Show when in CAS(have no clue on this yet).~~ Have it working for in Game CAS(mirror, testingcheats & MCC) but New Game CAS is still a mystery.
- Configuration file for choosing to show household name, funds etc(already started just been lazy).

### Issues
These are a list of issues that I am aware of ATM and either cannot fix or have no plans to:
- Switching from build/buy to live very quickly will cause the presence to not update those states(everything else will still change accordingly). There is no way to fix this as it's just a matter of the presence update not being sent quick enough as it's changing so quick.
- I am not super knowledgable about Sims 4 modding so there may be better ways to call functions, or any other mistakes.
