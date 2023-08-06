#!/usr/bin/env python

import arm4
import sys
import os

app_id = arm4.ArmID ()
tran_id = arm4.ArmID ()

app_handle = arm4.ArmHandle ()

def demo_app (config_file):
    tran_handle = arm4.start_transaction (app_handle, tran_id)

    print ('Hello world (config=', config_file, ')!\n')

    arm4.stop_transaction (tran_handle)

def arm_init (config_file):
    global app_id
    global tran_id
    global app_handle

    app_identity = arm4.ArmSubbufferAppIdentity ()
    app_identity.set_context_name (0, "Config File")

    buffer = arm4.ArmBuffer ()
    buffer.add_subbuffer (app_identity)

    app_id = arm4.register_application ("HelloWorld", buffer)
    tran_id = arm4.register_transaction (app_id, "HelloTran")

    app_context = arm4.ArmSubbufferAppContext ()
    app_context.set_context_value (0, config_file)

    buffer = arm4.ArmBuffer ()
    buffer.add_subbuffer (app_context)

    app_handle = arm4.start_application (app_id, "Examples", buffer=buffer)

def arm_end ():
    arm4.stop_application (app_handle)
    arm4.destroy_application (app_id)

#
# Setting this to 1 will cause ARM calls to generate exceptions on error. This is useful
# for debugging, but you probably don't want this in a production environment
#arm4.enable_exceptions (1)

config_file = ".default.cfg"
if len(sys.argv) > 1:
    config_file = sys.argv[1]
elif 'CONFIGFILE' in os.environ:
    config_file = os.environ['CONFIGFILE']

arm_init (config_file)
demo_app (config_file)
arm_end ()

