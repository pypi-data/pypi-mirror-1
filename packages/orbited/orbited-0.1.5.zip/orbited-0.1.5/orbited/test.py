import event

event.timeout(10, event.abort)

event.dispatch()