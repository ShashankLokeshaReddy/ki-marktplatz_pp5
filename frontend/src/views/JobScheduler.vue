<template>
    <div>
        <FullCalendar :options="calendarOptions">
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

// output should come from the backend, and below lines should move to the place where backend call occurs
// var output = [{
//         "resourceId": "SL 2",
//         "jobId": "12403",
//         "start": new Date("2023-01-03T11:54:52Z"), // time in UTC, UTC + 1 hr = local time
//         "end": new Date("2023-01-04T14:10:06Z"),
//         "production_start": new Date("2023-01-02T14:10:06Z"),
//         "production_end": new Date("2023-01-06T14:10:06Z")
//             },
//             {
//         "resourceId": "SL 4",
//         "jobId": "12404",
//         "start": new Date("2023-01-03T11:00:52Z"),
//         "end": new Date("2023-01-04T22:00:06Z"),
//         "production_start": new Date("2023-01-02T14:10:00Z"),
//         "production_end": new Date("2023-01-03T11:42:06Z")
//             }]

// var events_var: { resourceId: string; title: string; start: Date; end: Date }[] = [];

// for (var i = 0; i < output.length; ++i) {
//     var prod_event = {
//         "resourceId":output[i]["jobId"],
//         "title":output[i]["jobId"],
//         "start":output[i]["production_start"],
//         "end":output[i]["production_end"],
//         "display": 'background',
//         "className": "bck"
//     };
//     var temp_event = {
//         "resourceId":output[i]["jobId"],
//         "title":output[i]["resourceId"],
//         "start":output[i]["start"],
//         "end":output[i]["end"],
//         "background":"blue"
//     };
    
//     if(output[i]["end"] > output[i]["production_end"])
//     {
//         var numerator = output[i]["production_end"] - output[i]["start"];
//         var denominator = output[i]["end"] - output[i]["start"];
//         var delta = numerator*100/denominator;
//         //temp_event["delay"] = 30;
//         //temp_event["eventContent"] = `{ html: '<hr style="width:50%">' }`;
//         temp_event["background"] = `linear-gradient(90deg, blue ${delta}%, red 0%)`;
//     }
//     if (temp_event["title"] === "SL 2")
//     {
//         temp_event["title"] = "Maschine 1"
//     }
//     if (temp_event["title"] === "SL 4")
//     {
//         temp_event["title"] = "Maschine 2"
//     }
//     if (temp_event["title"] === "SL 5")
//     {
//         temp_event["title"] = "Maschine 3"
//     }
//     if (temp_event["title"] === "SL 6")
//     {
//         temp_event["title"] = "Maschine 4"
//     }
//     if (temp_event["title"] === "SL 7")
//     {
//         temp_event["title"] = "Maschine 5"
//     }
//     if (temp_event["title"] === "SL 8")
//     {
//         temp_event["title"] = "Maschine 6"
//     }
//     if (temp_event["title"] === "SL 9")
//     {
//         temp_event["title"] = "Maschine 7"
//     }
//     if (temp_event["title"] === "SL 10")
//     {
//         temp_event["title"] = "Maschine 8"
//     }
//     if (temp_event["title"] === "SL 11")
//     {
//         temp_event["title"] = "Maschine 9"
//     }
//     events_var.push(prod_event);
//     events_var.push(temp_event);
// }

// var resources_var: { id: string; title: string }[] = [];
// for (var i = 0; i < output.length; ++i) {
//     var temp_res = {
//         "id":output[i]["jobId"],
//         "title":output[i]["jobId"]
//     };
//     resources_var.push(temp_res);
// }

export default defineComponent({
     
    //props: [FullCalendar],
    components: {FullCalendar},
    data()  {
        return {
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
            events: [] as { resourceId : string; title: string; start: Date; end: Date; }[],
            eventDidMount: function (info) {
                    // info.el.style.background = info.event.extendedProps.background;
                    var resources = info.event.getResources();
                    var all_events = resources[0].getEvents()
                    var bck_event
                    for (let i = 0; i < all_events.length; i++) {
                        if (all_events[i].classNames[0] === "bck"){ //info.event.title
                            bck_event = all_events[i]
                        }
                    }
                    if(info.event.end > bck_event.end){
                        var numerator = bck_event.end - info.event.start;
                        var denominator = info.event.end - info.event.start;
                        var delta = numerator*100/denominator;
                        info.el.style.background = `linear-gradient(90deg, blue ${delta}%, red 0%)`;
                    }
                    else if(info.event.classNames[0] === "bck"){
                        info.el.style.background = `green`;
                    }
                    else{
                        info.el.style.background = `blue`;
                    }
            },
            eventResize: function(info) {
                var resources = info.event.getResources();
                //var resourceIds = resources.map(function(resource) { return resource.id });
                var all_events = resources[0].getEvents()
                var bck_event
                for (let i = 0; i < all_events.length; i++) {
                    if (all_events[i].classNames[0] === "bck"){ //info.event.title
                        bck_event = all_events[i]
                    }
                }
                if(info.event.end > bck_event.end){
                    var numerator = bck_event.end - info.event.start;
                    var denominator = info.event.end - info.event.start;
                    var delta = numerator*100/denominator;
                    info.el.style.background = `linear-gradient(90deg, blue ${delta}%, red 0%)`;
                }
                else{
                    info.el.style.background = `blue`;
                }

                axios.put('http://localhost:8000/api/jobs/' + bck_event.title + '/', {
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
            eventDrop: function(info) {
                var resources = info.event.getResources();
                var all_events = resources[0].getEvents()
                var bck_event
                for (let i = 0; i < all_events.length; i++) {
                    if (all_events[i].classNames[0] === "bck"){
                        bck_event = all_events[i]
                    }
                }
                if(info.event.end > bck_event.end){
                    var numerator = bck_event.end - info.event.start;
                    var denominator = info.event.end - info.event.start;
                    var delta = numerator*100/denominator;
                    info.el.style.background = `linear-gradient(90deg, blue ${delta}%, red 0%)`;
                }
                else{
                    info.el.style.background = `blue`;
                }

                axios.put('http://localhost:8000/api/jobs/' + bck_event.title + '/', {
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
            }                     
            
            },
        }
    },

   async created(){
            var response = await fetch('http://localhost:8000/api/jobs/')
            var output : { resourceId: string; jobID: string; partID: string; start: Date, end: Date, productionStart: Date, productionEnd: Date }[] = [];
            output = await response.json()
            
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
                    "display": 'background',
                    "eventColor":"green",
                    "className": "bck"
                };
                var temp_event = {
                    "resourceId":output[i]["jobID"],
                    "title":output[i]["resourceId"],
                    "start":output[i]["productionStart"],
                    "end":output[i]["productionEnd"],
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
/* .grad{
  background: linear-gradient(
    to right,
    blue 0%,
    blue 50%,
    red 50%,
    red 100%
  );
} */
</style>