var timeSlotEvents = {
    '.timeslot': {
        click: function (ev) {
            ev = new Event(ev);
            var elem = ev.target;
            while (!elem.hasClass('timeslot')) {
                elem = elem.getParent();
            }
            var slot = this.getSlot(elem);
            if (slot.setAsClicked()) {
                slot.updateEditBox();
            }
        },
        onEventsAdded: function (elem) {
            var slot = this.getSlot(elem);
            var limits = slot.calcLimits();

            slot.vertsize = new SBDrag(elem.getElement('ul'), {
                handle: elem.getElement('.updown img'),
                modifiers: {x: false, y: 'height'},
                limit: {y: limits.size},
                snap: 0
            });

            slot.vertsize.addEvent('onBeforeStart', function(elem) {
                slot.memoCoordinates = elem.getCoordinates();
                slot.updateLimits();
            });
            slot.vertsize.addEvent('onComplete', function(elem) {
                if (JSON.encode(slot.memoCoordinates) !== JSON.encode(elem.getCoordinates())) {
                    slot.update();
                }
            });
        }
    },
    '.timeslot .delete': {
        click: function (ev) {
            ev = new Event(ev);
            ev.stop();
            var slot = this.getSlot(ev.target.getAncestor(4));
            slot.destroy();
        }
    },
    '.timeslot .duplicate': {
        click: function (ev) {
            ev = new Event(ev);
            ev.stop();
            //if (confirm("Duplicate this " + this.mode + "?")) {
            if (1) {
                var slot = this.getSlot(ev.target.getAncestor(4));
                this.eventLayer.intent = "duplicate";
                this.eventLayer.params = [slot];
                this.getElement('#evlayer').addClass('active');
            }
        }
    }
};

