openerp.hr_timesheet_dh = function(instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    local.HomePage = instance.Widget.extend({
        className: 'oe_timesheet_homepage',
        start: function() {
            this.$el.append("pet store home page loaded");
            var greeting = new local.GreetingsWidget(this);
            return greeting.appendTo(this.$el);
        }
    });

    local.GreetingsWidget = instance.Widget.extend({
        init: function(parent, name) {
            this._super(parent);
            this.name = name;
        },
        className: 'oe_timesheet_greetings',
        start: function() {
            this.$el.append("<div>We are so happy to see you again in this menu!</div>")
        }
    });

    instance.web.client_actions.add(
        'timesheet_dh.homepage', 'instance.hr_timesheet_dh.HomePage'
    );
};