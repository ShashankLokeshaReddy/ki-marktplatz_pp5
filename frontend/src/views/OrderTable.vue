<template>
  <v-container fluid justify="center" align="center">
  <ag-grid-vue
    style="width: 1200px; height: 30rem;"
    class="ag-theme-alpine"
    :columnDefs="columnDefs"
    :rowData="rowData"
    display = "flex"
    rowSelection="multiple"
    alignItems="start"
   
    
  >
  </ag-grid-vue>
</v-container>

</template>

<script lang="ts">
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import { AgGridVue } from "ag-grid-vue3";
import { reactive } from '@vue/reactivity';

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
        { headerName: "Kundennummer", field: "title", type: 'rightAligned', filter:true},
        { headerName: "Startzeit", field: "start", type: 'rightAligned', filter:true },
        { headerName: "Endzeit", field: "end", type: 'rightAligned', filter:true },
        { headerName: "Auftragsnummer", field: "AKNR", type: 'rightAligned', filter:true },
        { headerName: "Schrittnummer", field: "SchrittNr", type: 'rightAligned', filter:true },
      ];
     /* this.rowData =[
        { make: "Toyota", model: "Celica", price: 35000 },
        { make: "Ford", model: "Mondeo", price: 32000 },
        { make: "Porsche", model: "Boxster", price: 72000 },
      ];*/
      fetch('http://localhost:8000/api/machines/')
        .then(res => res.json())
        .then(rowData => this.rowData = rowData)
        .catch(error => console.log(error));
    },
    
  }
</script>