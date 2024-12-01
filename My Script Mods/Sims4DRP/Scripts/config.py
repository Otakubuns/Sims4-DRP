# coding=utf-8
import configparser
import os

# Config File
# Description: Allows for the loading of a config file for the Discord RPC.
#              The config file is expected to be in the same directory as the ts4script.
#              If the config file is missing, the default values are used.


class CaseSensitiveConfigParser(configparser.ConfigParser):
    """Custom ConfigParser that preserves case sensitivity for option keys."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.optionxform = str


def LoadConfig():
    """Loads the config file and returns the values for the Discord RPC."""
    if IsConfigMissing():
        return LoadDefaultConfig()

    config = CaseSensitiveConfigParser()
    path = os.path.join(os.path.dirname(__file__), os.path.pardir, 'discordRPC.cfg')
    config.read(path, encoding='utf-8')

    return {key: value for key, value in config.items('Config')}


def LoadDefaultConfig():
    """Returns the default config values for the Discord RPC in case the config file isn't there."""
    return {
        'details': '{World_Name}',
        'state': '{Household_Name} | {Household_Funds}',
        'largeIconText': '{Lot_Name}',
        'showElapsedTime': 'True',
        'showWorldIcon': 'True',
        'showModeIcon': 'True'
    }

def IsConfigMissing():
    """Checks if the config file is missing."""
    path = os.path.join(os.path.dirname(__file__), os.path.pardir, 'discordRPC.cfg')
    return not os.path.exists(path)

def IsHouseholdFundsUsed(config):
    """Checks if the config file uses the household funds placeholder."""
    for value in config.values():
        if "{Household_Funds}" in value:
            return True
    return False
