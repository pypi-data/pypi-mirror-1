var scheduleEvents = {
    '.day': {
        onEventsAdded: function (elem) {
            var info = elem.getAttribute('id').split('-');
            var layer = info[0];
            var day = info[1];

            var reg = this.registry.days[day];
            var sort = reg[layer + 'Sortable'];

            if (sort) {
                sort.detach();
            }

            reg[layer + 'Sortable'] = new SBSortables(this, elem, {
                ghost: false
            });

            sort = reg[layer + 'Sortable'];

            sort.addEvent('onStart', function (slot, ghost) {
                slot.setProperty('alt', JSON.encode(slot.getCoordinates()));
            });

            sort.addEvent('onComplete', (function (slot) {
                // Only update slot's properties if it's actually moved over the course
                // of the drag.
                if (slot.getProperty('alt') !== JSON.encode(slot.getCoordinates())) {
                    this.getSlot(slot).update();
                }
            }).bind(this));
        }
    }
};

var Schedule = new Class({
    Extends: ElementObject,
    Implements: Options,
    options: {
        id: 'schedule',
        layers: new Hash({
            earmark: {
                sessionTypes: {
                    cleaning: 'Cleaning',
                    closed:   'Closed',
                    otherUse: 'Other Use',
                    reserved: 'Reserved',
                    scanning: 'Scanning'
                }
            },
            session: {
                sessionTypes: {
                    maintenance: 'Maintenance',
                    methods: 'Methods',
                    scanning: 'Scanning',
                    downtime: 'Downtime'
                }
            }
        }),
        days: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'],
        mediaUrl: null,
        rpcUrl: null,

        display: {
            minSlot      : 900, // 15 mins
            slotHeight   : 12 + (17 * 0),
            slotPadding  : 2,
            slotMargin   : 1,
            slotExtra    : (2 * 2) + 1,
            scheduleBorder: 1,
            dayDatesHeight: 25
        }
    },

    initialize: function (options) {
        this.setOptions(options);

        this.id = this.options.id;
        this.days = this.options.days;
        this.layers = this.options.layers;

        this.parent('div', {id: this.id});
        this.setElementFromDom();
        this.element().addClass('loading');

        this.eventManager = new EventManager(this, scheduleEvents);
        this.templateSelector = new TemplateSelector(this);
        this.createSlotBox = new SidebarBox({id: 'createslotoptions'});
        this.eventLayer = {intent: null, params: []};

        this.registry = {days: {}, ids: {}};

        this.days.each(function (day) {
            this.registry.days[day] = {};

            this.layers.each(function (info, layer) {
                var slotElem = this.getElement('#' + layer);

                slotElem.adopt(
                    new Element('ul', {'id': layer + '-' + day, 'class': 'day'})
                );
            }, this);
        }, this);
    },

    setAllUnclicked: function () {
        this.getElements('.timeslot').removeClass('clickedtimeslot');
    },

    // Various helper functions
    getSlot: function (elem) {
        var slot;
        if (elem) {
            var layer = elem.getParent().getAttribute('id').split('-')[0];
            var id = elem.getAttribute('id');
            slot = this.registry.ids[layer][id];
        }
        return slot;
    },
    dayElement: function (day, layer) {
        layer = layer || this.mode;
        return this.getElement('#' + layer + '-' + day);
    },
    dayLength: function () {
        return (this.options.workingEndsHour - this.options.workingStartsHour) * 3600;
    },
    startOfDay: function (day) {
        var midnight = this.options.weekStarts + (this.days.indexOf(day) * 86400);
        return (midnight + (this.options.workingStartsHour * 3600));
    },
    endOfDay: function (day) {
        var midnight = this.options.weekStarts + (this.days.indexOf(day) * 86400);
        return (midnight + (this.options.workingEndsHour * 3600));
    },
    addRpcService: function (url) {
        this.rpcService = new MooRpcService(url);
        return this.rpcService;
    },
    isEmptyWeek: function () {
        return $H(this.registry.ids.earmark).getLength() === 0;
    },

    // Core data updating methods:
    setData: function (data) {
        if ($type(data) !== 'object') { console.warn("Data is not object"); }
        if (data.config) { this.setOptions(data.config); }

        this.layers.each(function (info, layer) {
            if (data[layer + 's']) { this.setLayerData(layer, data[layer + 's']); }
        }, this);
    },
    setLayerData: function (layer, data) {
        this.registry.ids[layer] = {};
        this.days.each(function (day) {
            this.registry.days[day][layer] = [];
            if (data && data[day]) {
                data[day].each(function (data) {
                    data.layer = layer;
                    this.addSlot(data);
                }, this);
            }
        }, this);
    },
    addSlot: function (data) {
        var slot = new TimeSlot(this, data);
        this.registry.days[slot.day()][slot.data.layer].push(slot);
        this.registry.ids[slot.data.layer][slot.data.id] = slot;
        return slot;
    },
    // TODO: remove this horrible, horrible hack
    injectSlot: function (data) {
        if (data.error) {
            alert(data.error);
            setBusy(false);
        } else {
            var slot = this.addSlot(data);
            this.drawDay(slot.day(), slot.data.layer);
            slot.setAsClicked();
            setBusy(false);
            slot.updateEditBox();
        }
    },
    createSlot: function (data) {
        setBusy(true);
        this.rpcService.createTimeSlot(data).callback(this.injectSlot.bind(this));
    },
    destroySlot: function (data) {
        var slot = this.registry.ids[data.layer][data.id];
        slot.element().remove();
        this.registry.days[slot.day()][data.layer].remove(slot);
        this.registry.ids[data.layer][data.id] = null;
        setBusy(false);
        if (this.editBox) {
            this.editBox.hide();
        }
    },

    // Schedule mode control:
    setMode: function (modeName) {
        if (this.editBox) {
            this.editBox.hide();
        }
        var disp;
        var blockElements = ['address', 'blockquote', 'div', 'dl', 'fieldset',
                             'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr',
                             'noscript', 'ol', 'p', 'pre', 'table', 'ul'];
        this.mode = modeName;
        $$(".modeonlydisplay").each(function (elem) {
            if (elem.hasClass(modeName)) {
                disp = (blockElements.contains(elem.getTag())) ? 'block' : 'inline';
                elem.setStyle('display', disp);
            } else {
                elem.setStyle('display', 'none');
            }
        });
        $$(".modeonlyactive").each(function (elem) {
            if (elem.hasClass(modeName)) {
                elem.removeClass('inactive');
                elem.addClass('active');
            } else {
                elem.removeClass('active');
                elem.addClass('inactive');
            }
        });
    },

    // GUI:
    clickToTimeStamp: function (x, y) {
        var timeFrac, timeStamp;
        var day = this.clickToDay(x, y);
        var coords = this.dayElement(day).getCoordinates();
        timeFrac = (y - coords.top) / (coords.height - this.options.display.dayDatesHeight);
        timeStamp = this.options.weekStarts +
                   (this.days.indexOf(day) * 86400) +
                   (this.options.workingStartsHour * 3600) +
                    Math.ceil(timeFrac * this.dayLength());
        return timeStamp;
    },
    clickToDay: function (x, y) {
        var theDay;
        this.days.each(function (day) {
            if (this.dayElement(day).containsCoordinates(x, y)) { theDay = day; }
        }, this);
        return theDay;
    },
    timeStampToDay: function (timeStamp) {
        var theDay;
        this.days.each(function (day, idx) {
            if ((this.startOfDay(day) <= timeStamp) &&
                (this.endOfDay(day) >= timeStamp)) { theDay = day; }
        }, this);
        return theDay;
    },
    timeStampToTimeSlot: function (timeStamp, layer) {
        layer = layer || this.mode;
        var theSlot;
        var day = this.timeStampToDay(timeStamp);
        if (day) {
            this.registry.days[day][layer].each(function (slot) {
                if ((slot.data.dtstart <= timeStamp) &&
                    (slot.data.dtend >= timeStamp)) { theSlot = slot; }
            });
        }
        return theSlot;
    },
    // TODO: Next two methods should fail fast.
    timeSlotBeforeTimeStamp: function (timeStamp, layer) {
        layer = layer || this.mode;
        var theSlot;
        var day = this.timeStampToDay(timeStamp);
        if (day) {
            this.registry.days[day][layer].each(function (slot) {
                if (slot.data.dtend < timeStamp) {
                    theSlot = theSlot || slot;
                }
            });
        }
        return theSlot;
    },
    timeSlotAfterTimeStamp: function (timeStamp, layer) {
        layer = layer || this.mode;
        var theSlot;
        var day = this.timeStampToDay(timeStamp);
        if (day) {
            this.registry.days[day][layer].each(function (slot) {
                if (slot.data.dtstart > timeStamp) {
                    theSlot = theSlot || slot;
                }
            });
        }
        return theSlot;
    },
    clickToTimeSlot: function (x, y) {
        return this.timeStampToTimeSlot(this.clickToTimeStamp(x, y));
    },
    timeToLength: function (time) {
        var d = this.options.display;
        if (time < d.minSlot) {
            return false;
        } else {
            var slots = Math.ceil(time / d.minSlot);
            var length = (slots * d.slotHeight) + ((slots - 1) * d.slotExtra);
            return length;
        }
    },
    lengthToTime: function (length) {
        var d = this.options.display;
        var h = d.slotExtra + d.slotHeight;
        var slots = 0;
        while (length > 0) {
            length -= h;
            slots += 1;
        }
        if (length <= -(h / 2)) {
            slots -= 1;
        }
        return (slots * d.minSlot);
    },
    clearToZoom: function () {
        this.clearTimescale();
        this.clearDayDates();
        this.clearDays();
        this.element().addClass('loading');
    },
    updateView: function () {
        this.element().removeClass('loading');
        this.drawDayDates();
        this.drawTimescale();
        // TODO: replace the following with: this.drawDays(this.options.isWeekPublished);
        this.rpcService.getWeekIsPublished().callback(this.drawDays.bind(this));
    },
    clearDays: function () {
        this.layers.each(function (layer, layerName) {
            this.days.each(function (day) {
                // Clear out the old week's elements.
                this.dayElement(day, layerName).empty();
                // Get rid of SBSortables memo (or all hell will break loose
                // when we attempt to draw this day again).
                this.registry.days[day][layerName + 'Sortable'] = null;
            }, this);
        }, this);
    },
    drawDays: function (weekShown) {
        var elem = $('weekshown');
        if (elem) {
            elem.setProperty('checked', weekShown);
            if (weekShown) {
                elem.getParent().removeClass('active');
            } else {
                elem.getParent().addClass('active');
            }
        }
        if (weekShown || viewerHasRole('admin')) {
            this.element().removeClass('weekhidden');
            this.layers.each(function (layer, layerName) {
                this.days.each(function (day) {
                    this.drawDay(day, layerName);
                }, this);
            }, this);
        } else {
            this.layers.each(function (layer, layerName) {
                this.days.each(function (day) {
                    // Clear out the old week's elements.
                    this.dayElement(day, layerName).empty();
                    // Get rid of SBSortables memo (or all hell will break loose
                    // when we attempt to draw this day again).
                    this.registry.days[day][layerName + 'Sortable'] = null;
                }, this);
            }, this);
            this.element().addClass('weekhidden');
        }
    },
    clearTimescale: function () {
        var ts = this.getElement('#timescale');
        var o = this.options;
        var d = this.options.display;
        ts.empty();
        //this.element().setStyle('height', '');
    },
    drawTimescale: function () {
        var ts = this.getElement('#timescale');
        var o = this.options;
        var d = this.options.display;

        ts.empty();

        var schedHeight = d.slotHeight + d.slotExtra;
        schedHeight *= this.dayLength() / d.minSlot;
        schedHeight += d.scheduleBorder + d.dayDatesHeight;

        this.element().setStyle('height', schedHeight);

        var zeropad = function (n) { return (n > 9) ? n : ('0' + n); };
        for (var i = o.workingStartsHour; i < o.workingEndsHour; i += 1) {
            ts.adopt((new Element('li')).adopt(new Element('p').setText(zeropad(i) + ":00").setStyle('height', ((d.slotHeight + d.slotExtra) * 4) - 1)));
        }
    },
    clearDayDates: function () {
        var dd = this.getElement('#daydates');
        dd.empty();
    },
    blankDayDates: function () {
        var dd = this.getElement('#daydates');
        dd.empty();
        this.days.each(function (day) {
            var li = new Element('li');
            dd.adopt(li);
            li.setHTML('<p>-</p>');
        }, this);
    },
    drawDayDates: function () {
        var dd = this.getElement('#daydates');
        var setHead = false;
        dd.empty();
        this.days.each(function (day) {
            var ts = this.startOfDay(day);
            if (!setHead) {
                var head = $('scheddate');
                head.setText(ts);
                head.formatContentsAsTimeStamp('%d %B %Y');
                setHead = true;
            }
            var li = new Element('li');
            dd.adopt(li);
            li.setHTML('<p>' + ts + '</p>');
            li.getElement('p').formatContentsAsTimeStamp('%a %d %b');
        }, this);
    },
    drawDay: function (day, layer) {
        layer = layer || this.mode;
        var elem = this.dayElement(day, layer);
        var reg = this.registry.days[day][layer];

        elem.getChildren().each(function (elem) {
            if (!reg.contains(this.getSlot(elem))) {
                elem.remove();
            }
        }, this);

        reg = reg.sort(function (a, b) {
            if (a.data.dtstart > b.data.dtstart) {
                return 1;
            } else if (a.data.dtstart < b.data.dtstart) {
                return -1;
            } else {
                return 0;
            }
        });

        reg.each(function (slot, idx) {
            if (idx === 0) {
                $(slot.element()).injectTop(elem);
            } else {
                $(slot.element()).injectAfter(reg[idx - 1].element());
            }
            if (!slot.adopted) { slot.setup(); }
        });
        
        if (viewerHasRole('admin')) {
            this.eventManager.add('.timeslot', elem);
            this.eventManager.add('.day', elem, true); // true => forceRebind
        }
    }
});

