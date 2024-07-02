document.addEventListener('DOMContentLoaded', function() {
    var dateInputs = document.querySelectorAll('.booking-date');

    dateInputs.forEach(function(dateInput) {
        dateInput.addEventListener('change', function(event) {
            handleDateChange(event);
        });

        handleDateChange({ target: dateInput });
    });
});

function handleDateChange(event) {
    var dateInput = event.target;
    var form = dateInput.closest('form');

    if (!form) {
        console.error('Form element not found');
        return;
    }

    var serviceIdInput = form.querySelector('input[name="service_id"]');
    if (!serviceIdInput) {
        console.error('Service ID input not found');
        return;
    }

    var serviceId = serviceIdInput.value;
    var timesSelect = form.querySelector('.booking-time');
    if (!timesSelect) {
        console.error('Times select element not found');
        return;
    }

    var bookingDate = dateInput.value;
    fetchAvailableAndBookedTimes(serviceId, bookingDate, timesSelect);
}

function fetchAvailableAndBookedTimes(serviceId, date, timeSelectElement) {
    var availableTimesUrl = `/cart/${serviceId}/get_available_times/?booking_date=${date}`;
    var bookedTimesUrl = `/cart/${serviceId}/get_booked_times/?booking_date=${date}`;

    fetch(availableTimesUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            fetch(bookedTimesUrl)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(bookedTimesData => {
                    var availableTimes = data.available_times;
                    var bookedTimes = bookedTimesData.booked_times;

                    var filteredTimes = availableTimes.filter(time => {
                        return !bookedTimes.some(bookedTime => bookedTime.includes(time));
                    });

                    var selectedTime = timeSelectElement.value;

                    timeSelectElement.innerHTML = '';
                    var initialOption = document.createElement('option');
                    initialOption.value = selectedTime; 
                    initialOption.textContent = selectedTime; 
                    initialOption.disabled = true;
                    initialOption.selected = true;
                    timeSelectElement.appendChild(initialOption);

                    filteredTimes.forEach(function(timeSlot) {
                        var option = document.createElement('option');
                        option.value = timeSlot;
                        option.textContent = timeSlot;
                        timeSelectElement.appendChild(option);
                    });

                    
                    timeSelectElement.value = selectedTime;  

                })
                .catch(error => {
                    console.error('Error fetching booked times:', error);
                });
        })
        .catch(error => {
            console.error('Error fetching available times:', error);
        });
}
