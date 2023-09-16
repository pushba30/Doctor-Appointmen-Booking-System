document.addEventListener('DOMContentLoaded', async function () {
    const form = document.getElementById('update-delete-form');
    const message = document.getElementById('message');
    const doctorDropdown = document.getElementById('doctor');
    const dateInput = document.getElementById('date');
    const from_timeInput = document.getElementById('from_time');
    const to_timeInput = document.getElementById('to_time');
    const operationInput = document.getElementById('operation');

    // Fetch available doctor names
    const doctorsResponse = await fetch('/get_available_doctors');
    const doctorsData = await doctorsResponse.json();
    doctorsData.forEach(doctor => {
        const option = document.createElement('option');
        option.value = doctor;
        option.textContent = doctor;
        doctorDropdown.appendChild(option);
    });

    //Updation
    form.addEventListener('submit', async function (event) {
        event.preventDefault();

        const doctor = doctorDropdown.value;
        const date = dateInput.value;
        const from_time = from_timeInput.value;
        const to_time = to_timeInput.value;
        const operation = operationInput.value;


        // Validate date not before current date
        const currentDate = new Date().toISOString().split('T')[0];
        if (date < currentDate) {
            message.textContent = 'Please select a date not before the current date.';
            return;
        }        

        // Check if to_time is after from_time
        if (!isTimeValid(from_time, to_time)) {
            message.textContent = 'Invalid time range. To time must be after from time.';
            return;
        }

        const response = await fetch('/update_delete_doctor', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ doctor, date, from_time, to_time, operation })
        });

        const result = await response.json();
        message.textContent = result.message;
    });

    
    // Function to check if to_time is after from_time
    function isTimeValid(from_time, to_time) {
        const fromParts = from_time.split(':');
        const toParts = to_time.split(':');

        const fromHour = parseInt(fromParts[0]);
        const fromMinute = parseInt(fromParts[1]);
        const toHour = parseInt(toParts[0]);
        const toMinute = parseInt(toParts[1]);

        if (toHour > fromHour || (toHour === fromHour && toMinute >= fromMinute)) {
            return true;
        }

        return false;
    }
});
