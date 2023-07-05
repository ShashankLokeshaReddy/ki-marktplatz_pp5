<template>
  <div>
    <canvas ref="chart"></canvas>
  </div>
</template>

<script>
import Chart from 'chart.js/auto'
import axios from 'axios'

export default {
  mounted() {
    axios.get('http://' + window.location.hostname + ':8000/api/jobs/getUtilization')
      .then(response => {
        const machineData = response.data.MachineData
        console.log(machineData)
        const chartData = {
          labels: machineData.map(d => d.machineId),
          datasets: [{
            label: '% Occupancy',
            data: machineData.map(d => parseFloat(d.percentageOccupancy)),
            backgroundColor: 'rgba(213, 12, 48, 1)',
            borderColor: 'rgba(35, 48, 56, 1)',
            borderWidth: 1
          }]
        }
        const chartOptions = {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            yAxes: [{
              type: 'linear',
              ticks: {
                callback: function(value) {
                  return value.toString() + '%';
                },
                beginAtZero: true
              }
            }]
          }
        }

        const ctx = this.$refs.chart.getContext('2d')
        this.chart = new Chart(ctx, {
          type: 'bar',
          data: chartData,
          options: chartOptions
        })
      })
      .catch(error => {
        console.error(error)
      })
  },
  beforeDestroy() {
    if (this.chart) {
      this.chart.destroy()
    }
  }
}
</script>

<style>
/* Adjust the height of the chart to match the parent element */
.chart-container {
  height: 100%;
}

/* Set the bar thickness to fill the chart's width and adjust spacing */
.chartjs-render-monitor .chartjs-dataset-0 {
  barThickness: "flex";
  categorySpacing: 0.5;
}

</style>
