/** @odoo-module **/
import { registry } from "@web/core/registry";
import { onMounted } from "@odoo/owl";

export function renderSalesChart() {
    console.log("Product Turnover Chart - Initialized");

    if (typeof Chart === "undefined") {
        console.error("Chart.js is not loaded!");
        return;
    }

    const product_id = document.querySelector('input[name=id]')?.value;
    console.log("Extracted Product ID:", product_id);

    if (!product_id) {
        console.error("Product ID not found");
        return;
    }

    fetch(`/product_turnover/data/${product_id}`)
        .then(response => response.json())
        .then(data => {
            console.log("Fetched sales data:", data);

            const ctx = document.getElementById('salesChart')?.getContext('2d');
            if (ctx) {
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
            } else {
                console.error("Canvas element for Chart.js not found!");
            }
        })
        .catch(error => console.error("Failed to load sales data:", error));
}

// Spustíme funkci po načtení stránky
onMounted(() => {
    renderSalesChart();
});
