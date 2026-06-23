/** @odoo-module **/
import { Component, useState, onMounted, useRef, onPatched } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { loadJS } from "@web/core/assets";

export class ItParcDashboard extends Component {
    static template = "it_parc.ItParcDashboard";

    setup() {
        this.action = useService("action");
        this.notification = useService("notification");
        this.chartMaintenanceRef = useRef("chartMaintenance");
        this.chartCategoriesRef = useRef("chartCategories");

        this.state = useState({
            loaded: false,
            error: false,
            charts_ready: false,
            kpis: {
                total: 0,
                assigned: 0,
                in_maintenance: 0,
                contracts_alert: 0,
                total_cost_year: 0,
                alerts_pending: 0,
            },
            chart_maintenance: { labels: [], values: [] },
            chart_categories: { labels: [], values: [] },
        });

        onMounted(async () => {
            await this._loadData();
        });

        onPatched(() => {
            if (this.state.charts_ready) {
                this._renderCharts();
            }
        });
    }

    async _loadData() {
        try {
            const data = await rpc("/it_parc/dashboard_data", {});
            this.state.kpis = data.kpis;
            this.state.chart_maintenance = data.chart_maintenance;
            this.state.chart_categories = data.chart_categories;
            this.state.loaded = true;
            this.state.charts_ready = true;
        } catch (e) {
            console.error("Erreur dashboard:", e);
            this.state.error = true;
            this.state.loaded = true;
            this.notification.add("Impossible de charger le tableau de bord.", { type: "danger" });
        }
    }

    async _renderCharts() {
        try {
            if (typeof Chart === "undefined") {
                await loadJS("/web/static/lib/Chart/Chart.js");
            }
        } catch (e) {
            console.error("Chart.js loading failed:", e);
            return;
        }
        if (typeof Chart === "undefined") return;

        const renderOpts = {
            responsive: true,
            maintainAspectRatio: false,
        };

        const ctxMaint = this.chartMaintenanceRef.el;
        if (ctxMaint) {
            if (ctxMaint._chartInstance) ctxMaint._chartInstance.destroy();
            ctxMaint._chartInstance = new Chart(ctxMaint, {
                type: "bar",
                data: {
                    labels: this.state.chart_maintenance.labels,
                    datasets: [{
                        label: "Couts maintenance (FCFA)",
                        data: this.state.chart_maintenance.values,
                        backgroundColor: "rgba(30, 58, 95, 0.75)",
                        borderColor: "rgba(30, 58, 95, 1)",
                        borderWidth: 2,
                        borderRadius: 6,
                    }]
                },
                options: {
                    ...renderOpts,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => `${ctx.parsed.y.toLocaleString("fr-FR")} FCFA`
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: (val) => val.toLocaleString("fr-FR") + " F"
                            }
                        }
                    }
                }
            });
        }

        const ctxCat = this.chartCategoriesRef.el;
        if (ctxCat) {
            if (ctxCat._chartInstance) ctxCat._chartInstance.destroy();
            const palette = [
                "#1e3a5f", "#2563eb", "#3b82f6", "#60a5fa", "#93c5fd",
                "#0ea5e9", "#0284c7", "#0369a1", "#1d4ed8", "#1e40af"
            ];
            ctxCat._chartInstance = new Chart(ctxCat, {
                type: "doughnut",
                data: {
                    labels: this.state.chart_categories.labels,
                    datasets: [{
                        data: this.state.chart_categories.values,
                        backgroundColor: palette.slice(0, this.state.chart_categories.values.length),
                        borderWidth: 2,
                        borderColor: "#ffffff",
                    }]
                },
                options: {
                    ...renderOpts,
                    plugins: {
                        legend: { position: "right", labels: { padding: 16, font: { size: 12 } } }
                    },
                    cutout: "65%",
                }
            });
        }
    }

    formatCurrency(value) {
        return value.toLocaleString("fr-FR", { maximumFractionDigits: 0 }) + " FCFA";
    }

    navigateTo(model, state) {
        const domain = state ? [["state", "=", state]] : [];
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: model,
            views: [[false, "list"], [false, "form"]],
            domain: domain,
        });
    }

    openEquipements() { this.navigateTo("it.equipement"); }
    openAssigned() { this.navigateTo("it.equipement", "assigned"); }
    openMaintenance() { this.navigateTo("it.equipement", "maintenance"); }
    openAlerts() { this.navigateTo("it.alerte", "to_treat"); }
    openContracts() { this.navigateTo("it.contrat"); }
    openInterventions() { this.navigateTo("it.intervention"); }

    exportInventaire() { window.open("/it_parc/export/inventaire", "_blank"); }
    exportMaintenanceCosts() { window.open("/it_parc/export/couts_maintenance", "_blank"); }
    exportContratsExpirant() { window.open("/it_parc/export/contrats_expirant", "_blank"); }
    downloadSampleCSV() { window.open("/it_parc/export/sample_csv", "_blank"); }
}

registry.category("actions").add("it_parc_dashboard", ItParcDashboard);
