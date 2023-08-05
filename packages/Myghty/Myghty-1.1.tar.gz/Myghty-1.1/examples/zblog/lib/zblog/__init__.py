"""zblog general module.  Defines global application constants and helper functions."""

import os

"""application configuration.  the runtime environment should establish configuration details in this dictionary."""
config = {}

"""startup list.  when configuration is loaded, callables in this list will be executed."""
startup =[]

"""indicates if config file needs to be loaded."""
need_config = True


def load_config(file):
    """called by application starting point (such as a front controller or command line script) to initialize configuration with given filename."""
    global need_config
    if not need_config:
        return False
    if len(config) == 0:
        if os.access(file, os.F_OK):
            execfile(file, config)
            need_config=False
            for callable_ in startup:
                callable_()
    return need_config

def reset_config():
    """reset config - used by bootstrapper when an error occurs"""
    config.clear()
    global need_config
    need_config=True
