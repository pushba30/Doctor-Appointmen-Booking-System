document.addEventListener('DOMContentLoaded', async function () {
    const form = document.getElementById('appointment-form');
    const message = document.getElementById('message');
    const doctorDropdown = document.getElementById('doctor');
    const slotDropdown = document.getElementById('slot');
    const bookButton = document.getElementById('book-appointment');
    const specialistDropdown1 = document.getElementById('specialist'); // Add this line

    // Fetch available doctor names
    const doctorsResponse = await fetch('/get_available_doctors');
    const doctorsData = await doctorsResponse.json();
    doctorsData.forEach(doctor => {
        const option = document.createElement('option');
        option.value = doctor;
        option.textContent = doctor;
        doctorDropdown.appendChild(option);
    });

    // Fetch available specialists
const specialistsResponse = await fetch('/get_available_specialists');
const specialistsData = await specialistsResponse.json();
const specialistDropdown = document.getElementById('specialist');
specialistsData.forEach(specialist => {
    const option = document.createElement('option');
    option.value = specialist;
    option.textContent = specialist;
    specialistDropdown.appendChild(option);
});

specialistDropdown.addEventListener('change', async function () {
    const selectedSpecialist = specialistDropdown1.value;

    // Fetch available doctors for the selected specialist
    const doctorsResponse = await fetch('/get_available_doctors_by_specialist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ specialist: selectedSpecialist })
    });
    const doctorsData = await doctorsResponse.json();

    // Clear and populate doctor dropdown
    doctorDropdown.innerHTML = '';
    const chooseDoctorOption = document.createElement('option'); // Add this line
    chooseDoctorOption.value = '';
    chooseDoctorOption.textContent = 'Choose Doctor';
    doctorDropdown.appendChild(chooseDoctorOption);
    
    doctorsData.forEach(doctor => {
        const option = document.createElement('option');
        option.value = doctor;
        option.textContent = doctor;
        doctorDropdown.appendChild(option);
    });

    // Clear the slot dropdown
    slotDropdown.innerHTML = '';
});

    
    doctorDropdown.addEventListener('change', async function () {
        const selectedDoctor = doctorDropdown.value;
    
        // Fetch available slots for the selected doctor
        const availabilityResponse = await fetch('/get_available_slots', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ doctor: selectedDoctor })
        });
        const availabilityData = await availabilityResponse.json();
    
        slotDropdown.innerHTML = '';
    
        if (availabilityData.slots.length === 0) {
            const option = document.createElement('option');
            option.textContent = 'No slots available';
            slotDropdown.appendChild(option);
        } else {
            availabilityData.slots.forEach(slot => {
                const option = document.createElement('option');
                option.value = slot;
                option.textContent = slot;
                slotDropdown.appendChild(option);
            });
        }
    });
    bookButton.addEventListener('click', async function () {
        const doctor = doctorDropdown.value;
        const slot = slotDropdown.value;

        const response = await fetch('/check_availability', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ doctor, slot })
        });

        const result = await response.json();
        if (result.available) {
            const registerResponse = await fetch('/book_appointment', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ doctor, slot })
            });

            const registerResult = await registerResponse.json();
            if (registerResult.success) {
                message.textContent = 'Appointment registered successfully.';
                setTimeout(() => {
                    message.textContent = '';
                    form.reset();
                }, 3000); // Clear message and reset form after 3 seconds
            } else {
                message.textContent = 'Failed to register appointment.';
            }
        } else {
            message.textContent = 'Doctor is not available at the selected time.';
        }
    });
});
