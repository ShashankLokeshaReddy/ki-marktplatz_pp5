<template>
  <v-container>
    <v-row align="center">
      <v-col align="center" class="mb-4">
        <v-btn class="bordered flex-grow-1 mr-2" @click="runSJF">SJF</v-btn>
        <v-btn class="bordered flex-grow-1 mr-2" @click="runLJF">LJF</v-btn>
        <v-btn class="bordered flex-grow-1 mr-2" @click="runDeadlineFirst">Early Deadline</v-btn>
        <v-btn class="bordered flex-grow-1 mr-2" @click="runReleaseFirst">Early Release</v-btn>
        <v-btn class="bordered flex-grow-1" @click="runRandom">Random</v-btn>
      </v-col>
      <v-col align="center" class="mb-4">
        <v-btn class="bordered flex-grow-1 mr-2" @click="runGeneticOptimizer">Genetic Optimizer</v-btn>
        <v-btn class="bordered flex-grow-1 mr-2" color="error" @click="stopProcess">GA stoppen</v-btn>
        <v-btn class="bordered flex-grow-1 mr-2" @click="saveJobs">Save Job Orders</v-btn>
      </v-col>
      <v-col align="center" class="mb-4">
        <input type="file" ref="fileInput" @change="handleFileUpload"/>
        <v-btn class="bordered" @click="upload">Arbeitsaufträge hochladen</v-btn>
        <v-btn class="bordered" color="error" @click="deleteJobs">Arbeitsaufträge löschen</v-btn>
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
    this.fillTable();
  },

  methods: {
    saveJobs() {
      const confirmed = window.confirm("Möchten Sie alle Jobs in einer CSV-Datei speichern?");
      if (!confirmed) {
        return;
      }
      this.isLoading = true; // show loading icon
      axios
        .post("http://localhost:8000/api/jobs/savejobstoCSV/")
        .then((response) => {
          console.log(response.data);
          this.isLoading = false;
          window.alert(response.data.message);
          this.fillTable();
        })
        .catch((error) => {
          console.log(error);
        });
    },
    fillTable() {
      // Define saveButtonRenderer
      const saveButtonRenderer = params => {
        const button = document.createElement('button')
        button.innerText = 'Save'
        button.addEventListener('click', () => {
          const rowData = params.node.data
          const jobs_data = {
            selected_machine: rowData.selected_machine,
            job: rowData.job,
            item: rowData.item,
            start: rowData.start,
            end: rowData.end,
            final_start: rowData.final_start,
            final_end: rowData.final_end,
            tube_type: rowData.tube_type,
            machines: rowData.machines,
            tool: rowData.tool,
            setuptime_material: rowData.setuptime_material,
            setuptime_coil: rowData.setuptime_coil,
            duration_machine: rowData.duration_machine,
            shift: rowData.shift,
            setup_time: rowData.setup_time,
            status: rowData.status
          };

          const formData = new FormData();
          for (let key in jobs_data) {
          formData.append(key, jobs_data[key]);
          }
          
          axios.post('http://localhost:8000/api/jobs/setInd_Table/', formData)
          .then(response => {
              console.log(response.data);
          })
          .catch(error => {
              console.log(error);
          });

        })
        return button
      }

      this.columnDefs = [
        { headerName: "Job", field: "job", type: 'rightAligned', filter:true },
        { headerName: "Maschine", field: "selected_machine", type: 'rightAligned', filter: true, editable: true },
        { headerName: "Part ID", field: "item", type: 'rightAligned', filter:true, editable: true },
        { headerName: "Startzeit", field: "start", type: 'rightAligned', filter:true, editable: true },
        { headerName: "Endzeit", field: "end", type: 'rightAligned', filter:true, editable: true },
        { headerName: "Production Start", field: "final_start", type: 'rightAligned', filter:true, editable: true },
        { headerName: "Production End", field: "final_end", type: 'rightAligned', filter:true, editable: true },
        { headerName: "Tube Type", field: "tube_type", type: 'rightAligned', filter:true, editable: true },
        { headerName: "Machines", field: "machines", type: 'rightAligned', filter:true, editable: true },
        { headerName: "Calculated Setup Time", field: "calculated_setup_time", type: 'rightAligned', filter:true, editable: true },
        { headerName: "Tool", field: "tool", type: 'rightAligned', filter:true, editable: true },
        { headerName: "Setup Time (Material)", field: "setuptime_material", type: 'rightAligned', filter:true, editable: true },
        { headerName: "Setup Time (Coil)", field: "setuptime_coil", type: 'rightAligned', filter:true, editable: true },
        { headerName: "Machine Duration", field: "duration_machine", type: 'rightAligned', filter:true, editable: true },
        { headerName: "Manual Duration", field: "duration_manual", type: 'rightAligned', filter:true, editable: true },
        { headerName: "Shift", field: "shift", type: 'rightAligned', filter:true, editable: true },
        { headerName: "Setup Time", field: "setup_time", type: 'rightAligned', filter:true, editable: true },
        { headerName: "Status", field: "status", type: 'rightAligned', filter:true, editable: true },
        { headerName: "Action", cellRenderer: saveButtonRenderer}
      ];

      fetch("http://localhost:8000/api/jobs/getSchedule")
        .then((res) => res.json())
        .then((rowData) => (this.rowData = rowData["Table"]))
        .catch((error) => console.log(error));
    },
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
          this.fillTable();
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
          this.fillTable();
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
          this.fillTable();
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
          this.fillTable();
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
          this.fillTable();
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
          this.fillTable();
        })
        .catch((error) => {
          console.log(error);
        });
    },
    deleteJobs() {
      const confirmed = window.confirm("Möchten Sie alle Jobs löschen?");
      if (!confirmed) {
        return;
      }
      this.isLoading = true; // show loading icon
      axios
        .post("http://localhost:8000/api/jobs/deleteJobs/")
        .then((response) => {
          console.log(response.data);
          this.isLoading = false;
          window.alert(response.data.message);
          this.fillTable();
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
          this.fillTable();
        })
        .catch((error) => {
          console.log(error);
        });
    },
    handleFileUpload(event) {
      this.file = event.target.files[0];
    },
    upload() {
      const formData = new FormData();
      formData.append('file', this.file);
      this.isLoading = true;
      axios.post('http://localhost:8000/api/jobs/uploadCSV/', formData)
        .then(response => {
          console.log(response.data);
          this.isLoading = false;
          window.alert(response.data.message);
          this.fillTable();
        })
        .catch(error => {
          console.log(error);
        });
      },
    },
  },

};
</script>

<style>
  button.v-btn {
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 6px 12px; /* smaller padding */
    font-size: 12px; /* smaller font size */
    font-weight: 500;
    text-transform: uppercase;
    color: #333;
    background-color: #fff;
  }

  button.v-btn:hover {
    border-color: #999;
    color: #666;
    background-color: #f5f5f5;
  }

  button.v-btn:active,
  button.v-btn:focus {
    outline: none;
    box-shadow: none;
  }

  label.v-btn {
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 6px 12px; /* smaller padding */
    font-size: 12px; /* smaller font size */
    font-weight: 500;
    text-transform: uppercase;
    color: #333;
    background-color: #fff;
  }

  label.v-btn:hover {
    border-color: #999;
    color: #666;
    background-color: #f5f5f5;
  }

  label.v-btn:active,
  label.v-btn:focus {
    outline: none;
    box-shadow: none;
  }
</style>
