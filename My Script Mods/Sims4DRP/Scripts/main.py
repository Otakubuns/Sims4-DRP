import io
import time
import urllib.request
from functools import wraps
from os.path import expanduser
from time import mktime

import build_buy
import rpc
import services
import sims4.reload
from game_services import GameServiceManager, service_manager
from sims.funds import FamilyFunds
from sims4 import commands
from sims4.service_manager import Service
from world import lot

# Sims 4 Discord Rich Presence
# Created by: Otakubuns
# Version: 1.0.1
# Last Updated: 2023-03-08
# Description: Adds Discord Rich Presence to The Sims 4 with Injection methods for CAS, Build/Buy, and Live Mode.
#              Also adds world icons and household funds & name.

# DRP Variables

req = urllib.request.Request(
    'https://raw.githubusercontent.com/Otakubuns/Sims4-DRP/master/My%20Script%20Mods/Sims4DRP/Scripts/main.py')
client_id = '971558123531804742'
client = rpc.DiscordIpcClient.for_platform(client_id)
start_time = mktime(time.localtime())


def GetWorldDict():
    world_dict = {}

    # urllib variables
    url = "https://raw.githubusercontent.com/Otakubuns/Sims4-DRP/master/My%20Script%20Mods/Sims4DRP/Scripts/world_info.txt"

    data = urllib.request.urlopen(url).read().decode('utf-8')
    buf = io.StringIO(data)
    for line in buf:
        value = line.split(' - ')[0].strip().lower().replace(' ', '_').replace('-', '_').replace('.', '_')
        key = line.split(' - ')[1].strip()
        world_dict[key] = value
    return world_dict


try:
    world_dict = GetWorldDict()
except:
    # Set to default(current game version is 1.96.365.1030 as of 2023-03-19)
    world_dict = {'1902162923': 'willow_creek',
                  '3632553424': 'oasis_springs',
                  '3942535331': 'newcrest',
                  '1704446400': 'magnolia_promenade',
                  '1084260742': 'windenburg',
                  '4034911840': 'san_myshuno',
                  '3950992577': 'forgotten_hollow',
                  '2893613071': 'brindleton_bay',
                  '2323227531': 'del_sol_valley',
                  '2018586480': 'strangerville',
                  '3105469928': 'sulani',
                  '100140133' : 'glimmerbrook',
                  '2371324614': 'britechester',
                  '369359163' : 'evergreen_harbor',
                  '3002294565': 'mt__komorebi',
                  '2650041621': 'henford_on_bagley',
                  '3442073656': 'tartosa',
                  '1812713502': 'moonwood_mill',
                  '1505295608': 'copperdale',
                  '3962653297': 'san_sequoia',
                  '4131314756': 'granite_falls',
                  '345901884' : 'selvadorada',
                  '3755578420': 'batuu'}


def inject(target_function, new_function):
    @wraps(target_function)
    def _inject(*args, **kwargs):
        return new_function(target_function, *args, **kwargs)

    return _inject


def inject_to(target_object, target_function_name):
    def _inject_to(new_function):
        target_function = getattr(target_object, target_function_name)
        setattr(target_object, target_function_name, inject(target_function, new_function))
        return new_function

    return _inject_to


# Global service variable
with sims4.reload.protected(globals()):
    _my_custom_service = None


def get_my_custom_service():
    return service_manager.my_custom_service

# Storage for variables for easier updating
gamemode_image = None
gamemode_text = None
current_zone_id = None


