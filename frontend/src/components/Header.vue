<template>
  <v-container>
    <v-row align="center">
      <v-col align="center">
        <v-btn-toggle mandatory tile color="primary" class="d-flex flex-row">
          <v-btn align="start" @click="showToggle" color="success" to="/">Gantt</v-btn>
          <v-btn align="end" @click="hideToggle" color="success" to="/table">Tabelle</v-btn>
        </v-btn-toggle>
      </v-col>
      <v-col class="text-right" align="center">
        <v-btn @click="runGeneticOptimizer">Run Genetic Optimizer</v-btn>
      </v-col>
    </v-row>
  </v-container>

  <header v-if="$route.path !== '/table'">
    <v-container align="center" id="my-toggle">
      <v-btn-toggle mandatory tile color="primary" class="d-flex flex-row">
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
  methods: {
    showToggle() {
      document.getElementById('my-toggle').hidden=false;
    },
    hideToggle() {
      document.getElementById('my-toggle').hidden=true;
    },
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
};
</script>
