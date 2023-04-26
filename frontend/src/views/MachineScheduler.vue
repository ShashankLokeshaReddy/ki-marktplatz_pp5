<template>
    <div>
        <FullCalendar ref="machinecalendar" :options="calendarOptions">
         </FullCalendar>
    </div>
</template>

<script lang="ts">

import { defineComponent } from 'vue'
import '@fullcalendar/core/vdom'
import FullCalendar from '@fullcalendar/vue3'
import DayGridPlugin from '@fullcalendar/daygrid'
import TimegridPlugin from '@fullcalendar/timegrid'
import InteractionPlugin from '@fullcalendar/interaction'
import ListPlugin from '@fullcalendar/list'
import ResourceTimelinePlugin from '@fullcalendar/resource-timeline'
import axios from 'axios'
import moment from 'moment';

const holidays = ["2022-01-01", "2022-04-15", "2022-04-16", "2022-04-17", "2022-04-18", "2022-05-01", "2022-05-26", "2022-05-27", "2022-05-28", "2022-06-05", "2022-06-06", "2022-06-16", "2022-06-17", "2022-06-18", "2022-10-03", "2022-10-31", "2022-11-01", "2022-12-24", "2022-12-25", "2022-12-26", "2022-12-27", "2022-12-28", "2022-12-29", "2022-12-30", "2022-12-31"];

