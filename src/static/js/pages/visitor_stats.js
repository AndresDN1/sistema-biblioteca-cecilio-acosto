document.addEventListener("DOMContentLoaded", () => {
    const filterForm = document.getElementById("filter-form");
    const chartCanvas = document.getElementById("visitorChart");
    const totalVisitsLabel = document.getElementById("total-visits-val");
    const growthPctLabel = document.getElementById("growth-pct-val");

    let visitorChart = null;

    const renderChart = (labels, values) => {
        const ctx = chartCanvas.getContext('2d');

        if (visitorChart) {
            visitorChart.destroy();
        }

        const primaryRed = getComputedStyle(document.documentElement).getPropertyValue('--primary-red').trim();

        visitorChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Número de Visitantes',
                    data: values,
                    borderColor: primaryRed,
                    backgroundColor: 'rgba(122, 32, 24, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: primaryRed,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    };

    const updateStats = async () => {
        const formData = new FormData(filterForm);
        const params = new URLSearchParams();

        formData.forEach((value, key) => params.append(key, value));

        try {
            const response = await fetch(`/admin/stats/visitors?${params.toString()}`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });

            if (!response.ok) throw new Error("Error fetching stats");

            const data = await response.json();

            totalVisitsLabel.textContent = data.total_visits;
            growthPctLabel.textContent = `${data.growth_pct}%`;
            growthPctLabel.className = `stats-value ${data.growth_pct >= 0 ? 'text-success' : 'text-danger'}`;
            renderChart(data.labels, data.values);

        } catch (err) {
            console.error("Analytics Error:", err);
            alert("No se pudieron cargar los datos de las estadísticas.");
        }
    };

    filterForm.addEventListener("submit", (e) => {
        e.preventDefault();
        updateStats();
    });

    updateStats();
});
