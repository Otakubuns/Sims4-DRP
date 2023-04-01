# Sims 4 Discord Rich Presence

This is a mod for The Sims 4 utilizing Discord Rich Presence.

It currently:
  - Shows current world & Household Name
  - Shows when in Build/Buy (with small images for gamemode(build/buy & live))
  - Shows household money and updates when it changes
  - Shows when in CAS in game(not New Game(yet))
 
![image](https://user-images.githubusercontent.com/77337386/205202833-4c7063cb-64b8-4679-93a7-2aeac75948fb.png)

### Compatibility
⚠️ If you have BetterExceptions and it say's this mod is the reason why an exception occured its **probably** not. I have added in some try/catch's in case another mod causes issues with loading zones so it doesnt break but it may not be perfect. If you do have an exception and it say's its this mod it may be another mod not working due to a new update so please try only with this mod(and BetterExceptions) in your mods folder to make sure.
- This shouldn't conflict with anything as it's purely a ts4script so it isn't editing anything other mods would.
- This also shouldn't break during any updates for the same reason(big updates might cause it to break).
- If you rename your world (like using [SrslySims World Rename Tool](https://srslysims.net/downloads/world-rename-tool/)) there a compatiable version. The renamed world will show up in your presence as the world name but the icon will be the original world you renamed.

Mac has not been tested but should work fine.

## Getting Started
### Installing
Make sure you have Rich Presence enabled in: Discord -> User Settings -> Activity Privacy -> Display current activity as a status message.<br><br>
Go to [releases](https://github.com/Otakubuns/Sims4-DRP/releases) and download the latest release.

Choose only **one** version. If you don't rename your worlds just grab the basic one, if you do grab the CustomWorldNames version.<br>
Drag the .ts4script into the Mods folder(do NOT unzip the ts4script file).

## Future Plans for it are:
- ~~Show when in CAS(have no clue on this yet).~~ Have it working for in Game CAS(mirror, testingcheats & MCC) but New Game CAS is still a mystery.
- Configuration file for choosing to show household name, funds etc(already started just been lazy).

### Issues
These are a list of issues that I am aware of ATM and either cannot fix or have no plans to:
- ~~Switching from build/buy to live very quickly will cause the presence to not update those states(everything else will still change accordingly). There is no way to fix this as it's just a matter of the presence update not being sent quick enough as it's changing so quick.~~ Haven't come across this issues anymore but i'll leave here in case it does pop up again.

### Disclaimer
I am not well versed in Sims 4 modding and my Python knowledge as well is not amazing(C# lover) so there may be better ways to do this. If you do notice something wrong feel free to let me know.

## Acknowledgments
I would have never had this done without the **amazing** Sims 4 Modding community and their posts/documentation.
 - https://github.com/niveshbirangal/discord-rpc for a simple Discord API wrapper that works with Sims limited libraries.
 - https://modthesims.info/showthread.php?p=4751246 for help with hooking into functions and injecting the discord code.
 - https://lot51.cc/ for Sims 4 injector for on_load, buildbuy functions.
 - https://github.com/qwertyquerty/pypresence for a few edits of the code to make it runner better & easier.
 - https://sims4studio.com/thread/15145/started-python-scripting for the Python Script Workspace & learning how to get started with this.