var TimeSlot = ElementObject.extend({
    options: {
        template: [
            '<ul class="vevent %(layer) %(sessionType)">',
            '   <li class="id">%(id)</li>',
            '   <li class="dtstart">%(dtstart)</li>',
            '   <li class="dtend">%(dtend)</li>',
            '   <li class="summary">%(summary)</li>',
            '   <li class="location">%(location)</li>',
            '   <li class="sessionType">%(sessionType)</li>',
            '   <li class="layer">%(layer)</li>',
            '   <li class="util adminonly">',
            '       <a class="delete" href="#/%(layer)/delete/%(id)" title="Delete this %(layer)">',
            '           <img src="%(mediaUrl)/images/icons/cross.png" alt="Delete this %(layer)">',
            '       </a>',
            '       <a class="duplicate" href="#/%(layer)/duplicate/%(id)" title="Duplicate this %(layer)">',
            '           <img src="%(mediaUrl)/images/icons/dup.png" alt="Duplicate this %(layer)">',
            '       </a>',
            '       <a class="updown" href="#/%(layer)/edit/%(id)" title="Drag to alter %(layer) end time">',
            '           <img src="%(mediaUrl)/images/icons/updown.png" alt="Drag to alter %(layer) end time">',
            '       </a>',
            '   </li>',
            '</ul>'
        ].join("\n"),

        filters: {}
    },
    data: {
        'id':          0,
        'dtstart':     0,
        'dtend':       0,
        'summary':     null,
        'location':    null,
        'sessionType': null,
        'layer':       null
    },
    initialize: function (schedule, data, options) {
        this.setOptions(options);
        this.schedule = schedule;
        this.schedule.eventManager.append(timeSlotEvents);
        this.data = $merge(this.data, data);

        $each(this.schedule.options.display, function (value, name) {
            this.options[name] = value;
        }, this);

        this.parent('li', {
            'id': this.shortName(),
            'class': 'timeslot'
        });
    },
    shortName: function () {
        return this.data.id;
    },
    day: function () {
        this.schedDay = this.schedDay || this.schedule.timeStampToDay(this.data.dtstart);
        return this.schedDay;
    },
    setup: function () {
        this.element().setHTML(RND(this.options.template, $merge(this.data, {
            summary: this.data.summary || this.data.sessionType,
            mediaUrl: this.schedule.options.mediaUrl
        }), this.options.filters));
        this.adopted = true;
        this.draw();
        return this;
    },
    dataToElem: function (data) {
        // Merge new data into existing data.
        this.data = $merge(this.data, data);
        // Infer summary info.
        this.data = $merge(this.data, {
            summary: this.data.summary || this.data.sessionType
        });
        // Put data into element(s).
        $each(this.data, function (value, key) {
            var e = this.getElement('.' + key);
            if (e) {
                e.setHTML(value);
            }
        }, this);
        // Set class for the event, layer, and session type.
        this.getElement('ul').setProperty('class', 'vevent ' + this.data.layer + ' ' + this.data.sessionType)
        // Set element's top and height from dtstart and dtend.
        this.draw();
        return this.element();
    },
    elemToData: function () {
        // Set element's top and height from dtstart and dtend.
        this.calcTimes();
        //var attrs = this.getElements('ul li');
        //attrs.each(function (li) {
        //    var cls = li.getProperty('class');
        //    // Pick out the 'dtstart' and 'dtend' text.
        //    if ((cls === 'dtstart') || (cls === 'dtend')) {
        //        this.data[cls] = li.get('text');
        //    }
        //    console.log(this.data);
        //}, this);
        return this.data;
    },
    offset: function () {
        var t = this.schedule.timeToLength(this.data.dtstart - this.schedule.startOfDay(this.day()));
        return ((t) ? (t + this.options.slotExtra) : 0);
    },
    height: function () {
        return this.schedule.timeToLength(this.data.dtend - this.data.dtstart);
    },
    draw: function () {
        this.element().setStyle('top', this.offset());
        this.element().getFirst().setStyle('height', this.height());
    },
    calcTimes: function () {
        var startOfDay = this.schedule.startOfDay(this.day());
        var endOfDay = this.schedule.endOfDay(this.day());

        var offset = this.element().getStyle('top').toInt();
        var offsetTime = startOfDay + this.schedule.lengthToTime(offset);

        if (offsetTime < startOfDay) {
            offsetTime = startOfDay;
        } else if (offsetTime > (endOfDay - this.options.minSlot)) {
            offsetTime = endOfDay - this.options.minSlot;
        }

        var height = this.element().getFirst().getStyle('height').toInt();
        var heightTime = startOfDay + this.schedule.lengthToTime(offset + height + this.options.slotExtra);

        if (heightTime < (startOfDay + this.options.minSlot)) {
            heightTime = startOfDay + this.options.minSlot;
        } else if (heightTime > endOfDay) {
            heightTime = endOfDay;
        }

        this.data.dtstart = offsetTime;
        this.data.dtend = heightTime;

        this.draw();
        this.dataToElem();
    },
    calcLimits: function () {
        var limits = {
            size: [false, false]
        };

        var o = this.options;

        var next = this.element().getNext();
        var nCoords = next && next.getCoordinates();
        var prev = this.element().getPrevious();
        var pCoords = prev && prev.getCoordinates();

        var eCoords = this.element().getCoordinates();
        var dCoords = this.element().getParent().getCoordinates();

        limits.size[0] = o.slotHeight;

        if (next) {
            limits.size[1] = nCoords.top - eCoords.top - o.slotExtra;
        } else {
            limits.size[1] = (dCoords.bottom - o.scheduleBorder - o.dayDatesHeight) - eCoords.top - o.slotExtra;
        }

        this.limits = limits;

        return limits;
    },
    updateLimits: function () {
        this.calcLimits();
        this.vertsize.options.limit.y = this.limits.size;
    },

    // Server calls
    update: function () {
        this.calcTimes();
        var handleUpdateTimeSlot = (function(response) {
            //setBusy(false);
            this.dataToElem(response);
            if (this.setAsClicked()) {
                this.updateEditBox();
            }
        }).bind(this);
        var timeSlotData = {
            id: this.data.id,
            dtstart: this.data.dtstart,
            dtend: this.data.dtend,
        }; 
        //setBusy(true);
        this.schedule.rpcService.updateTimeSlot(timeSlotData).callback(handleUpdateTimeSlot.bind(this));
    },
    refresh: function () {
        var handleUpdateTimeSlot = (function(response) {
            //setBusy(false);
            this.dataToElem(response);
        }).bind(this);
        var timeSlotData = {
            id: this.data.id
        }; 
        //setBusy(true);
        this.schedule.rpcService.updateTimeSlot(timeSlotData).callback(handleUpdateTimeSlot.bind(this));
    },
    updateWithoutEditBox: function () {
        this.elemToData();
        var handleUpdateTimeSlot = (function(response) {
            this.dataToElem(response);
            //setBusy(false);
        }).bind(this);
        this.schedule.rpcService.updateTimeSlot(this.data).callback(handleUpdateTimeSlot.bind(this));
    },
    setAsClicked: function () {
        if (this.element().hasClass('clickedtimeslot')) {
            return false;
        } else {
            this.schedule.setAllUnclicked();
            this.element().addClass('clickedtimeslot');
            return true
        }
    },
    destroy: function () {
        //setBusy(true);
        if (this.schedule.editBox) {
            this.schedule.editBox.hide();
        }
        this.schedule.rpcService.deleteTimeSlot(this.data).callback(this.schedule.destroySlot.bind(this.schedule));
    },

    updateEditBox: function () {
        this.schedule.editBox = this.schedule.editBox || new SidebarBox({id: 'editbox'});
        //if (this.schedule.editBox.currentTimeSlot == this) {
        //    this.schedule.editBox.show();
        //    setBusy(false);
        //    return;
        //}

        //var tpl = '<h2>%(id)</h2>%(editform)';
        var tpl = '<h2>Properties</h2>%(editform)';
        var data = {
            id: this.data.id
        };
        var redraw = (function (response) {
            data.editform = response.form;
            this.schedule.editBox.currentTimeSlot = this;
            this.schedule.editBox.redraw(RND(tpl, data));
            this.schedule.editBox.show();
            this.schedule.eventManager.add('#timeslotform', this.schedule.editBox.element());
        }).bind(this);
        this.schedule.rpcService.getTimeSlotUpdateForm(data).callback(redraw);
    }
});
TimeSlot.implement(new Options());


