<template>
    <header>
        <v-container align="center" >
            
                <v-btn align="start" @click="showToggle" color="success" to="/">Gantt</v-btn>
                <v-btn align="end" @click="hideToggle" color="success" to="/table">Tabelle</v-btn>
            
        </v-container> 
        
        <v-container align="center" id="my-toggle">
        
                <v-btn-toggle mandatory tile color="primary" class="d-flex flex-row">
                    <v-btn class="flex-grow-1" to="/">Maschinenansicht</v-btn>
                    <v-btn class="flex-grow-1" to="/job">Jobansicht</v-btn>
                </v-btn-toggle> 
            
        </v-container>
    </header>
</template>

<script lang="ts">
  export default {
    methods: {
      showToggle() {
        document.getElementById('my-toggle').hidden=false;
      },
      hideToggle() {
        document.getElementById('my-toggle').hidden=true;
      }
    }
  }
</script>