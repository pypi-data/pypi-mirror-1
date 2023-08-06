Request.implement({
    callback: function (fn) {
        // TODO: this is an ugly place to do the conversion from JSON to data object.
        return this.addEvent('onSuccess', function () {
            fn(JSON.decode(this.response.text));
        });
    }
});

var MooRpcService = new Class({
    Implements: [Options, Events],
    initialize: function (options) {
        this.setOptions(options);
        new Request.JSON({
            url: this.options.smdUrl,
            method: 'get',
            onSuccess: this.parseResponse.bind(this)
        }).send();
    },
    parseResponse: function (resp) {
        this.response = resp;
        this.response.methods.each(function (m) {
            this.addMethod(m);
        }, this);
        this.fireEvent('onComplete', this);
    },
    addMethod: function (m) {
        this[m.name] = function () {
            return new Request({
                method: 'post',
                url: this.response.serviceURL
            }).send(escape(JSON.encode({
                method: m.name,
                params: $A(arguments)
            })));
        };
    }
});

