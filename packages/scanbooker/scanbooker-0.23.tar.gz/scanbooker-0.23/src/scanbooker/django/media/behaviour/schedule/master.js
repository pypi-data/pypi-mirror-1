// schedule/master.js - schedule view behaviour control

// scanBookerSchedule: global scope variable containing the main Schedule
// instance.
var scanBookerSchedule;
var scanBookerEvents;
// mediaUrl: path to media assets. Should be set in the template directly
// before inclusion of this file.
var mediaUrl;
// Global viewer auth status.
var viewerRoles;
var viewerHasRole = function (roleName) {
    if (!viewerRoles) {
        var body = document.getElement('body');
        viewerRoles =  body.getProperty("class").split(/\s+/).map(function (clsName) {
            var m = /^vieweris(.+)$/.exec(clsName);
            if (m && m[1]) {
                return m[1];
            }
        }).clean();
    }
    return viewerRoles.contains(roleName);
}

// Used so often that we may as well have a global-scope function to do this.
var setBusy = function (amBusy) {
    if (amBusy) {
        document.getElement('#schedule').setStyles({cursor: 'wait'});
    } else {
        document.getElement('#schedule').setStyles({cursor: 'auto'});
    }
}

var clearNotes = function () {

    var notesdisplay = $('notesdisplay');
    notesdisplay.setHTML('<p>Loading...</p>');
    notesdisplay.setStyle('display: block');

    var notesform = $('notesform');
    if (notesform) {
        notesform.setStyle('display', 'none');
        var textareas = notesform.getElements('textarea');
        textareas[0].value = '';
        textareas[1].value = '';
    }
}

var assets = [
    '/behaviour/vendor/stamp.js',
    '/behaviour/vendor/strftime.js',
    '/behaviour/vendor/rnd.js',
    '/behaviour/vendor/DatePicker.js',
    '/behaviour/schedule/elementobject.js',
    '/behaviour/schedule/sidebarbox.js',
    '/behaviour/schedule/templateselector.js',
    '/behaviour/schedule/eventmanager.js',
    '/behaviour/schedule/timeslot.js',
    '/behaviour/schedule/moorpc.js',
    '/behaviour/schedule/sbsortables.js',
    '/behaviour/schedule/schedule.js'
];

var assetElements = [];

assets.each(function (asset) {
    assetElements.push(new Asset.javascript(mediaUrl + asset));
});

var addNewSlot = function (ev) {
    ev = new Event(ev);
    ev.target.blur();
    if (this.editBox) {
        this.editBox.hide();
    }
    if (this.createSlotBox.visible()) {
        this.createSlotBox.hide();
        return;
    }
    var template = [
        '<h2>Select %(layer) type:</h2>',
        '<ul>',
        '%(typeslist)',
        '</ul>'
    ].join("\n");
    var data = {
        layer: this.mode,
        typeslist: ''
    };
    $each(this.layers.get(this.mode).sessionTypes, function (sessTypeName, key) {
        data.typeslist += '<li><a href="#" title="' + key + '">';
        data.typeslist += sessTypeName;
        data.typeslist += '</a></li>\n';
    });
    this.createSlotBox.element().injectAfter(ev.target.getAncestor(2));
    this.createSlotBox.redraw(RND(template, data));
    this.createSlotBox.element().getElements('a').addEvent('click', (function (ev) {
        ev = new Event(ev);
        ev.stop();
        ev.target.getAncestor(2).getElements('a').removeClass('selected');
        ev.target.addClass('selected');
        this.eventLayer.intent = "create";
        this.getElement('#evlayer').addClass('active');
    }).bind(this));

    this.createSlotBox.show();
};

var updateScheduleData = function (data) {
    if (this.editBox) {
        this.editBox.hide();
    }
    if (data.config) {
        var notesform = $('notesform');
        if (notesform) {
            notesform.setStyle('display: hidden');
            var textareas = notesform.getElements('textarea');
            textareas[0].value = data.config.weekNotesPrivate;
            textareas[1].value = data.config.weekNotesPublic;
        }
        var notesdisplay = $('notesdisplay');
        notesdisplay.setStyle('display: block');

        if (data.config.weekNotesRendered) {
            notesdisplay.setHTML(data.config.weekNotesRendered);
        } else {
            notesdisplay.setHTML('');
        }
            
    }
    this.setData(data);
    this.eventManager.add('.DatePicker');
    var d = new Date(this.startOfDay("monday") * 1000);
    document.getElement('.DatePicker').setProperty('value', d.strftime("%d-%m-%Y"));
    this.updateView();
    //setBusy(false);
};

