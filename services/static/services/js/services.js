function fetchAvailableAndBookedTimes(serviceId, date, timeSelectElement) {
    var availableTimesUrl = `/services/${serviceId}/get_available_times/?booking_date=${date}`;
    var bookedTimesUrl = `/services/${serviceId}/get_booked_times/?booking_date=${date}`;

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

                    timeSelectElement.innerHTML = '<option value="" disabled selected>Select a time</option>';

                    filteredTimes.forEach(function(timeSlot) {
                        var option = document.createElement('option');
                        option.value = timeSlot;
                        option.textContent = timeSlot;
                        timeSelectElement.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error('Error fetching booked times:', error);
                });
        })
        .catch(error => {
            console.error('Error fetching available times:', error);
        });
}

document.getElementById('booking_date').addEventListener('change', function(event) {
    var bookingDate = event.target.value;
    var serviceId = document.getElementById('bookingForm').querySelector('input[name="service_id"]').value;
    var timesSelect = document.getElementById('booking_time');
    fetchAvailableAndBookedTimes(serviceId, bookingDate, timesSelect);
});

document.getElementById('additional_booking_date').addEventListener('change', function(event) {
    var bookingDate = event.target.value;
    var serviceId = document.getElementById('service_select').value;
    var timesSelect = document.getElementById('additional_booking_time');
    fetchAvailableAndBookedTimes(serviceId, bookingDate, timesSelect);
});

document.getElementById('service_select').addEventListener('change', function(event) {
    var bookingDate = document.getElementById('additional_booking_date').value;
    if (bookingDate) {
        var serviceId = event.target.value;
        var timesSelect = document.getElementById('additional_booking_time');
        fetchAvailableAndBookedTimes(serviceId, bookingDate, timesSelect);
    }
});
    document.getElementById('toggleAdditionalService').addEventListener('click', function(event) {
        var additionalServiceContainer = document.getElementById('additionalServiceContainer');
        if (additionalServiceContainer.style.display === 'none') {
            additionalServiceContainer.style.display = 'block';
            event.target.textContent = 'Cancel Adding';
        } else {
            additionalServiceContainer.style.display = 'none';
            event.target.textContent = 'Add Another Service';
        }
});
