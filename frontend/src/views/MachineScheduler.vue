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

function convertToMilliseconds(duration) {
  let [days, time] = duration.split(", ");
  let [hours, minutes, seconds] = time.split(":").map(Number);
  let totalMilliseconds = days * 24 * 60 * 60 * 1000 + hours * 60 * 60 * 1000 + minutes * 60 * 1000 + seconds * 1000;
  return totalMilliseconds;
}

function convertMillisecondsToDuration(milliseconds) {
  const seconds = Math.floor((milliseconds / 1000) % 60);
  const minutes = Math.floor((milliseconds / (1000 * 60)) % 60);
  const hours = Math.floor((milliseconds / (1000 * 60 * 60)) % 24);
  const days = Math.floor(milliseconds / (1000 * 60 * 60 * 24));
  const formattedHours = hours.toString().padStart(2, '0');
  const formattedMinutes = minutes.toString().padStart(2, '0');
  const formattedSeconds = seconds.toString().padStart(2, '0');
  let formattedDuration = '';
  if (days > 0) {
    formattedDuration += `${days} day${days > 1 ? 's' : ''}, `;
  }
  formattedDuration += `${formattedHours}:${formattedMinutes}:${formattedSeconds}`;
  return formattedDuration;
}

function get_EventorDBDuration(info, totalMilliseconds, resize) {
    const start = new Date(info.event.start);
    const end = new Date(info.event.end);
    const startHour = Math.max(start.getHours(), 7);
    const endHour = Math.min(end.getHours(), 23);
    let duration = 0;
    let event_duration = 0;
    let currentDate = new Date(start);
    let duration_flag = true;
    while (duration_flag) {
        const dayOfWeek = currentDate.getDay();
        const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
        const isHoliday = holidays.includes(currentDate.toISOString().substring(0, 10));
        const isOperationalHour = !isWeekend && !isHoliday && currentDate.getHours() >= 7 && currentDate.getHours() <= 23;
        event_duration += 1000;
        if (isOperationalHour) {
            duration += 1000; // add 1 sec in milliseconds
        }
        if (totalMilliseconds._milliseconds <= duration)
        {
            duration_flag = false;
        }
        currentDate.setTime(currentDate.getTime() + 1000); // add 1 sec
    }
    console.log(totalMilliseconds._milliseconds);
    console.log("duration..",duration);
    console.log(event_duration);
    if resize{
        return duration;
    }
    else{
        return event_duration;
    }
}

