#!/usr/bin/env python

import arm4;

def hello ():
    # Register
    app_id = arm4.register_application ("Python test")
    tran_id = arm4.register_transaction (app_id, "Python hello world")
    tran_child_id = arm4.register_transaction (app_id, "Python hello world - child")

    # Start our application and transaction measurements
    app_handle = arm4.start_application (app_id, "Example")

    # Create our parent correlator
    parent = arm4.ArmCorrelator()
    tran_handle = arm4.start_transaction (app_handle, tran_id, correlator=parent)

    # Do our work
    print 'Hello, world!'

    # Create our child
    child = arm4.ArmCorrelator()
    child_handle = arm4.start_transaction (app_handle, tran_child_id, parent=parent, correlator=child)

    # Stop our measurements
    arm4.stop_transaction (child_handle, arm4.ARM_STATUS_ABORTED)
    arm4.stop_transaction (tran_handle, arm4.ARM_STATUS_GOOD)
    arm4.stop_application (app_handle)

    # Finish up
    arm4.destroy_application (app_id)

hello ()
