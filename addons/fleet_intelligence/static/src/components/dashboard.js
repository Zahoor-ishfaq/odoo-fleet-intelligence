/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class FleetDashboard extends Component {
    static template = "fleet_intelligence.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            data: null,
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        this.state.loading = true;
        const data = await this.orm.call("fleet.dashboard", "get_dashboard_data", []);
        this.state.data = data;
        this.state.loading = false;
    }

    formatCurrency(value) {
        return new Intl.NumberFormat("en-SA", {
            style: "currency",
            currency: "SAR",
            maximumFractionDigits: 0,
        }).format(value || 0);
    }

    async refresh() {
        await this.loadData();
    }
}

registry.category("actions").add("fleet_intelligence_dashboard", FleetDashboard);