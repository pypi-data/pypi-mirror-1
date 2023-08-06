
var templateSelectorEvents = {
    '#templateselector form': {
        submit: function (ev) {
            ev = new Event(ev);
            ev.stop();
            ev.target.blur();
        }
    },
    '#templateselector #selecttemplate': {
        click: function (ev) {
            ev = new Event(ev);
            ev.stop();
            var t = this.templateSelector;
            var name = t.box.getElement('#templatename').value;
            if (this.isEmptyWeek() ||
                confirm("Are you sure you wish to apply the '" + name +
                        "' template to this week? This will erase " +
                        "all this week's exiting earmarks.")) {
                t.selectTemplate(name);
            }
        }
    },
    '#templateselector #createtemplate': {
        click: function (ev) {
            ev = new Event(ev);
            ev.stop();
            var t = this.templateSelector;
            var name = t.box.getElement('#templatename').value;
            if (confirm("Are you sure you wish to save the current week as the " +
                        "'" + name + "' template?")) {
                t.createTemplate(name);
            }
        }
    },
    '#templateselector #deletetemplate': {
        click: function (ev) {
            ev = new Event(ev);
            ev.stop();
            var t = this.templateSelector;
            var name = t.box.getElement('#templatename').value;
            if (name === "Standard") {
                alert("Sorry, you can't delete the standard template.");
            } else if (confirm("Are you sure you wish to permanently remove the "
                       + "'" + name + "' template from the list?")) {
                t.deleteTemplate(name);
            }
        }
    },
    '#templateselector #templatename': {
        change: function (ev) {
            ev = new Event(ev);
            var t = this.templateSelector;
            var s = t.box.element().getElementById('templatename');
            var selected = s.getProperty('value').trim();

            var onblur = function (ev) {
                ev = new Event(ev);
                var s = t.box.element().getElementById('templatename');
                var name = s.getProperty('value').trim();
                if (s.getTag() === 'input') {
                    if (name !== '') {
                        this.addTemplateName(name);
                        this.setSelected(name);
                    }
                    this.redraw();
                }
            };

            if (selected === 'New template...') {
                var r = new Element('input', {
                    type: 'text',
                    id: 'templatename',
                    size: 15,
                    events: { blur: onblur.bind(t) }
                });
                t.box.getElement('#selecttemplate').setProperty('disabled', 'disabled');
                t.box.getElement('#deletetemplate').setProperty('disabled', 'disabled');
                r.replaces(s);
                r.focus();
            } else {
                t.setSelected(selected);
                t.redraw();
            }
        }
    }
};

var TemplateSelector = new Class({
    Implements: Options,
    options: {
        id: 'templateselector',
        template: [
            '<h2>Templates:</h2>',
            '<form method="post">',
            '  <p>',
            '    <select id="templatename">',
            '      %(optionlist)',
            '       <option name="_new">New template...</option>',
            '    </select>',
            '  </p>',
            '  <p>',
            '    <input type="button" id="selecttemplate" value="Change times" />',
            '    <input type="button" id="createtemplate" value="Save times" />',
            '  </p>',
            '  <p>',
            '    <input type="button" id="deletetemplate" value="Delete template" />',
            '  </p>',
            '</form>'
        ].join("\n")
    },
    data: {},
    initialize: function (schedule, options) {
        this.setOptions(options);
        this.schedule = schedule;
        this.templateNames = [];
        this.extraTemplateNames = [];

        this.schedule.eventManager.append(templateSelectorEvents);

        this.box = new SidebarBox({id: this.options.id, 'class': 'modeonlydisplay earmark'});
        this.box.show();
    },
    setSelected: function (name) {
        this.selected = name;
    },
    update: function () {
        this.extraTemplateNames = [];
        this.schedule.rpcService.getEarmarkTemplateNames().callback(this.redraw.bind(this));
    },
    redraw: function (templateNames) {
        this.templateNames = templateNames || this.templateNames;
        this.data.optionlist = this.optionlist();
        this.box.redraw(RND(this.options.template, this.data));
        if (this.extraTemplateNames.contains(this.box.getElement('#templatename').getProperty('value'))) {
            this.box.getElement('#selecttemplate').setProperty('disabled', 'disabled');
            this.box.getElement('#deletetemplate').setProperty('disabled', 'disabled');
        } else {
            this.box.getElement('#selecttemplate').removeProperty('disabled');
            this.box.getElement('#deletetemplate').removeProperty('disabled');
        }
        this.schedule.eventManager.add('#' + this.options.id, this.box.element());
    },
    selectTemplate: function (name) {
        setBusy(true);
        this.schedule.rpcService.earmarkCurrentWeek(name).callback(initSchedule.bind(this.schedule));
    },
    createTemplate: function (name) {
        this.schedule.rpcService.createEarmarkTemplate(name).callback(this.update.bind(this));
    },
    deleteTemplate: function (name) {
        this.schedule.rpcService.deleteEarmarkTemplate(name).callback(this.update.bind(this));
    },
    addTemplateName: function (name) {
        // For the moment we only allow one at a time;
        this.extraTemplateNames = [name];
    },
    optionlist: function () {
        var o = '';
        this.templateNames.merge(this.extraTemplateNames).each(function (name) {
            o += '<option name="' + name + '"';
            if (this.selected === name) {
                o += ' selected="selected"';
            }
            o += '>' + name + '</option>\n';
        }, this);
        return o;
    }
});

