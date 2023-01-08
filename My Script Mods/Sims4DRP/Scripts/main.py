import time
from functools import wraps
from os.path import expanduser
from time import mktime

import build_buy
import rpc
import services
import sims4.reload
from cas.cas import is_online_entitled, _cas
from game_services import GameServiceManager, service_manager
from server.client import Client
from sims.funds import FamilyFunds
from sims4.resources import Types
from sims4.service_manager import Service
from situations.situation_manager import SituationManager

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


#### FOR DEBUG ####
path = expanduser('~/Documents/Electronic Arts/The Sims 4/Mods/TESTING/DRP.txt')
# Storage for variables for easier updating
gamemode_image = None
gamemode_text = None

class MyCustomService(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # Setting Presence to on zone load, build/buy, and on menu
    def on_zone_load(self, *args, **kwargs):
        global gamemode_text
        global gamemode_image
        gamemode_text = "Live Mode"
        gamemode_image = "live"
        client.set_activity(
            details=GetWorldName(),
            state=f"{GetHouseholdName()} | §{GetHouseholdFunds()}",
            large_image= GetWorldKey(GetWorldName()),
            large_text = GetWorldName(),
            small_image = gamemode_image,
            small_text = gamemode_text,
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
            large_text=GetWorldName(),
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
            large_text=GetWorldName(),
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


@inject_to(FamilyFunds, 'send_money_update')
def update_household_funds(original, self, *args, **kwargs):
    original(self, *args, **kwargs)
    client.set_activity(details=GetWorldName(),
            state=f"{GetHouseholdName()} | §{GetHouseholdFunds()}",
            large_image=GetWorldKey(GetWorldName()),
            large_text=GetWorldName(),
            small_image=gamemode_image,
            small_text=gamemode_text,
            start=start_time)


# CAS STUFF
# TODO: Find CAS function

# Functionality Functions
def GetHouseholdName():
    return services.active_household().name


def GetHouseholdFunds():
    return f"{services.active_household().funds.money:,}"


def GetWorldName():
    return services.get_persistence_service().get_neighborhood_proto_buf_from_zone_id(services.current_zone_id()).name


def GetWorldKey(world_name):
    world_key = world_name.replace(' ', '_')
    world_key = world_key.replace('.', '_')
    world_key = world_key.replace('-', '_')
    world_key = world_key.lower()
    return world_key
