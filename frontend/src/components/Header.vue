<template>
  <header class="my-header">
    <v-container align="center" id="my-toggle">
      <v-btn-toggle mandatory tile color="primary" class="d-flex flex-row my-btn-toggle">
        <v-btn class="flex-grow-1" to="/">Maschinenansicht</v-btn>
        <v-btn class="flex-grow-1" to="/production">Production Jobansicht</v-btn>
        <v-btn class="flex-grow-1" to="/background">Background Jobansicht</v-btn>
        <v-btn class="flex-grow-1" to="/table">Table</v-btn>
        <v-btn class="flex-grow-1" to="/machineOccupation">Maschinenbesetzung</v-btn>
      </v-btn-toggle>
    </v-container>
  </header>
  <v-container class="my-container">
    <v-row align="center">
      <v-col align="center">
        <p>Optimierungsstatus: {{ mappedStatus }}</p>
      </v-col>
      <v-col align="center">
          <p>Makespan: {{ makespan }} seconds</p>
      </v-col>
    </v-row>
  </v-container>
</template>
<script>
import axios from 'axios';

export default {
  data() {
    return {
      scheduleData: {},
      makespanData: {},
    };
  },
  computed: {
    mappedStatus() {
      const statusMap = {
        0: 'Empty',
        1: 'Unplanned/ Manually planned',
        2: 'Heuristic',
        3: 'Optimized',
      };
      if (Object.keys(this.scheduleData).length !== 0) {
        return statusMap[this.scheduleData["Status"]];
      }
      return "";
    },
    makespan() {
      if (Object.keys(this.makespanData).length !== 0) {
        return this.makespanData["Makespan"];
      }
      return "";
    },
  },
  created() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      axios.get('http://localhost:8000/api/jobs/getSchedule')
        .then(response => {
          this.scheduleData = response.data;
        })
        .catch(error => {
          console.log(error);
        });

      axios.get('http://localhost:8000/api/jobs/getMakespanFromDetails')
        .then(response => {
          this.makespanData = response.data;
        })
        .catch(error => {
          console.log(error);
        });        
    },
    showToggle() {
      document.getElementById('my-toggle').hidden=false;
    },
    hideToggle() {
      document.getElementById('my-toggle').hidden=true;
    },
    handlePostRequest() {
      // Make a GET request after a POST request is made
      this.fetchData();
    },
  },
  mounted() {
    // Listen for POST requests and call handlePostRequest()
    axios.interceptors.response.use((response) => {
      if (response.config.method === 'post') {
        this.handlePostRequest();
      }
      return response;
    });
  },
  beforeDestroy() {
    // Remove the interceptor when the component is destroyed
    axios.interceptors.response.eject(this.handlePostRequest);
  },
};
</script>
<style scoped>
  .my-btn-toggle .v-btn {
    border: 1px solid #ccc;
    margin: 0;
  }
</style>
