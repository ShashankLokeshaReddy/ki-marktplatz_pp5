import { createWebHistory, createRouter } from "vue-router";
import MachineScheduler from "@/views/MachineScheduler.vue";
import OrderTable from "@/views/OrderTable.vue";
import ProductionJobScheduler from "@/views/ProductionJobScheduler.vue";
import BackgroundJobScheduler from "@/views/BackgroundJobScheduler.vue";
import MachineOccupation from "@/views/MachineOccupation.vue";

const routes = [
  {
    path: "/",
    name: "MachineScheduler",
    component: MachineScheduler,
  },
  {
    path: "/table",
    name: "OrderTable",
    component: OrderTable,
  },
  {
    path: "/production",
    name: "Production",
    component: ProductionJobScheduler,
  },
  {
    path: "/background",
    name: "Background",
    component: BackgroundJobScheduler,
  },
  {
    path: "/machineOccupation",
    name: "MachineOccupation",
    component: MachineOccupation,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;