#!/usr/bin/env python

import arm4;

def hello ():
    # Register
    app_id = arm4.register_application ("Python test")
    tran_id = arm4.register_transaction (app_id, "Python hello world")

    # Start our application and transaction measurements
    app_handle = arm4.start_application (app_id, "Example")
    tran_handle = arm4.start_transaction (app_handle, tran_id)

    # Do our work
    print ('Hello, world!')

    # Stop our measurements
    arm4.stop_transaction (tran_handle) # Default status is arm4.ARM_STATUS_GOOD
    arm4.stop_application (app_handle)

    # Finish up
    arm4.destroy_application (app_id)

hello ()
