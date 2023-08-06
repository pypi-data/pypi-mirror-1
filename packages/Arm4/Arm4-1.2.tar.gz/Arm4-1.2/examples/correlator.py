#!/usr/bin/env python

import arm4

def child (app_handle, tran_child_id, parent):
    # Start the transaction
    child = arm4.ArmCorrelator()
    child_handle = arm4.start_transaction (app_handle, tran_child_id, parent=parent, correlator=child)

    # Do any processing here

    # Stop our measurements
    arm4.stop_transaction (child_handle, arm4.ARM_STATUS_ABORTED) # In this case we say we've aborted!

def hello ():
    # Register our application
    app_id = arm4.register_application ("Python test")

    # Register our transactions
    tran_id = arm4.register_transaction (app_id, "Python hello world")
    tran_child_id = arm4.register_transaction (app_id, "Python hello world - child")

    # Start our application
    app_handle = arm4.start_application (app_id, "Example")

    # Create our parent transaction
    parent = arm4.ArmCorrelator()
    tran_handle = arm4.start_transaction (app_handle, tran_id, correlator=parent)

    # Do our work
    print ('Hello, world!')

    # Create our child
    child (app_handle, tran_child_id, parent)

    # Stop our measurements
    arm4.stop_transaction (tran_handle, arm4.ARM_STATUS_GOOD)

    # Finish up
    arm4.stop_application (app_handle)
    arm4.destroy_application (app_id)

hello ()