export default defineComponent({
     
    //props: [FullCalendar],
    components: {FullCalendar},
    data()  {
        return {
            calendarApi: null,
            calendarOptions: {
            plugins: [ 
                DayGridPlugin,
                TimegridPlugin,
                InteractionPlugin,
                ListPlugin,
                ResourceTimelinePlugin,
            ],
            selectOverlap: false,
            eventOverlap: false,
            eventMaxStack: 3,
            slotDuration: '00:05:00',
            slotLabelContent: ({ date }) => {
                const hour = date.getHours();
                const minute = date.getMinutes();
                const startHour = 0;
                const endHour = 24;
            },
            slotLabelClassNames: ({ date, isLabel }) => {
                const hour = date.getHours();
                const startHour = 7;
                const endHour = 23;
                const classNames = ["slot-label"];
                const holidays = ["2022-01-01", "2022-04-15", "2022-04-16", "2022-04-17", "2022-04-18", "2022-05-01", "2022-05-26", "2022-05-27", "2022-05-28", "2022-06-05", "2022-06-06", "2022-06-16", "2022-06-17", "2022-06-18", "2022-10-03", "2022-10-31", "2022-11-01", "2022-12-24", "2022-12-25", "2022-12-26", "2022-12-27", "2022-12-28", "2022-12-29", "2022-12-30", "2022-12-31"];
                const formattedDate = date.toISOString().substring(0, 10);
                if (holidays.includes(formattedDate)) {
                    classNames.push("weekend-non-operating-hours");
                } else if ( (hour < startHour || hour >= endHour) && ![0, 6].includes(date.getDay()) ) {
                    classNames.push("non-operating-hours");
                } else if ( ([0, 6].includes(date.getDay())) ) {
                    classNames.push("weekend-non-operating-hours");
                } else {
                    classNames.push("operating-hours");
                }
                
                if (isLabel) {
                    classNames.push("date-label");
                }

                return classNames.join(" ");
            },
            slotLaneClassNames: ({ date, isLabel }) => {
                const hour = date.getHours();
                const startHour = 7;
                const endHour = 23;
                const classNames = ["slot-label"];
                const holidays = ["2022-01-01", "2022-04-15", "2022-04-16", "2022-04-17", "2022-04-18", "2022-05-01", "2022-05-26", "2022-05-27", "2022-05-28", "2022-06-05", "2022-06-06", "2022-06-16", "2022-06-17", "2022-06-18", "2022-10-03", "2022-10-31", "2022-11-01", "2022-12-24", "2022-12-25", "2022-12-26", "2022-12-27", "2022-12-28", "2022-12-29", "2022-12-30", "2022-12-31"];
                const formattedDate = date.toISOString().substring(0, 10);
                if (holidays.includes(formattedDate)) {
                    classNames.push("weekend-non-operating-hours");
                } else if ( (hour < startHour || hour >= endHour) && ![0, 6].includes(date.getDay()) ) {
                    classNames.push("non-operating-hours");
                } else if ( ([0, 6].includes(date.getDay())) ) {
                    classNames.push("weekend-non-operating-hours");
                } else {
                    classNames.push("operating-hours");
                }
                
                if (isLabel) {
                    classNames.push("date-label");
                }

                return classNames.join(" ");
            },
            locale: "ger",
            initialView: 'resourceTimelineDay',
            schedulerLicenseKey: 'CC-Attribution-NonCommercial-NoDerivatives',
            headerToolbar: {
                left: 'prev next today myCustomButton',
                center: 'title',
                right: 'resourceTimelineMonth resourceTimelineWeek resourceTimelineDay',
            },
            customButtons: {
                myCustomButton: {
                    text: 'speichern',
                    click: function() {
                        const confirmed = window.confirm("Möchten Sie alle Jobs in einer CSV-Datei speichern?");
                        if (!confirmed) {
                            return;
                        }
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
                    }
                }
            },
            weekends: true,
            editable: true,
            
            resourceAreaColumns: [
                {
                field: 'title',
                headerContent: 'Machines'
                }
            ],

            resources: [],
            events: [] as { resourceId : string; title: string; start: Date; end: Date; eventTextColor : string;}[],
            eventDidMount: (info) => {
                info.el.style.background = `blue`;
                info.el.style.color = "white";
            },
            eventResize: (info) => {
                // Get the selected machine
                var resources = info.event.getResources();
                var selectedMachine = resources[0]["title"];
                
                var machines = info.event.extendedProps.machines;
                var allowedMachines = machines.split(',');
                
                // Check whether the selected machine is allowed
                if (allowedMachines.includes(selectedMachine)) {
                    const jobs_data = {
                    job: info.event.title,
                    final_start: info.event.start,
                    final_end: info.event.end,
                    selected_machine: selectedMachine
                    };

                    const formData = new FormData();
                    for (let key in jobs_data) {
                    formData.append(key, jobs_data[key]);
                    }

                    axios.post('http://localhost:8000/api/jobs/setInd/', formData)
                    .then(response => {
                        console.log(response.data);
                    })
                    .catch(error => {
                        console.log(error);
                    });
                } 
                else {
                    // If the selected machine is not allowed, revert the event to its original position
                    info.revert();
                    alert('Cannot drop event as it has constraints to run on following machines: ' + info.event.extendedProps.machines);
                }
            },
            eventDrop: (info) => {
                // Get the selected machine
                var resources = info.event.getResources();
                var selectedMachine = resources[0]["title"];
                
                var machines = info.event.extendedProps.machines;
                var allowedMachines = machines.split(',');
                
                // Check whether the selected machine is allowed
                if (allowedMachines.includes(selectedMachine)) {
                    const jobs_data = {
                    job: info.event.title,
                    final_start: info.event.start,
                    final_end: info.event.end,
                    selected_machine: selectedMachine
                    };
                    console.log("jobs_data at VUe:",jobs_data);
                    const formData = new FormData();
                    for (let key in jobs_data) {
                    formData.append(key, jobs_data[key]);
                    }

                    axios.post('http://localhost:8000/api/jobs/setInd/', formData)
                    .then(response => {
                        console.log(response.data);
                    })
                    .catch(error => {
                        console.log(error);
                    });
                } 
                else {
                    // If the selected machine is not allowed, revert the event to its original position
                    info.revert();
                    alert('Cannot drop event as it has constraints to run on following machines: ' + info.event.extendedProps.machines);
                }
            },
            mounted() {
                this.$nextTick(() => {
                    let calendar = this.$refs.machinecalendar.getApi();
                    let currentView = calendar.view;
                    console.log(currentView.type);
                })
            }
            },
        }
    },
    async created(){
        var response = await fetch('http://localhost:8000/api/jobs/getSchedule')
        var output_resp = await response.json()
        var status = output_resp["Status"]
        var output : { selected_machine: string; machines: string; job: string; item: string; start: Date, end: Date, final_start: Date, final_end: Date }[] = [];
        output = output_resp["Table"]
        
        var events_var = []
        for (var i = 0; i < output.length; ++i) {
            if(output[i]["final_end"]===null){
                output[i]["final_end"] = output[i]["end"]
            }
            var temp_event = {
                "resourceId":output[i]["selected_machine"],
                "title":output[i]["job"],
                "start":output[i]["final_start"],
                "end":output[i]["final_end"],
                "eventColor":"blue",
                "display":'auto',
                "className": "fwd",
                "extendedProps": {
                    "machines": output[i]["machines"]
                }
            };
            events_var.push(temp_event);
        }

        var resources_var: { id: string; title: string }[] = [];
        for (var i = 0; i < output.length; ++i) {
            var temp_res = {
                "id":output[i]["selected_machine"],
                "title":output[i]["selected_machine"]
            };
            resources_var.push(temp_res);
        }
        /*output = [{
            "selected_machine": "SL 2",
            "title": "12403",
            "start": new Date("2016-02-26T11:54:52Z"),
            "end": new Date("2022-09-13T14:10:06Z")
                }]*/
        var machinecount = resources_var.length
        console.log(machinecount)
        
        this.calendarOptions["events"] = events_var
        this.calendarOptions["resources"] = resources_var
        console.log(this.calendarOptions["events"])
    }

})

</script>

<style>
.bck{
    height:10px;
    vertical-align: center;
}
.fwd{
    height:20px;
    vertical-align: center;
}
.slot-label.operating-hours {
  background-color: #d3d3d3;
}
.slot-label.non-operating-hours {
  background-color: #7f7f7f;
}
.slot-label.weekend-non-operating-hours {
  background-color: #151515;
  color: #FFFFFF;
}
.date-label {
  font-weight: bold;
  text-align: center;
}
</style>