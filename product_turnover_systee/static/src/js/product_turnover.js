odoo.define('product_turnover_systee.sales_chart', ['web.public.widget'], function(require) {
    "use strict";

    var publicWidget = require('web.public.widget');

    publicWidget.registry.SalesChartWidget = publicWidget.Widget.extend({
        selector: '.oe_product_form',
        start: function () {
            var self = this;
            this._super.apply(this, arguments);

            // Počkejme, než se DOM načte
            $(document).ready(function() {
                if (typeof Chart === "undefined") {
                    console.error("Chart.js is not loaded!");
                    return;
                }

                var product_id = $('input[name=id]').val();
                console.log("Extracted Product ID:", product_id);

                if (!product_id) {
                    console.error("Product ID not found");
                    return;
                }

                $.getJSON('/product_turnover/data/' + product_id, function(data) {
                    console.log("Fetched sales data:", data);
                    
                    var ctx = document.getElementById('salesChart').getContext('2d');
                    new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: data.dates,
                            datasets: [{
                                label: 'Sales',
                                data: data.sales,
                                borderColor: 'blue',
                                fill: false
                            }]
                        }
                    });
                }).fail(function() {
                    console.error("Failed to load sales data");
                });
            });
        }
    });

    return publicWidget.registry.SalesChartWidget;
});
