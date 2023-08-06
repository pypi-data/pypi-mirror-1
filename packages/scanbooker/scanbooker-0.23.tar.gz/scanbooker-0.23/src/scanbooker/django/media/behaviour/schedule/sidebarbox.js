var SidebarBox = new Class({
    Extends: ElementObject,
    Implements: Options,
    options: {
        sidebar: 'primary'
    },
    initialize: function (options) {
        this.setOptions(options);

        this.parent('div', {id: this.options.id, 'class': 'box'});
        this.element().addClass(this.options['class'] || '');
        var content = new Element('div', {'class': 'boxcontent'});
        this.element().adopt(content);
        this.element().addRoundedCorners();
        this.hide();
        $(this.options.sidebar).adopt(this.element());
    },
    content: function () {
        this.boxcontent = this.boxcontent || this.getElement('.boxcontent');
        return this.boxcontent;
    },
    redraw: function (html) {
        this.innards = html || this.innards;
        this.content().setHTML(this.innards || '');
    },
    hide: function () {
        this.element().setStyle('display', 'none');
    },
    show: function () {
        this.element().setStyle('display', 'block');
    },
    visible: function () {
        return (this.element().getStyle('display') !== 'none');
    }
});
