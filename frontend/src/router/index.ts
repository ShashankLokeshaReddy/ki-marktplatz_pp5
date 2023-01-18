import { createWebHistory, createRouter } from "vue-router";
import MachineScheduler from "@/views/MachineScheduler.vue";
import OrderTable from "@/views/OrderTable.vue";
import JobScheduler from "@/views/JobScheduler.vue";

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
    path: "/job",
    name: "JobScheduler",
    component: JobScheduler,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;