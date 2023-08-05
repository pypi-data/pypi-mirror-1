# Copyright (c) 2007 Open Source Applications Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import sys, os
import traceback

def initialize_settings(default_module, main_module=None, local_env_variable=None):
    """
    Initialize the settings from default_module.
    Attaches settings dictionary to main_module. 
    If main_module is not specified the settings dict is called from is used.
    Override any settings from default_module with the settings in the python file specified in 
    local_env_variable when specified.
    """
    # If a main module is not defined assume the module initialize_settings is called from is the main module
    if main_module is None:
        main_module = sys.modules[traceback.extract_stack()[1][2]]
    
    settings = {}
    for key, value in dict( [ ( name, getattr(default_module, name) ) 
                                for name in dir(default_module)] ).items():
        settings[key] = value
        
    if local_env_variable is not None and os.environ.has_key(local_env_variable):
        
        sys.path.insert(0, os.path.dirname(os.path.expanduser(os.environ[local_env_variable])))
        local_module = __import__(os.path.split(os.environ[local_env_variable])[-1].replace('.py', ''))
        sys.path.pop(0)
        for key, value in dict( [ ( name, getattr(local_module, name) ) 
                                    for name in dir(local_module)] ).items():
            settings[key] = value
    
    main_module.settings = settings
    
    