function get_ValidDuration(info) {
  const start = new Date(info.event.start);
  const end = new Date(info.event.end);
  const startHour = Math.max(start.getHours(), 7);
  const endHour = Math.min(end.getHours(), 23);
  let validDuration = 0;
  let currentDate = new Date(start);
  while (currentDate < end) {
    const dayOfWeek = currentDate.getDay();
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
    const isHoliday = holidays.includes(currentDate.toISOString().substring(0, 10));
    const isOperationalHour = !isWeekend && !isHoliday && currentDate.getHours() >= 7 && currentDate.getHours() <= 23;
    if (isOperationalHour) {
      validDuration += 60 * 1000; // add 1 min in milliseconds
    }
    currentDate.setTime(currentDate.getTime() + 60 * 1000); // add 1 min
  }
  return validDuration;
}

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
            resourceAreaWidth: "10%",
            scrollTimeReset: false,
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
                const formattedDate = date.toISOString().substring(0, 10);
                if (holidays.includes(formattedDate)) {
                    classNames.push("weekend-non-operating-hours");
                } else if ( ([0, 6].includes(date.getDay())) ) {
                    classNames.push("weekend-non-operating-hours");
                } else if ( ! (hour < startHour || hour >= endHour) && ![0, 6].includes(date.getDay()) ) {
                    classNames.push("operating-hours");
                } else {
                    classNames.push("non-operating-hours");
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
                const formattedDate = date.toISOString().substring(0, 10);
                if (holidays.includes(formattedDate)) {
                    classNames.push("weekend-non-operating-hours");
                } else if ( ([0, 6].includes(date.getDay())) ) {
                    classNames.push("weekend-non-operating-hours");
                } else if ( ! (hour < startHour || hour >= endHour) && ![0, 6].includes(date.getDay()) ) {
                    classNames.push("operating-hours");
                } else {
                    classNames.push("non-operating-hours");
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
                headerContent: 'Maschinen'
                }
            ],

            resourceGroupField: 'resourcegroup',
            resources: [],
            eventConstraint: {
                start: '07:00', // opening time
                end: '23:00', // closing time
            },
            events: [] as { resourceId : string; title: string; start: Date; end: Date; eventTextColor : string;}[],
            eventDidMount: (info) => {
                info.el.style.background = `purple`;
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
                    // Calculate the duration between the original start and end times
                    const origStart = moment(info.event.start);
                    const origEnd = moment(info.event.end);
                    const duration = info.event.extendedProps.duration_machine
                    console.log("duration", duration)
                    var days = 0
                    var time = 0
                    if (duration.includes("days")){
                        days = parseInt(duration.split(" ")[0]);
                        time = duration.split(", ")[1];
                    }
                    else{
                        time = duration;
                    }
                    const hours = parseInt(time.split(":")[0]);
                    const minutes = parseInt(time.split(":")[1]);
                    const seconds = parseInt(time.split(":")[2]);
                    const millisecondsPerDay = 24 * 60 * 60 * 1000;
                    const millisecondsPerHour = 60 * 60 * 1000;
                    const millisecondsPerMinute = 60 * 1000;
                    const millisecondsPerSecond = 1000;
                    const totalMilliseconds = moment.duration(days * millisecondsPerDay + hours * millisecondsPerHour + minutes * millisecondsPerMinute + seconds * millisecondsPerSecond);
                    console.log("totalMilliseconds", moment.duration(origEnd.diff(origStart)), totalMilliseconds)
                    // const duration = moment.duration(origEnd.diff(origStart));

                    // Calculate the new start and end times
                    // let newStart = moment(info.event.start);
                    
                    let valid_duration = get_ValidDuration(info);
                    console.log("valid_duration",valid_duration);
                    const valid_duration_s = convertMillisecondsToDuration(valid_duration);
                    info.event.setExtendedProp('duration_machine', valid_duration_s);
                    const start_s = new Date(info.event.start);
                    const startISOString = start_s.toISOString().substring(0, 19) + "Z";
                    const end_s = new Date(info.event.end);
                    const endISOString = end_s.toISOString().substring(0, 19) + "Z";
                    console.log(convertMillisecondsToDuration(34260000)); // Output: "0:57:06"
                    
                    console.log("valid_duration_s", valid_duration_s);

                    const jobs_data = {
                    job: info.event.title,
                    final_start: startISOString,
                    final_end: endISOString,
                    selected_machine: selectedMachine,
                    duration_machine: valid_duration_s
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
                    alert('Das Ereignis kann nicht gelöscht werden, da es Einschränkungen für die Ausführung auf folgenden Computern hat: ' + info.event.extendedProps.machines);
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
                // Calculate the duration between the original start and end times
                const origStart = moment(info.event.start);
                const origEnd = moment(info.event.end);
                const duration = info.event.extendedProps.duration_machine
                console.log("duration", duration)
                var days = 0
                var time = 0
                if (duration.includes("days")){
                    days = parseInt(duration.split(" ")[0]);
                    time = duration.split(", ")[1];
                }
                else{
                    time = duration;
                }
                const hours = parseInt(time.split(":")[0]);
                const minutes = parseInt(time.split(":")[1]);
                const seconds = parseInt(time.split(":")[2]);
                const millisecondsPerDay = 24 * 60 * 60 * 1000;
                const millisecondsPerHour = 60 * 60 * 1000;
                const millisecondsPerMinute = 60 * 1000;
                const millisecondsPerSecond = 1000;
                const totalMilliseconds = moment.duration(days * millisecondsPerDay + hours * millisecondsPerHour + minutes * millisecondsPerMinute + seconds * millisecondsPerSecond);
                console.log("totalMilliseconds", moment.duration(origEnd.diff(origStart)), totalMilliseconds)
                // const duration = moment.duration(origEnd.diff(origStart));

                // Calculate the new start and end times
                // let newStart = moment(info.event.start);
                
                let event_duration = get_EventorDBDuration(info, totalMilliseconds, false);
                console.log("event_duration", event_duration);
                let newEnd = moment(info.event.start).add(moment.duration(event_duration));

                // Set the new start and end times
                // info.event.setStart(newStart.toISOString());
                info.event.setEnd(newEnd.toISOString());
                console.log("fghg",info.event.start,info.event.end)
                const start_s = new Date(info.event.start);
                const startISOString = start_s.toISOString().substring(0, 19) + "Z";
                const end_s = new Date(info.event.end);
                const endISOString = end_s.toISOString().substring(0, 19) + "Z";
                const jobs_data = {
                job: info.event.title,
                final_start: startISOString,
                final_end: endISOString,
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
                alert('Das Ereignis kann nicht gelöscht werden, da es Einschränkungen für die Ausführung auf folgenden Computern hat: ' + info.event.extendedProps.machines);
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
                "eventColor":"purple",
                "display":'auto',
                "className": "fwd",
                "extendedProps": {
                    "machines": output[i]["machines"],
                    "duration_machine": output[i]["duration_machine"]
                }
            };
            events_var.push(temp_event);
        }

        var resources_var: { id: string; title: string }[] = [];
        
        for (var i = 0; i < output.length; ++i) {
            var resourcegroup = null;
            if (output[i]["selected_machine"] == "1535" || output[i]["selected_machine"] == "1536" || output[i]["selected_machine"] == "1537"){
                resourcegroup = "Gruppe 1";
            }
            if (output[i]["selected_machine"] == "1532" || output[i]["selected_machine"] == "1533" || output[i]["selected_machine"] == "1534"){
                resourcegroup = "Gruppe 2";
            }
            if (output[i]["selected_machine"] == "1531" || output[i]["selected_machine"] == "1541" || output[i]["selected_machine"] == "1542" || output[i]["selected_machine"] == "1543"){
                resourcegroup = "Gruppe 3";
            }
            var temp_res = {
                "id":output[i]["selected_machine"],
                "resourcegroup":resourcegroup,
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
  background-color: #FFFFE0;
}
.slot-label.non-operating-hours {
  background-color: #FFFF00;
}
.slot-label.weekend-non-operating-hours {
  background-color: #FFA700;
  color: #FFFFFF;
}
.date-label {
  font-weight: bold;
  text-align: center;
}
</style>