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
            eventMaxStack: 3,
            slotDuration: '00:05:00',
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
                    alert('Der Plan wurde gespeichert!');
                    var current_events: { resourceId : string; title: string; start: Date; end: Date; }[]
                    //current_events = this.getEvents(); //genau hier ist das Problem, dass es scheinbar keine Events bekommt.
                    (async () => {
                        const rawResponse = await fetch('https://httpbin.org/post', {
                        method: 'POST',
                        headers: {
                            'Accept': 'application/json',
                            'Content-Type': 'application/json'
                                },
                        //body: JSON.stringify(current_events)
                                });
                        const content = await rawResponse.json();

                        console.log(content);
                        })();
                }
                }
            },
            weekends: false,
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
                axios.put('http://localhost:8000/api/jobs/' + info.event.title + '/', {
                    productionStart: info.event.start,
                    productionEnd: info.event.end                  
                })
                .then(response => {
                    // Handle successful response
                    console.log(response.data)
                })
                .catch(error => {
                    // Handle error
                    console.log(error)
                })
            },
            eventDrop: (info) => {
                axios.put('http://localhost:8000/api/jobs/' + info.event.title + '/', {
                    productionStart: info.event.start,
                    productionEnd: info.event.end                  
                })
                .then(response => {
                    // Handle successful response
                    console.log(response.data)
                })
                .catch(error => {
                    // Handle error
                    console.log(error)
                })
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
            var output : { resourceId: string; jobID: string; partID: string; start: Date, end: Date, productionStart: Date, productionEnd: Date }[] = [];
            output = output_resp["Table"]
            
            var events_var = []
            for (var i = 0; i < output.length; ++i) {
                if(output[i]["productionEnd"]===null){
                    output[i]["productionEnd"] = output[i]["end"]
                }
                var temp_event = {
                    "resourceId":output[i]["resourceId"],
                    "title":output[i]["jobID"],
                    "start":output[i]["productionStart"],
                    "end":output[i]["productionEnd"],
                    "eventColor":"blue",
                    "display":'auto',
                    "className": "fwd"
                };

                if (temp_event["resourceId"] === "SL 2")
                {
                    temp_event["resourceId"] = "Maschine 1"
                }
                if (temp_event["resourceId"] === "SL 4")
                {
                    temp_event["resourceId"] = "Maschine 2"
                }
                if (temp_event["resourceId"] === "SL 5")
                {
                    temp_event["resourceId"] = "Maschine 3"
                }
                if (temp_event["resourceId"] === "SL 6")
                {
                    temp_event["resourceId"] = "Maschine 4"
                }
                if (temp_event["resourceId"] === "SL 7")
                {
                    temp_event["resourceId"] = "Maschine 5"
                }
                if (temp_event["resourceId"] === "SL 8")
                {
                    temp_event["resourceId"] = "Maschine 6"
                }
                if (temp_event["resourceId"] === "SL 9")
                {
                    temp_event["resourceId"] = "Maschine 7"
                }
                if (temp_event["resourceId"] === "SL 10")
                {
                    temp_event["resourceId"] = "Maschine 8"
                }
                if (temp_event["resourceId"] === "SL 11")
                {
                    temp_event["resourceId"] = "Maschine 9"
                }
                events_var.push(temp_event);
            }

            var resources_var: { id: string; title: string }[] = [];
            for (var i = 0; i < output.length; ++i) {
                var temp_res = {
                    "id":output[i]["resourceId"],
                    "title":output[i]["resourceId"]
                };
                resources_var.push(temp_res);
            }
            /*output = [{
               "resourceId": "SL 2",
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
</style>