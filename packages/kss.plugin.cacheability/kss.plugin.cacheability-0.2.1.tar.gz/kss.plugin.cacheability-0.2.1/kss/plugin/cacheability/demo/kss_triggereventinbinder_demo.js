
/* Event plugins for the more_selector demo */
kukit._dummy = new function () {

var th = this;

th.TriggerTestBinder = function() {
};

kukit.eventsGlobalRegistry.register('cacheability', 'trigger', th.TriggerTestBinder, null, null);


th.TriggerTestBinder2 = function() {
};

kukit.eventsGlobalRegistry.register('cacheability', 'trigger2', th.TriggerTestBinder2, null, null);


}();            // END CLOSURE

