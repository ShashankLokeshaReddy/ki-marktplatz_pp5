<template>
    <div>
        <FullCalendar ref="prodcalendar" :options="calendarOptions">
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
                        const confirmed = window.confirm("Would you like to save all jobs in a CSV?");
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
            // editable: true, # to ensure that it cannot be dragged to a different resource
            eventStartEditable: true,
            eventDurationEditable: true,
            resourceEditable: false,
            
            resourceAreaColumns: [
                {
                field: 'title',
                headerContent: 'Jobs'
                }
            ],

            resources: [],
            events: [] as { resourceId : string; title: string; start: Date; end: Date; eventTextColor : string;}[],
            eventDidMount: (info) => {
                let calendar: any = this.$refs.prodcalendar.getApi();
                let view_start = calendar.currentData.calendarApi.currentData.dateProfile.activeRange.start;
                let view_end = calendar.currentData.calendarApi.currentData.dateProfile.activeRange.end;
                let offset_start = view_start.getTimezoneOffset();
                let gmtTime_view_start = new Date(view_start.getTime() + offset_start * 60 * 1000);
                let offset_end = view_end.getTimezoneOffset();
                let gmtTime_view_end = new Date(view_end.getTime() + offset_end * 60 * 1000);
                var resources = info.event.getResources();
                console.log("info.event",info.event)
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
                let calendar: any = this.$refs.prodcalendar.getApi();
                let view_start = calendar.currentData.calendarApi.currentData.dateProfile.activeRange.start;
                let view_end = calendar.currentData.calendarApi.currentData.dateProfile.activeRange.end;
                let offset_start = view_start.getTimezoneOffset();
                let gmtTime_view_start = new Date(view_start.getTime() + offset_start * 60 * 1000);
                let offset_end = view_end.getTimezoneOffset();
                let gmtTime_view_end = new Date(view_end.getTime() + offset_end * 60 * 1000);

                var resources = info.event.getResources();
                var all_events = resources[0].getEvents();
                
                // Get all events with the same title, but exclude the current event
                const res = calendar.getResources();
                const all_events_in_calandar = res.flatMap(resource => resource.getEvents())
                const overlapping_events = all_events_in_calandar.filter(event => {
                    return (event.title === info.event.title && event !== info.event);
                });

                // Check for overlapping events across different resources
                const eventStart = info.event.start;
                const eventEnd = info.event.end;
                for (const overlappingEvent of overlapping_events) {
                    const resourceIds = info.event.getResources().map(resource => resource.id);
                    const overlappingResourceIds = overlappingEvent.getResources().map(resource => resource.id);
                    const resourceOverlap = resourceIds.some(id => overlappingResourceIds.includes(id));
                    if (!resourceOverlap) {
                    if (eventEnd > overlappingEvent.start && eventStart < overlappingEvent.end) {
                        // If there is an overlapping event, revert the change and show an error message
                        info.revert();
                        alert('Cannot drop event because it overlaps with another event with the same title.');
                        return;
                    }
                    }
                }

                var bck_event;
                for (let i = 0; i < all_events.length; i++) {
                    if (all_events[i].classNames[0] === "bck"){
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

                if(info.event.end > bck_event.end){
                    var numerator = bck_event.end - override_start;
                    var denominator = override_end - override_start;
                    var delta = numerator*100/denominator;
                    info.el.style.background = `linear-gradient(90deg, blue ${delta}%, red 0%)`;
                }
                else{
                    info.el.style.background = `blue`;
                }

                const jobs_data = {job: bck_event.title, final_start: info.event.start, final_end: info.event.end};
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
            },  
            eventDrop: (info) => {
                let calendar: any = this.$refs.prodcalendar.getApi();
                let view_start = calendar.currentData.calendarApi.currentData.dateProfile.activeRange.start;
                let view_end = calendar.currentData.calendarApi.currentData.dateProfile.activeRange.end;
                let offset_start = view_start.getTimezoneOffset();
                let gmtTime_view_start = new Date(view_start.getTime() + offset_start * 60 * 1000);
                let offset_end = view_end.getTimezoneOffset();
                let gmtTime_view_end = new Date(view_end.getTime() + offset_end * 60 * 1000);

                var resources = info.event.getResources();
                var all_events = resources[0].getEvents();
                
                // Get all events with the same title, but exclude the current event
                const res = calendar.getResources();
                const all_events_in_calandar = res.flatMap(resource => resource.getEvents())
                const overlapping_events = all_events_in_calandar.filter(event => {
                    return (event.title === info.event.title && event !== info.event);
                });

                // Check for overlapping events across different resources
                const eventStart = info.event.start;
                const eventEnd = info.event.end;
                for (const overlappingEvent of overlapping_events) {
                    const resourceIds = info.event.getResources().map(resource => resource.id);
                    const overlappingResourceIds = overlappingEvent.getResources().map(resource => resource.id);
                    const resourceOverlap = resourceIds.some(id => overlappingResourceIds.includes(id));
                    if (!resourceOverlap) {
                    if (eventEnd > overlappingEvent.start && eventStart < overlappingEvent.end) {
                        // If there is an overlapping event, revert the change and show an error message
                        info.revert();
                        alert('Cannot drop event because it overlaps with another event with the same title.');
                        return;
                    }
                    }
                }

                var bck_event;
                for (let i = 0; i < all_events.length; i++) {
                    if (all_events[i].classNames[0] === "bck"){
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

                if(info.event.end > bck_event.end){
                    var numerator = bck_event.end - override_start;
                    var denominator = override_end - override_start;
                    var delta = numerator*100/denominator;
                    info.el.style.background = `linear-gradient(90deg, blue ${delta}%, red 0%)`;
                }
                else{
                    info.el.style.background = `blue`;
                }

                const jobs_data = {job: bck_event.title, final_start: info.event.start, final_end: info.event.end};
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
            },       
            mounted() {
                this.$nextTick(() => {
                    let calendar = this.$refs.prodcalendar.getApi();
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
            var output : { selected_machine: string; job: string; item: string; start: Date, end: Date, final_start: Date, final_end: Date }[] = [];
            output = output_resp["Table"]
            
            var events_var = []
            for (var i = 0; i < output.length; ++i) {
                if(output[i]["final_end"]===null){
                    output[i]["final_end"] = output[i]["end"]
                }
                var bck_event = {
                    "resourceId":output[i]["job"],
                    "title":output[i]["job"],
                    "start":output[i]["start"],
                    "end":output[i]["end"],
                    "eventColor":"green",
                    "display":'background',
                    "className": "bck"
                };
                var temp_event = {
                    "resourceId":output[i]["job"],
                    "title":output[i]["selected_machine"],
                    "start":output[i]["final_start"],
                    "end":output[i]["final_end"],
                    "eventColor":"blue",
                    "display":'auto',
                    "className": "fwd"
                };

                events_var.push(bck_event);
                events_var.push(temp_event);
            }

            var resources_var: { id: string; title: string }[] = [];
            for (var i = 0; i < output.length; ++i) {
                var temp_res = {
                    "id":output[i]["job"],
                    "title":output[i]["job"]
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