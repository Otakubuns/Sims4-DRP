# coding=utf-8
import logging
import time
from functools import wraps
from time import mktime

import build_buy
import services
import sims4.reload
from game_services import GameServiceManager, service_manager
from sims.funds import FamilyFunds
from sims4 import commands
from sims4.service_manager import Service
from world import lot

import config
import rpc
from logger import logger

# Sims 4 Discord Rich Presence
# Created by: Otakubuns
# Version: 1.0.7
# Last Updated: 2024-11-30
# Description: Adds Discord Rich Presence to The Sims 4 with injection methods for CAS, Build/Buy, and Live Mode.
#              Also adds world icons, household funds & name. Configurable through the discordRPC.cfg file

# DRP Variables
client_id = '971558123531804742'
client = rpc.DiscordIpcClient.for_platform(client_id)
start_time = mktime(time.localtime())
raw_config = config.LoadConfig()

# Global service variable
with sims4.reload.protected(globals()):
    _my_custom_service = None


def get_my_custom_service():
    return service_manager.my_custom_service


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
        SetActivity()

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

        if services.active_household() is None:
            client.set_activity(details=GetWorldName(),
                                state="Editing A Lot",
                                large_image=GetWorldKey(),
                                large_text=GetLotName(),
                                small_image=gamemode_image,
                                small_text=gamemode_text,
                                start=start_time)
        else:
            SetActivity()

    def on_build_buy_exit(self, *args, **kwargs):
        global gamemode_text
        global gamemode_image
        gamemode_text = "Live Mode"
        gamemode_image = "live"

        if services.active_household() is None:
            # If no household is active, we're in manage worlds
            client.set_activity(details="In Manage Worlds", large_text="Manage Worlds", large_image="menu",
                                start=start_time)
        else:
            SetActivity()


# Reconnect if need be
@sims4.commands.Command('discord', command_type=sims4.commands.CommandType.Live)
def discord_reconnect(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    try:
        # This will close the client and create a new one, I don't recommend using this command often
        global client
        client.close()
        client = rpc.DiscordIpcClient.for_platform(client_id)
        output("Reconnected to Discord RPC.")
        SetActivity()
    except Exception as e:
        output(f"Error reconnecting to Discord. Please check logs for more information.")


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


# If HouseHold funds is used in the presence, update it when funds are updated, but don't inject if its not used
if config.IsHouseholdFundsUsed(raw_config):
    @inject_to(FamilyFunds, 'send_money_update')
    def update_household_funds(original, self, *args, **kwargs):
        SetActivity()
        original(self, *args, **kwargs)


# World for Live CAS but not in menu(create a household)
@inject_to(commands, 'client_cheat')
def inject_cas_load(original, s, context):
    # Make sure command is "exit2cas"
    if "exit2cas" in s:
        global gamemode_text
        global gamemode_image
        gamemode_text = "CAS"
        gamemode_image = "cas"
        SetActivity()
    original(s, context)

# Functionality Functions
def GetHouseholdName():
    if services.active_household() is None:
        return None
    return services.active_household().name

def GetHouseholdFunds():
    if services.active_household() is None:
        return None
    return f"§{services.active_household().funds.money:,}"

def GetWorldName():
    if services.current_zone_id() is None:
        return None
    return services.get_persistence_service().get_neighborhood_proto_buf_from_zone_id(services.current_zone_id()).name

def GetWorldKey():
    if services.current_zone_id() is None:
        return None
    return str(services.get_persistence_service().get_neighborhood_proto_buf_from_zone_id(
        services.current_zone_id()).region_id)

def GetLotName():
    if services.active_lot() is None:
        return None
    return lot.Lot.get_lot_name(self=services.active_lot())


def SetActivity():
    """Sets the activity for the Discord Rich Presence."""
    global raw_config

    def returnConfig(key):
        value = ResolveConfigValueFunctions(raw_config[key])
        return value if value != "" else None

    try:
        details = returnConfig('details')
        state = returnConfig('state')
        large_icon_text = returnConfig('largeIconText')
        show_world_icon = raw_config['showWorldIcon'].lower() == 'true'
        show_mode_icon = raw_config['showModeIcon'].lower() == 'true'
    except Exception:
        # if exception happens run the default values
        details = ResolveConfigValueFunctions(config.LoadDefaultConfig()['details'])
        state = ResolveConfigValueFunctions(config.LoadDefaultConfig()['state'])
        large_icon_text = ResolveConfigValueFunctions(config.LoadDefaultConfig()['largeIconText'])
        show_world_icon = config.LoadDefaultConfig()['showWorldIcon'].lower() == 'true'
        show_mode_icon = config.LoadDefaultConfig()['showModeIcon'].lower() == 'true'

    large_icon = GetWorldKey() if show_world_icon else 'menu'
    small_icon, small_text = (gamemode_image, gamemode_text) if show_mode_icon else (None, None)

    client.set_activity(
        details=details,
        state=state,
        large_image=large_icon,
        large_text=large_icon_text,
        start=start_time,
        small_image=small_icon,
        small_text=small_text
    )


def ResolveConfigValueFunctions(config_value):
    """Resolves the functions in the config values."""
    config_dict = {
        "{Household_Name}": GetHouseholdName,
        "{Household_Funds}": GetHouseholdFunds,
        "{Lot_Name}": GetLotName,
        "{World_Name}": GetWorldName
    }

    for placeholder, function in config_dict.items():
        if placeholder in config_value:
            try:
                # Call the function and replace the placeholder with its result
                result = function()
                if result is None:
                    result = "[Unavailable]"
                config_value = config_value.replace(placeholder, result)
            except Exception as e:
                config_value = config_value.replace(placeholder, "")
                logger.error(f"Error resolving placeholder {placeholder}: {e}")
    return config_value
