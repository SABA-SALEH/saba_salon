// When the document has fully loaded, execute the following function
document.addEventListener('DOMContentLoaded', function() {
    // Select all input elements with the class 'booking-date'
    var dateInputs = document.querySelectorAll('.booking-date');

    // For each date input element, add an event listener for the 'change' event
    dateInputs.forEach(function(dateInput) {
        dateInput.addEventListener('change', function(event) {
            handleDateChange(event);  // Call the function to handle changes in the date input
        });

        // Simulate a change event to initialize the available times when the page loads
        handleDateChange({ target: dateInput });
    });
});

// Function to handle changes in the date input fields
function handleDateChange(event) {
    var dateInput = event.target;  // Get the date input element that triggered the event
    var form = dateInput.closest('form');  // Find the closest form element that contains the date input

    // Check if the form element was found
    if (!form) {
        console.error('Form element not found');  // Log an error if the form is missing
        return;
    }

    // Find the input element for the service ID within the form
    var serviceIdInput = form.querySelector('input[name="service_id"]');
    if (!serviceIdInput) {
        console.error('Service ID input not found');  // Log an error if the service ID input is missing
        return;
    }

    var serviceId = serviceIdInput.value;  // Get the value of the service ID input
    // Find the select element for booking times within the form
    var timesSelect = form.querySelector('.booking-time');
    if (!timesSelect) {
        console.error('Times select element not found');  // Log an error if the times select element is missing
        return;
    }

    var bookingDate = dateInput.value;  // Get the selected date value from the date input
    // Fetch available and booked times based on the selected date
    fetchAvailableAndBookedTimes(serviceId, bookingDate, timesSelect);
}

// Function to fetch available and booked times from the server and update the times select element
function fetchAvailableAndBookedTimes(serviceId, date, timeSelectElement) {
    // Construct URLs to fetch available and booked times from the server
    var availableTimesUrl = `/cart/${serviceId}/get_available_times/?booking_date=${date}`;
    var bookedTimesUrl = `/cart/${serviceId}/get_booked_times/?booking_date=${date}`;

    // Fetch available times from the server
    fetch(availableTimesUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');  // Handle network errors
            }
            return response.json();  // Parse the JSON response
        })
        .then(data => {
            // Fetch booked times after fetching available times
            fetch(bookedTimesUrl)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');  // Handle network errors
                    }
                    return response.json();  // Parse the JSON response
                })
                .then(bookedTimesData => {
                    var availableTimes = data.available_times;  // Extract available times from the response data
                    var bookedTimes = bookedTimesData.booked_times;  // Extract booked times from the response data

                    // Filter out times that are already booked
                    var filteredTimes = availableTimes.filter(time => {
                        return !bookedTimes.some(bookedTime => bookedTime.includes(time));
                    });

                    var selectedTime = timeSelectElement.value;  // Store the currently selected time

                    // Clear the existing options in the times select element
                    timeSelectElement.innerHTML = '';
                    // Create and add an option for the previously selected time
                    var initialOption = document.createElement('option');
                    initialOption.value = selectedTime; 
                    initialOption.textContent = selectedTime; 
                    initialOption.disabled = true;
                    initialOption.selected = true;
                    timeSelectElement.appendChild(initialOption);

                    // Add available times as new options in the times select element
                    filteredTimes.forEach(function(timeSlot) {
                        var option = document.createElement('option');
                        option.value = timeSlot;
                        option.textContent = timeSlot;
                        timeSelectElement.appendChild(option);
                    });

                    // Re-select the previously selected time
                    timeSelectElement.value = selectedTime;  

                })
                .catch(error => {
                    console.error('Error fetching booked times:', error);  // Log any errors that occur during fetching booked times
                });
        })
        .catch(error => {
            console.error('Error fetching available times:', error);  // Log any errors that occur during fetching available times
        });
}