class MyCustomService(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # Setting Presence to on zone load, build/buy, and on menu
    def on_zone_load(self, *args, **kwargs):
        global gamemode_text
        global gamemode_image
        global current_zone_id
        gamemode_text = "Live Mode"
        gamemode_image = "live"
        current_zone_id = services.current_zone_id()
        client.set_activity(
            details=GetWorldName(),
            state=f"{GetHouseholdName()} | §{GetHouseholdFunds()}",
            large_image=GetWorldKey(),
            large_text=GetLotName(),
            small_image=gamemode_image,
            small_text=gamemode_text,
            start=start_time)

    def start(self, *args, **kwargs):
        pass

    def stop(self, *args, **kwargs):
        global _my_custom_service
        _my_custom_service = None


@inject_to(GameServiceManager, 'start_services')
def start_services(original, self, *args, **kwargs):
    global _my_custom_service
    try:
        if _my_custom_service is None:
            _my_custom_service = MyCustomService()
            self.register_service(_my_custom_service, is_init_critical=False)

    except:
        pass
    original(self, *args, **kwargs)


@inject_to(services, 'on_enter_main_menu')
def inject_main_menu_load(original):
    client.set_activity(details="Browsing the menu", large_text="Main Menu", large_image="menu", start=start_time)
    original()

@inject_to(build_buy, 'c_api_buildbuy_session_begin')
def inject_build_buy_enter(original, zone_id, account_id):
    original(zone_id, account_id)
    global current_zone_id
    global gamemode_text
    global gamemode_image
    gamemode_text = "Build/Buy Mode"
    gamemode_image = "buildbuy"

    # If the zone id is different it's in manage world build/buy so update the presence
    try:
        if current_zone_id != zone_id:
                client.set_activity(details=GetWorldName(),
                                    state=f"Editing A Lot",
                                    large_image=GetWorldKey(),
                                    large_text=GetLotName(),
                                    small_image=gamemode_image,
                                    small_text=gamemode_text,
                                    start=start_time)

        else:
            client.set_activity(
                details=GetWorldName(),
                state=f"{GetHouseholdName()} | §{GetHouseholdFunds()}",
                large_image=GetWorldKey(),
                large_text=GetLotName(),
                small_image=gamemode_image,
                small_text=gamemode_text,
                start=start_time)
    except Exception:
        pass

@inject_to(build_buy, 'c_api_buildbuy_session_end')
def inject_build_buy_exit(original, zone_id, account_id, **kwargs):
    global current_zone_id
    global gamemode_text
    global gamemode_image
    gamemode_text = "Live Mode"
    gamemode_image = "live"

    try:
        # If the zone id is different it's in manage world build/buy so update the presence
        if current_zone_id != zone_id:
            client.set_activity(details="In Manage Worlds", large_text="Manage Worlds", large_image="menu",
                                start=start_time)
        else:
            client.set_activity(
                details=GetWorldName(),
                state=f"{GetHouseholdName()} | §{GetHouseholdFunds()}",
                large_image=GetWorldKey(),
                large_text=GetLotName(),
                small_image=gamemode_image,
                small_text=gamemode_text,
                start=start_time)
    except Exception:
        pass
    original(zone_id, account_id, **kwargs)


@inject_to(FamilyFunds, 'send_money_update')
def update_household_funds(original, self, *args, **kwargs):
    original(self, *args, **kwargs)
    client.set_activity(details=GetWorldName(),
                        state=f"{GetHouseholdName()} | §{GetHouseholdFunds()}",
                        large_image=GetWorldKey(),
                        large_text=GetLotName(),
                        small_image=gamemode_image,
                        small_text=gamemode_text,
                        start=start_time)

# World for Live CAS but not in menu(create a household)
@inject_to(commands, 'client_cheat')
def inject_cas_load(original, s, context):
    # Make sure command is "exit2cas"
    if "exit2cas" in s:
        global gamemode_text
        global gamemode_image
        gamemode_text = "CAS"
        gamemode_image = "cas"
        client.set_activity(details=GetWorldName(),
                            state=f"{GetHouseholdName()} | §{GetHouseholdFunds()}",
                            large_image=GetWorldKey(),
                            large_text=GetLotName(),
                            small_image=gamemode_image,
                            small_text=gamemode_text,
                            start=start_time)
    original(s, context)


# Functionality Functions
def GetHouseholdName():
    if services.active_household() is None:
        return None
    return services.active_household().name


def GetHouseholdFunds():
    if services.active_household() is None:
        return None
    return f"{services.active_household().funds.money:,}"


def GetWorldName():
    if services.current_zone_id() is None:
        return None
    return services.get_persistence_service().get_neighborhood_proto_buf_from_zone_id(services.current_zone_id()).name


def GetLotName():
    if services.active_lot() is None:
        return None
    return lot.Lot.get_lot_name(self=services.active_lot())


def GetWorldKey():
    world_id = services.get_persistence_service().get_world_id_from_zone(services.current_zone_id())
    if world_id is None:
        return "menu"
    # Check ID compared to dict to see if it's a valid world(if not return generic icon)
    if str(world_id) not in world_dict:
        return "menu"

    world_key = world_dict[str(world_id)]
    return world_key
