<template>
  <v-container class="my-container">
    <v-row align="center">
      <v-col align="center">
        <v-btn-toggle mandatory tile color="primary" class="d-flex flex-row my-btn-toggle">
          <v-btn align="start" @click="showToggle" color="success" to="/">Gantt</v-btn>
          <v-btn align="end" @click="hideToggle" color="success" to="/table">Table</v-btn>
        </v-btn-toggle>
      </v-col>
      <v-col align="center">
          <p>Optimization Status: {{ mappedStatus }}</p>
      </v-col>
    </v-row>
  </v-container>
  <header v-if="$route.path !== '/table'" class="my-header">
    <v-container align="center" id="my-toggle">
      <v-btn-toggle mandatory tile color="primary" class="d-flex flex-row my-btn-toggle">
        <v-btn class="flex-grow-1" to="/">Maschinenansicht</v-btn>
        <v-btn class="flex-grow-1" to="/production">Production Jobansicht</v-btn>
        <v-btn class="flex-grow-1" to="/background">Background Jobansicht</v-btn>
      </v-btn-toggle>
    </v-container>
  </header>
</template>
<script>
import axios from 'axios';

export default {
  data() {
    return {
      scheduleData: {},
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
  },
  mounted() {
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
    },
    showToggle() {
      document.getElementById('my-toggle').hidden=false;
    },
    hideToggle() {
      document.getElementById('my-toggle').hidden=true;
    },
  },
  watch: {
    scheduleData: {
      handler() {
        this.fetchData();
      },
      deep: true,
    },
  },
};
</script>
<style scoped>
  .my-btn-toggle .v-btn {
    border: 1px solid #ccc;
    margin: 0;
  }
</style>