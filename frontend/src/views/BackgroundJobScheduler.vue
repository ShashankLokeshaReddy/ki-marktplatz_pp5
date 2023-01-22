<template>
    <div>
        <FullCalendar ref="calendar" :options="calendarOptions">
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
                headerContent: 'Jobs'
                }
            ],

            resources: [],
            events: [] as { resourceId : string; title: string; start: Date; end: Date; eventTextColor : string;}[],
            eventDidMount: (info) => {
                let calendar: any = this.$refs.calendar.getApi();
                let view_start = calendar.currentData.calendarApi.currentData.dateProfile.activeRange.start;
                let view_end = calendar.currentData.calendarApi.currentData.dateProfile.activeRange.end;
                let offset_start = view_start.getTimezoneOffset();
                let gmtTime_view_start = new Date(view_start.getTime() + offset_start * 60 * 1000);
                let offset_end = view_end.getTimezoneOffset();
                let gmtTime_view_end = new Date(view_end.getTime() + offset_end * 60 * 1000);
                var resources = info.event.getResources();
                var all_events = resources[0].getEvents()
                var bck_event
                for (let i = 0; i < all_events.length; i++) {
                    if (all_events[i].classNames[0] === "bck"){ //info.event.title
                        bck_event = all_events[i]
                    }
                }
                if(info.event.classNames[0] === "fwd"){
                    var override_start = info.event.start;
                    var override_end = info.event.end;
                    if(info.event.end > gmtTime_view_end){
                        override_end = gmtTime_view_end;
                    }
                    if(info.event.start < gmtTime_view_start){
                        override_start = gmtTime_view_start;
                    }
                }
                console.log(view_start,view_end);
                console.log(info.event.title,info.event.start,info.event.end);
                console.log(bck_event.title,bck_event.start,bck_event.end);
                if((info.event.end > bck_event.end) && (info.event.classNames[0] === "fwd")){
                    var numerator = bck_event.end - override_start;
                    var denominator = override_end - override_start;
                    var delta = numerator*100/denominator;
                    info.el.style.background = `linear-gradient(90deg, blue ${delta}%, red 0%)`;
                    info.el.style.color = "white";
                }
                else if(info.event.classNames[0] === "bck"){
                    info.el.style.background = `green`;
                }
                else{
                    info.el.style.background = `blue`;
                    info.el.style.color = "white";
                }
            },
            eventResize: (info) => {
                let calendar: any = this.$refs.calendar.getApi();
                let currentView = calendar.view;
                calendar.changeView(currentView.type);
                axios.put('http://localhost:8000/api/jobs/' + info.event.title + '/', {
                    start: info.event.start,
                    end: info.event.end                  
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
                let calendar: any = this.$refs.calendar.getApi();
                let currentView = calendar.view;
                calendar.changeView(currentView.type);
                axios.put('http://localhost:8000/api/jobs/' + info.event.title + '/', {
                    start: info.event.start,
                    end: info.event.end                  
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
                    let calendar = this.$refs.calendar.getApi();
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
                var bck_event = {
                    "resourceId":output[i]["jobID"],
                    "title":output[i]["jobID"],
                    "start":output[i]["start"],
                    "end":output[i]["end"],
                    "eventColor":"green",
                    "className": "bck"
                };
                var temp_event = {
                    "resourceId":output[i]["jobID"],
                    "title":output[i]["resourceId"],
                    "start":output[i]["productionStart"],
                    "end":output[i]["productionEnd"],
                    "display": 'background',
                    "eventColor":"blue",
                    "className": "fwd"
                };

                if (temp_event["title"] === "SL 2")
                {
                    temp_event["title"] = "Maschine 1"
                }
                if (temp_event["title"] === "SL 4")
                {
                    temp_event["title"] = "Maschine 2"
                }
                if (temp_event["title"] === "SL 5")
                {
                    temp_event["title"] = "Maschine 3"
                }
                if (temp_event["title"] === "SL 6")
                {
                    temp_event["title"] = "Maschine 4"
                }
                if (temp_event["title"] === "SL 7")
                {
                    temp_event["title"] = "Maschine 5"
                }
                if (temp_event["title"] === "SL 8")
                {
                    temp_event["title"] = "Maschine 6"
                }
                if (temp_event["title"] === "SL 9")
                {
                    temp_event["title"] = "Maschine 7"
                }
                if (temp_event["title"] === "SL 10")
                {
                    temp_event["title"] = "Maschine 8"
                }
                if (temp_event["title"] === "SL 11")
                {
                    temp_event["title"] = "Maschine 9"
                }
                events_var.push(bck_event);
                events_var.push(temp_event);
            }

            var resources_var: { id: string; title: string }[] = [];
            for (var i = 0; i < output.length; ++i) {
                var temp_res = {
                    "id":output[i]["jobID"],
                    "title":output[i]["jobID"]
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