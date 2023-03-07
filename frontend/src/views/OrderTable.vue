<template>

  <v-container align="center">
    <v-btn class="flex-grow-1" @click="runGeneticOptimizer">Genetic Optimizer</v-btn>
    <v-btn class="flex-grow-1" @click="runSJF">SJF</v-btn>
  </v-container>

  <v-container fluid justify="center" align="center">
    <ag-grid-vue
      style="width: 1200px; height: 30rem;"
      class="ag-theme-alpine"
      :columnDefs="columnDefs"
      :rowData="rowData"
      display = "flex"
      rowSelection="multiple"
      alignItems="start">
    </ag-grid-vue>
  </v-container>

</template>

<script lang="ts">
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import { AgGridVue } from "ag-grid-vue3";
import { reactive } from '@vue/reactivity';
import axios from 'axios';

export default {
  data(){
    return {
      columnDefs: null,
      rowData: null,
    };
  },
  components: {
    AgGridVue,
  },
  
  beforeMount() {
      this.columnDefs = [
        { headerName: "Maschine", field: "resourceId", type: 'rightAligned', filter: true },
        { headerName: "Job", field: "jobID", type: 'rightAligned', filter:true},
        { headerName: "Part ID", field: "partID", type: 'rightAligned', filter:true },
        { headerName: "Startzeit", field: "start", type: 'rightAligned', filter:true },
        { headerName: "Endzeit", field: "end", type: 'rightAligned', filter:true },
        { headerName: "Production Start", field: "productionStart", type: 'rightAligned', filter:true },
        { headerName: "Production End", field: "productionEnd", type: 'rightAligned', filter:true },
      ];
     /* this.rowData =[
        { make: "Toyota", model: "Celica", price: 35000 },
        { make: "Ford", model: "Mondeo", price: 32000 },
        { make: "Porsche", model: "Boxster", price: 72000 },
      ];*/
      fetch('http://localhost:8000/api/jobs/getSchedule')
        .then(res => res.json())
        .then(rowData => this.rowData = rowData["Table"])
        .catch(error => console.log(error));
  },

  methods: {
    runGeneticOptimizer() {
      alert('Der genetische Algorithmus optimiert im Hintergrund die Fahrpläne!');
      axios.post('http://localhost:8000/api/jobs/run_genetic_optimizer/')
        .then(response => {
          console.log(response.data); // log the response data to the console
          alert('Abgeschlossener genetischer Optimierer.');
        })
        .catch(error => {
          console.log(error); // log any errors to the console
        });
    }
  }

  }
</script>