var initSchedule = function () {
    this.templateSelector.update();
    this.rpcService.viewWeek("", "").callback(updateScheduleData.bind(this));
};

var startup = function () {
    this.setMode('session');

    this.addRpcService({
        smdUrl: scheduleSmdPath,
        onComplete: initSchedule.bind(this)
    });

    this.eventManager.append(scanBookerEvents);
    this.eventManager.addAll();
};

scanBookerEvents = {
    '#notesedit': {
        auto: true,
        click: function (ev) {
            ev = new Event(ev);
            ev.stop();
            $('notesedit').setStyle('display', 'none').blur();
            $('notesdisplay').setStyle('display', 'none');
            $('notesform').setStyle('display', 'block');
        }
    },
    '#notesform': {
        auto: true,
        submit: function (ev) {
            ev = new Event(ev);
            ev.stop();
            var textareas = $('notesform').getElements('textarea');
            var notesPrivate = textareas[0].value;
            var notesPublic = textareas[1].value;
            this.rpcService.setWeekNotes({
                notesPrivate: notesPrivate,
                notesPublic: notesPublic
            }).callback(function (data) {
                $('notesform').setStyle('display', 'none');
                $('notesedit').setStyle('display', 'block');
                $('notesdisplay').setStyle('display', 'block'
                ).setHTML(data.weekNotesRendered);
            });
        }
    },
    '.zoomin': {
        auto: true,
        click: function (ev) {
            ev = new Event(ev);
            ev.stop();
            //setBusy(true);
            this.clearToZoom();
            if (this.linesPerSlot) {
                this.linesPerSlot *= 2;
            } else {
                this.linesPerSlot = 2;
            }
            console.log(this.linesPerSlot);
            this.options.display.slotHeight = 12 + 17 * (this.linesPerSlot - 1);
            //this.updateView();
            this.rpcService.viewWeek("", "").callback(updateScheduleData.bind(this));
        }
    },
    '.zoomout': {
        auto: true,
        click: function (ev) {
            ev = new Event(ev);
            ev.stop();
            //setBusy(true);
            this.clearToZoom();
            if (this.linesPerSlot) {
                this.linesPerSlot /= 2;
            } else {
                this.linesPerSlot = 0.5;
            }
            console.log(this.linesPerSlot);
            this.options.display.slotHeight = 12 + 17 * (this.linesPerSlot - 1);
            //this.updateView();
            this.rpcService.viewWeek("", "").callback(updateScheduleData.bind(this));
        }
    },
    '.viewnextweek': {
        auto: true,
        click: function (ev) {
            ev = new Event(ev);
            ev.stop();
            //setBusy(true);
            clearNotes();
            this.clearDays();
            this.blankDayDates();
            this.element().addClass('loading');
            if (this.editBox) {
                this.editBox.hide();
            }
            this.rpcService.viewWeek("Next", "").callback(updateScheduleData.bind(this));
        }
    },
    '.viewprevweek': {
        auto: true,
        click: function (ev) {
            ev = new Event(ev);
            ev.stop();
            //setBusy(true);
            clearNotes();
            this.clearDays();
            this.blankDayDates();
            this.element().addClass('loading');
            if (this.editBox) {
                this.editBox.hide();
            }
            this.rpcService.viewWeek("Previous", "").callback(updateScheduleData.bind(this));
        }
    },
    '.DatePicker': {
        change: function (ev, elem) {
            ev = new Event(ev);
            var revIso = elem.getProperty('value');
            // TODO: is this isodate hackery really what we want to do?
            var iso = revIso.slice(6, 10) + '-' + revIso.slice(3, 5) + '-' + revIso.slice(0, 2);
            var ts = dojo.date.stamp.fromISOString(iso);
            //setBusy(true);
            if (this.editBox) {
                this.editBox.hide();
            }
            this.rpcService.viewWeek(ts.getTime() / 1000, "").callback(updateScheduleData.bind(this));
        },
        onEventsAdded: function (elem) {
            var d = new Date();
            var y = (d.getFullYear() - 2005) + 5;
            elem.setProperty('alt',
                "{format: 'dd-mm-yyyy', startDay: 1, yearRange: " + y + ", yearStart: 2005}");
            return new DatePicker(elem);
        }
    },
    '#tosessions': {
        auto: true,
        click: function () { this.setMode('session'); }
    },
    '#toearmarks': {
        auto: true,
        click: function () { this.setMode('earmark'); }
    },
    '#newsession': {
        auto: true,
        click: addNewSlot
    },
    '#newearmark': {
        auto: true,
        click: addNewSlot
    },
    '#updateview': {
        auto: true,
        click: function (ev) {
            ev = new Event(ev);
            ev.stop();
            this.updateView();
            ev.target.blur();
        }
    },
    '#evlayer': {
        auto: true,
        click: function (ev) {
            ev = new Event(ev);
            ev.stop();
            
            var d;
            var day;
            var data;
            var clickTimeStamp;
            
            this.getElement('#evlayer').removeClass('active');

            switch (this.eventLayer.intent) {
            case "create":
                this.createSlotBox.hide();

                d = this.options.display;
                clickTimeStamp = this.clickToTimeStamp(ev.page.x, ev.page.y);
                day = this.timeStampToDay(clickTimeStamp);

                data = {
                    layer: this.mode,
                    sessionType: this.createSlotBox.element().getElement('.selected').getAttribute('title')
                };

                if (this.timeStampToTimeSlot(clickTimeStamp)) {
                    alert("Sorry, but you can only create new " + this.mode + "s in free space.");
                    //setBusy(false);
                    return;
                }

                data.dtstart = Math.floor(clickTimeStamp / d.minSlot) * d.minSlot;
                data.dtend = data.dtstart + d.minSlot;

                this.createSlot(data);
                break;

            case "duplicate":
                var slot = this.eventLayer.params[0];

                d = this.options.display;
                clickTimeStamp = this.clickToTimeStamp(ev.page.x, ev.page.y);
                day = this.timeStampToDay(clickTimeStamp);

                if (this.timeStampToTimeSlot(clickTimeStamp)) {
                    alert("Sorry, but you can only create new " + this.mode + "s in free space.");
                    //setBusy(false);
                    return;
                }

                data = {id: slot.id};

                var prev = this.timeSlotBeforeTimeStamp(clickTimeStamp);
                var next = this.timeSlotAfterTimeStamp(clickTimeStamp);
                var pEnd = prev && prev.data.dtend;
                var nStart = next && next.data.dtstart;

                var gap = (nStart || this.endOfDay(day)) - (pEnd || this.startOfDay(day));

                if (gap < (slot.data.dtend - slot.data.dtstart)) {
                    alert("There's not enough room to duplicate this " + this.mode + " here.");
                    //setBusy(false);
                    return;
                }

                data.dtstart = Math.floor(clickTimeStamp / d.minSlot) * d.minSlot;

                //setBusy(true);
                this.rpcService.duplicateTimeSlot(data).callback(this.injectSlot.bind(this));
                break;
            }
        }
    },
    '#timeslotform': {
        submit: function (ev) {
            ev = new Event(ev);
            ev.stop();
            var checkValidationErrors = (function (response) {
                response = JSON.decode(response);
                if (response.errors) {
                    alert(response.errors);
                } else {
                    this.editBox.currentTimeSlot.refresh();
                    this.editBox.currentTimeSlot.updateEditBox();
                }
            }).bind(this);
            var updateFormElem = ev.target;
            while (updateFormElem.getTag() !== 'form') {
                updateFormElem = updateFormElem.getParent();
            }
            updateFormElem.set('send', {
                onComplete: checkValidationErrors
            });
            updateFormElem.send();
        }
    },
    '#weekshown': {
        auto: true,
        click: function (ev) {
            ev = new Event(ev);
            var elem = ev.target;
            var value = elem.getProperty('checked');
            elem.setProperty(!value);
            if (value) {
                elem.getParent().removeClass('active');
            } else {
                elem.getParent().addClass('active');
            }
            this.rpcService.setWeekIsPublished({isPublished: value});
        }
    }
};

window.addEvent('load', function () {
    // TODO: yucky yucky yucky browser sniffing. This is a temporary fix for IE.
    if (window.ie) {
        $('schedule').setStyles({height: "500px"});
        $('schedule').removeClass('loading');
        $('schedule').addClass('iewarning');
    } else {
        scanBookerSchedule = new Schedule({
            mediaUrl: mediaUrl
        });
        startup.bind(scanBookerSchedule)();
    }
});

