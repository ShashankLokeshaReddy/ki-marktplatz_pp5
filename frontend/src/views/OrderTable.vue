<template>
  <v-container>
    <v-row align="center">
      <v-col align="center">
        <v-btn class="flex-grow-1" @click="runGeneticOptimizer">Genetic Optimizer</v-btn>
      </v-col>
      <v-col align="center">
        <v-btn class="flex-grow-1" @click="runSJF">SJF</v-btn>
        <v-btn class="flex-grow-1" @click="runLJF">LJF</v-btn>
        <v-btn class="flex-grow-1" @click="runDeadlineFirst">Early Deadline</v-btn>
        <v-btn class="flex-grow-1" @click="runReleaseFirst">Early Release</v-btn>
        <v-btn class="flex-grow-1" @click="runRandom">Random</v-btn>
      </v-col>
      <v-col align="center">
        <v-btn class="flex-grow-1" color="error" @click="stopProcess">Stop Process</v-btn>
      </v-col>
    </v-row>
  </v-container>

  <v-container v-if="isLoading" fluid justify="center" align="center">
    <v-progress-circular
      :size="70"
      :width="7"
      color="primary"
      indeterminate
    ></v-progress-circular>
  </v-container>

  <v-container v-else fluid justify="center" align="center">
    <ag-grid-vue
      style="width: 1200px; height: 30rem;"
      class="ag-theme-alpine"
      :columnDefs="columnDefs"
      :rowData="rowData"
      display = "flex"
      rowSelection="multiple"
      alignItems="start"
    ></ag-grid-vue>
  </v-container>
</template>

<script lang="ts">
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import { AgGridVue } from "ag-grid-vue3";
import { reactive } from "@vue/reactivity";
import axios from "axios";

export default {
  data() {
    return {
      columnDefs: null,
      rowData: null,
      isLoading: false, // new data property for loading state
    };
  },
  components: {
    AgGridVue,
  },

  beforeMount() {
    this.columnDefs = [
      { headerName: "Maschine", field: "selected_machine", type: 'rightAligned', filter: true },
      { headerName: "Job", field: "job", type: 'rightAligned', filter:true},
      { headerName: "Part ID", field: "item", type: 'rightAligned', filter:true },
      { headerName: "Startzeit", field: "start", type: 'rightAligned', filter:true },
      { headerName: "Endzeit", field: "end", type: 'rightAligned', filter:true },
      { headerName: "Production Start", field: "final_start", type: 'rightAligned', filter:true },
      { headerName: "Production End", field: "final_end", type: 'rightAligned', filter:true },
      { headerName: "Tube Type", field: "tube_type", type: 'rightAligned', filter:true },
      { headerName: "Machines", field: "machines", type: 'rightAligned', filter:true },
      { headerName: "Calculated Setup Time", field: "calculated_setup_time", type: 'rightAligned', filter:true },
      { headerName: "Tool", field: "tool", type: 'rightAligned', filter:true },
      { headerName: "Setup Time (Material)", field: "setuptime_material", type: 'rightAligned', filter:true },
      { headerName: "Setup Time (Coil)", field: "setuptime_coil", type: 'rightAligned', filter:true },
      { headerName: "Machine Duration", field: "duration_machine", type: 'rightAligned', filter:true },
      { headerName: "Manual Duration", field: "duration_manual", type: 'rightAligned', filter:true },
      { headerName: "Shift", field: "shift", type: 'rightAligned', filter:true },
      { headerName: "Latest Start", field: "latest_start", type: 'rightAligned', filter:true },
      { headerName: "Calculated Start", field: "calculated_start", type: 'rightAligned', filter:true },
      { headerName: "Calculated End", field: "calculated_end", type: 'rightAligned', filter:true },
      { headerName: "Planned Start", field: "planned_start", type: 'rightAligned', filter:true },
      { headerName: "Planned End", field: "planned_end", type: 'rightAligned', filter:true },
      { headerName: "Setup Time", field: "setup_time", type: 'rightAligned', filter:true },
      { headerName: "Status", field: "status", type: 'rightAligned', filter:true }
    ];

    fetch("http://localhost:8000/api/jobs/getSchedule")
      .then((res) => res.json())
      .then((rowData) => (this.rowData = rowData["Table"]))
      .catch((error) => console.log(error));
  },

  methods: {
    runGeneticOptimizer() {
      const confirmed = window.confirm("Möchten Sie den genetischen Optimierer ausführen?");
      if (!confirmed) {
        return;
      }
      this.isLoading = true; // show loading icon
      axios
        .post("http://localhost:8000/api/jobs/run_genetic_optimizer/")
        .then((response) => {
          console.log(response.data);
          this.isLoading = false;
        })
        .catch((error) => {
          console.log(error);
        });
    },
    runSJF() {
      const confirmed = window.confirm("Möchten Sie den SJF-Algorithmus ausführen?");
      if (!confirmed) {
        return;
      }
      this.isLoading = true; // show loading icon
      axios
        .post("http://localhost:8000/api/jobs/run_sjf/")
        .then((response) => {
          console.log(response.data);
          this.isLoading = false;
        })
        .catch((error) => {
          console.log(error);
        });
    },
    runLJF() {
      const confirmed = window.confirm("Möchten Sie den LJF-Algorithmus ausführen?");
      if (!confirmed) {
        return;
      }
      this.isLoading = true; // show loading icon
      axios
        .post("http://localhost:8000/api/jobs/run_ljf/")
        .then((response) => {
          console.log(response.data);
          this.isLoading = false;
        })
        .catch((error) => {
          console.log(error);
        });
    },
    runDeadlineFirst() {
      const confirmed = window.confirm("Möchten Sie den Early Deadline-Algorithmus ausführen?");
      if (!confirmed) {
        return;
      }
      this.isLoading = true; // show loading icon
      axios
        .post("http://localhost:8000/api/jobs/run_deadline_first/")
        .then((response) => {
          console.log(response.data);
          this.isLoading = false;
        })
        .catch((error) => {
          console.log(error);
        });
    },
    runReleaseFirst() {
      const confirmed = window.confirm("Möchten Sie den Early Release-Algorithmus ausführen?");
      if (!confirmed) {
        return;
      }
      this.isLoading = true; // show loading icon
      axios
        .post("http://localhost:8000/api/jobs/run_release_first/")
        .then((response) => {
          console.log(response.data);
          this.isLoading = false;
        })
        .catch((error) => {
          console.log(error);
        });
    },
    runRandom() {
      const confirmed = window.confirm("Möchten Sie den zufälligen Algorithmus ausführen?");
      if (!confirmed) {
        return;
      }
      this.isLoading = true; // show loading icon
      axios
        .post("http://localhost:8000/api/jobs/run_random/")
        .then((response) => {
          console.log(response.data);
          this.isLoading = false;
        })
        .catch((error) => {
          console.log(error);
        });
    },
    stopProcess() {
      axios
        .post("http://localhost:8000/api/jobs/stop_genetic_optimizer/")
        .then((response) => {
          console.log(response.data);
        })
        .catch((error) => {
          console.log(error);
        });
    },
  },

};
</script>
