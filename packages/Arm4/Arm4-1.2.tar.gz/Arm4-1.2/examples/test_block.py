#!/usr/bin/env python

import arm4;
import time;

def hello ():
    # Register
    app_id = arm4.register_application ("Python test")
    tran_id = arm4.register_transaction (app_id, "Python hello world")

    # Start our application and transaction measurements
    app_handle = arm4.start_application (app_id, "Example")
    tran_handle = arm4.start_transaction (app_handle, tran_id)

    # Do our work
    print ('Hello, world!')

    # The transaction may become blocked on another application or process
    block_handle = arm4.block_transaction (tran_handle);
 
    time.sleep (1);
 
    arm4.unblock_transaction (tran_handle, block_handle);

    # Stop our measurements
    arm4.stop_transaction (tran_handle) # Default status is arm4.ARM_STATUS_GOOD
    arm4.stop_application (app_handle)

    # Finish up
    arm4.destroy_application (app_id)

hello ()
