
/* Event plugins for the more_selector demo */
kukit.more_selectors = {};

kukit.more_selectors.AnnoyClickerEvent = function() {
};

kukit.more_selectors.AnnoyClickerEvent.prototype.__bind_click__ = function(name, func_to_bind, oper) {
    // validate and set parameters
    oper.completeParms([], {'count': '3'}, 'annoyClicker event binding');
    oper.evalInt('count', 'annoyClicker event binding');
    if (oper.parms.count < 1)
        throw 'Parameter count must be > 0, "' + oper.parms.count + '"';
    // overwrite countsomuch
    this.countsomuch = oper.parms.count;
    this.count = this.countsomuch;
    // Just bind the event via the native event binder
    oper.parms = {};
    kukit.pl.NativeEventBinder.prototype.__bind__('click', func_to_bind, oper);
};

kukit.more_selectors.AnnoyClickerEvent.prototype.__default_click__ = function(name, oper) {
    oper.completeParms([], {}, 'annoyClicker event binding');
    this.count -= 1;
    if (this.count == 0) {
        // Continue with the real action.
        this.count = this.countsomuch;
        this.__continue_event__('doit', oper.node, {});
    } else {
        this.__continue_event__('annoy', oper.node, {});
    }
};

kukit.eventsGlobalRegistry.register('annoyclicker', 'click', kukit.more_selectors.AnnoyClickerEvent, '__bind_click__', '__default_click__');
kukit.eventsGlobalRegistry.register('annoyclicker', 'annoy', kukit.more_selectors.AnnoyClickerEvent, null, null);
kukit.eventsGlobalRegistry.register('annoyclicker', 'doit', kukit.more_selectors.AnnoyClickerEvent, null, null);

