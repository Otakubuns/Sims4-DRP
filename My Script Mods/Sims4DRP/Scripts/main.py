import time
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

client_id = '971558123531804742'
client = rpc.DiscordIpcClient.for_platform(client_id)
start_time = mktime(time.localtime())


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


#### FOR DEBUG (Is removed in release)####
path = expanduser('~/Documents/Electronic Arts/The Sims 4/Mods/TESTING/DRP.txt')

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
            large_image=GetWorldKey(GetWorldName()),
            large_text=GetLotName(),
            small_image=gamemode_image,
            small_text=gamemode_text,
            start=start_time)

    def start(self, *args, **kwargs):
        build_buy.register_build_buy_enter_callback(self.on_build_buy_enter)
        build_buy.register_build_buy_exit_callback(self.on_build_buy_exit)

    def stop(self, *args, **kwargs):
        global _my_custom_service
        build_buy.unregister_build_buy_enter_callback(self.on_build_buy_enter)
        build_buy.unregister_build_buy_exit_callback(self.on_build_buy_exit)
        _my_custom_service = None

    def on_build_buy_enter(self, *args, **kwargs):
        global gamemode_text
        global gamemode_image
        gamemode_text = "Build/Buy Mode"
        gamemode_image = "buildbuy"
        client.set_activity(
            details=GetWorldName(),
            state=f"{GetHouseholdName()} | §{GetHouseholdFunds()}",
            large_image=GetWorldKey(GetWorldName()),
            large_text=GetLotName(),
            small_image=gamemode_image,
            small_text=gamemode_text,
            start=start_time)

    def on_build_buy_exit(self, *args, **kwargs):
        global gamemode_text
        global gamemode_image
        gamemode_text = "Live Mode"
        gamemode_image = "live"
        client.set_activity(
            details=GetWorldName(),
            state=f"{GetHouseholdName()} | §{GetHouseholdFunds()}",
            large_image=GetWorldKey(GetWorldName()),
            large_text=GetLotName(),
            small_image=gamemode_image,
            small_text=gamemode_text,
            start=start_time)


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
    original()
    client.set_activity(details="Browsing the menu", large_text="Main Menu", large_image="menu", start=start_time)


@inject_to(build_buy, 'c_api_buildbuy_session_begin')
def inject_build_buy_enter(original, zone_id, account_id):
    original(zone_id, account_id)
    global current_zone_id

    # If the zone id is different it's in manage world build/buy so update the presence
    if current_zone_id != zone_id:
        try:
            client.set_activity(details=GetWorldName(),
                                state=f"Editing A Lot",
                                large_image=GetWorldKey(GetWorldName()),
                                large_text=GetLotName(),
                                small_image=gamemode_image,
                                small_text=gamemode_text,
                                start=start_time)
        except Exception:
            pass


@inject_to(build_buy, 'c_api_buildbuy_session_end')
def inject_build_buy_exit(original, zone_id, account_id, **kwargs):
    global current_zone_id

    # If the zone id is different it's in manage world build/buy so update the presence
    if current_zone_id != zone_id:
        try:
            client.set_activity(details="In Manage Worlds", large_text="Manage Worlds", large_image="menu",
                                start=start_time)
        except Exception:
            pass


@inject_to(FamilyFunds, 'send_money_update')
def update_household_funds(original, self, *args, **kwargs):
    original(self, *args, **kwargs)
    client.set_activity(details=GetWorldName(),
                        state=f"{GetHouseholdName()} | §{GetHouseholdFunds()}",
                        large_image=GetWorldKey(GetWorldName()),
                        large_text=GetLotName(),
                        small_image=gamemode_image,
                        small_text=gamemode_text,
                        start=start_time)


# CAS STUFF
# TODO: Find CAS function(for new game & in menu)

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
                            large_image=GetWorldKey(GetWorldName()),
                            large_text=GetLotName(),
                            small_image=gamemode_image,
                            small_text=gamemode_text,
                            start=start_time)
    original(s, context)


# Functionality Functions
def GetHouseholdName():
    return services.active_household().name


def GetHouseholdFunds():
    return f"{services.active_household().funds.money:,}"


def GetWorldName():
    return services.get_persistence_service().get_neighborhood_proto_buf_from_zone_id(services.current_zone_id()).name


def GetLotName():
    return lot.Lot.get_lot_name(self=services.active_lot())


def GetWorldKey(world_name):
    world_key = world_name.replace(' ', '_')
    world_key = world_key.replace('.', '_')
    world_key = world_key.replace('-', '_')
    world_key = world_key.lower()
    return world_key
