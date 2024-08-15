/**
 * Fetches available and booked times for a given service and date, 
 * then updates the time selection dropdown accordingly.
 * @param {number} serviceId - The ID of the service.
 * @param {string} date - The selected booking date in YYYY-MM-DD format.
 * @param {HTMLElement} timeSelectElement - The select element to be updated with available times.
 */
function fetchAvailableAndBookedTimes(serviceId, date, timeSelectElement) {
    // URL for fetching available times
    var availableTimesUrl = `/services/${serviceId}/get_available_times/?booking_date=${date}`;
    // URL for fetching booked times
    var bookedTimesUrl = `/services/${serviceId}/get_booked_times/?booking_date=${date}`;

    // Fetch available times
    fetch(availableTimesUrl)
        .then(response => {
            if (!response.ok) {
                // Throw error if response is not ok
                throw new Error('Network response was not ok');
            }
            return response.json(); // Parse response as JSON
        })
        .then(data => {
            // Fetch booked times
            fetch(bookedTimesUrl)
                .then(response => {
                    if (!response.ok) {
                        // Throw error if response is not ok
                        throw new Error('Network response was not ok');
                    }
                    return response.json(); // Parse response as JSON
                })
                .then(bookedTimesData => {
                    // Get available and booked times from the responses
                    var availableTimes = data.available_times;
                    var bookedTimes = bookedTimesData.booked_times;

                    // Filter out booked times from available times
                    var filteredTimes = availableTimes.filter(time => {
                        return !bookedTimes.some(bookedTime => bookedTime.includes(time));
                    });

                    // Update the select element with filtered available times
                    timeSelectElement.innerHTML = '<option value="" disabled selected>Select a time</option>';

                    filteredTimes.forEach(function(timeSlot) {
                        // Create a new option element for each available time slot
                        var option = document.createElement('option');
                        option.value = timeSlot;
                        option.textContent = timeSlot;
                        // Append the option to the select element
                        timeSelectElement.appendChild(option);
                    });
                })
                .catch(error => {
                    // Log error if fetching booked times fails
                    console.error('Error fetching booked times:', error);
                });
        })
        .catch(error => {
            // Log error if fetching available times fails
            console.error('Error fetching available times:', error);
        });
}

// Event listener for changes in the main booking date
document.getElementById('booking_date').addEventListener('change', function(event) {
    // Get the selected booking date
    var bookingDate = event.target.value;
    // Get the service ID from the hidden input field
    var serviceId = document.getElementById('bookingForm').querySelector('input[name="service_id"]').value;
    // Get the time select element to be updated
    var timesSelect = document.getElementById('booking_time');
    // Fetch and update available and booked times
    fetchAvailableAndBookedTimes(serviceId, bookingDate, timesSelect);
});

// Event listener for changes in the additional booking date
document.getElementById('additional_booking_date').addEventListener('change', function(event) {
    // Get the selected booking date
    var bookingDate = event.target.value;
    // Get the selected additional service ID
    var serviceId = document.getElementById('service_select').value;
    // Get the time select element for additional booking
    var timesSelect = document.getElementById('additional_booking_time');
    // Fetch and update available and booked times
    fetchAvailableAndBookedTimes(serviceId, bookingDate, timesSelect);
});

// Event listener for changes in the additional service select
document.getElementById('service_select').addEventListener('change', function(event) {
    // Get the selected booking date
    var bookingDate = document.getElementById('additional_booking_date').value;
    if (bookingDate) {
        // Get the newly selected service ID
        var serviceId = event.target.value;
        // Get the time select element for additional booking
        var timesSelect = document.getElementById('additional_booking_time');
        // Fetch and update available and booked times
        fetchAvailableAndBookedTimes(serviceId, bookingDate, timesSelect);
    }
});

// Event listener for toggling the additional service container visibility
document.getElementById('toggleAdditionalService').addEventListener('click', function(event) {
    // Get the additional service container element
    var additionalServiceContainer = document.getElementById('additionalServiceContainer');
    if (additionalServiceContainer.style.display === 'none') {
        // Show the additional service container and change button text
        additionalServiceContainer.style.display = 'block';
        event.target.textContent = 'Cancel Adding';
    } else {
        // Hide the additional service container and change button text
        additionalServiceContainer.style.display = 'none';
        event.target.textContent = 'Add Another Service';
    }
});
