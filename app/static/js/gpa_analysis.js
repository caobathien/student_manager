document.addEventListener('DOMContentLoaded', function() {   
    // Lấy canvas cho biểu đồ cột (Bar)
    const barChartCanvas = document.getElementById('gpaDistributionChart');
    // Dùng JSON.parse để chuyển chuỗi data-labels thành mảng JavaScript
    const distributionLabels = JSON.parse(barChartCanvas.dataset.labels);
    const distributionData = JSON.parse(barChartCanvas.dataset.values);

    // Lấy canvas cho biểu đồ đường (Line)
    const lineChartCanvas = document.getElementById('gpaByClassChart');
    const classLabels = JSON.parse(lineChartCanvas.dataset.labels);
    const classData = JSON.parse(lineChartCanvas.dataset.values);

    // Lấy canvas cho biểu đồ tròn (Pie)
    const pieChartCanvas = document.getElementById('riskChart');
    // Dữ liệu rủi ro là một đối tượng lớn
    const classRiskData = JSON.parse(pieChartCanvas.dataset.risk);
    let currentRiskData = classRiskData['all'] || { high_risk: 0, low_risk: 0 };

    let barChart, lineChart, pieChart;

    // Hàm tạo biểu đồ cột
    function createBarChart() {
        const ctx1 = barChartCanvas.getContext('2d');
        barChart = new Chart(ctx1, {
            type: 'bar',
            data: {
                labels: distributionLabels,
                datasets: [{
                    label: 'Số lượng sinh viên',
                    data: distributionData,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(255, 205, 86, 0.6)',
                        'rgba(75, 192, 192, 0.6)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 205, 86, 1)',
                        'rgba(75, 192, 192, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    // Hàm tạo biểu đồ đường
    function createLineChart() {
        const ctx2 = lineChartCanvas.getContext('2d');
        lineChart = new Chart(ctx2, {
            type: 'line',
            data: {
                labels: classLabels,
                datasets: [{
                    label: 'GPA Trung bình',
                    data: classData,
                    fill: false,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    tension: 0.1,
                    pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 4.0
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    // Hàm tạo biểu đồ tròn
    function createPieChart() {
        const ctx3 = pieChartCanvas.getContext('2d');
        pieChart = new Chart(ctx3, {
            type: 'pie',
            data: {
                labels: ['Nguy cơ cao', 'Nguy cơ thấp'],
                datasets: [{
                    data: [currentRiskData.high_risk || 0, currentRiskData.low_risk || 0],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(75, 192, 192, 0.6)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(75, 192, 192, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }

    // Hàm cập nhật biểu đồ tròn
    function updatePieChart(selectedClass) {
        currentRiskData = classRiskData[selectedClass] || { high_risk: 0, low_risk: 0 };
        if (pieChart) {
            pieChart.data.datasets[0].data = [currentRiskData.high_risk || 0, currentRiskData.low_risk || 0];
            pieChart.update();
        }
    }

    // Tạo biểu đồ ban đầu
    createBarChart();
    createLineChart();
    createPieChart();

    // Xử lý sự kiện checkbox
    document.getElementById('showBarChart').addEventListener('change', function() {
        const container = document.getElementById('barChartContainer');
        if (this.checked) {
            container.style.display = 'block';
            if (!barChart) createBarChart();
        } else {
            container.style.display = 'none';
        }
    });

    document.getElementById('showLineChart').addEventListener('change', function() {
        const container = document.getElementById('lineChartContainer');
        if (this.checked) {
            container.style.display = 'block';
            if (!lineChart) createLineChart();
        } else {
            container.style.display = 'none';
        }
    });

    document.getElementById('showPieChart').addEventListener('change', function() {
        const container = document.getElementById('pieChartContainer');
        if (this.checked) {
            container.style.display = 'block';
            if (!pieChart) createPieChart();
        } else {
            container.style.display = 'none';
        }
    });

    // Xử lý sự kiện chọn lớp
    document.getElementById('classFilter').addEventListener('change', function() {
        const selectedClass = this.value;
        updatePieChart(selectedClass);
    });
});