odoo.define('pos_multi_branches.pos_extended', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var core = require('web.core');

    var QWeb = core.qweb;
    var _t = core._t;

    models.load_fields("pos.session", ["branch_id"]);

});
