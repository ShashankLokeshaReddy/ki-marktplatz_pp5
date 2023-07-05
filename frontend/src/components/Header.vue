<template>
  <header class="my-header">
    <v-container fluid align="center" id="my-toggle">
      <div class="d-flex flex-row my-btn-toggle">
        <button class="my-btn" :class="{ 'my-btn-active': selectedTab === 0 }" @mouseover="hoverColor = '#D50C30'" @mouseout="hoverColor = '#233038'" @click="selectedTab = 0; $router.push('/')">Maschinenansicht</button>
        <button class="my-btn" :class="{ 'my-btn-active': selectedTab === 1 }" @mouseover="hoverColor = '#D50C30'" @mouseout="hoverColor = '#233038'" @click="selectedTab = 1; $router.push('/production')">Production-Jobansicht</button>
        <button class="my-btn" :class="{ 'my-btn-active': selectedTab === 2 }" @mouseover="hoverColor = '#D50C30'" @mouseout="hoverColor = '#233038'" @click="selectedTab = 2; $router.push('/background')">Background-Jobansicht</button>
        <button class="my-btn" :class="{ 'my-btn-active': selectedTab === 3 }" @mouseover="hoverColor = '#D50C30'" @mouseout="hoverColor = '#233038'" @click="selectedTab = 3; $router.push('/table')">Table</button>
        <button class="my-btn" :class="{ 'my-btn-active': selectedTab === 4 }" @mouseover="hoverColor = '#D50C30'" @mouseout="hoverColor = '#233038'" @click="selectedTab = 4; $router.push('/machineOccupation')">Maschinenbesetzung</button>
      </div>
    </v-container>
  </header>

  <v-container fluid class="my-container">
    <v-row align="center">
      <v-col align="center">
        <p>Optimierungsstatus: {{ mappedStatus }}</p>
      </v-col>
      <v-col align="center">
          <p>Makespan: {{ makespan }} Tage</p>
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
      selectedTab: 0
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
    selectedTab() {
      switch (this.$route.path) {
        case '/production':
          return 1;
        case '/background':
          return 2;
        case '/table':
          return 3;
        case '/machineOccupation':
          return 4;
        default:
          return 0;
      }
    },
  },
  created() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      axios.get('http://${window.location.host}:8000/api/jobs/getSchedule')
        .then(response => {
          this.scheduleData = response.data;
        })
        .catch(error => {
          console.log(error);
        });

      axios.get('http://${window.location.host}:8000/api/jobs/getMakespanFromDetails')
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
    onHover(index) {
      this.selectedTab = index;
    },
    onLeave() {
      this.selectedTab = 0;
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
  .my-btn-toggle .router-link {
    border: 5px solid #ccc;
    margin: 5px;;
  }
  .my-btn {
    font-size: 20px;
    padding: 5px 5px;
    margin: 5px 5px;
    background-color: #233038;
    color: #FFFFFF;
    text-decoration: none;
    transition: background-color 0.2s ease-in-out, color 0.2s ease-in-out;
  }
  
  .my-btn:hover,
  .my-btn-active {
    background-color: #D50C30;
    color: #FFFFFF;
  }
  
  .my-btn:hover {
    background-color: #233038;
    color: #D50C30;
  }
</style>
