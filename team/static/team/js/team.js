document.addEventListener('DOMContentLoaded', function () {
    // Add event listeners to all delete forms
    document.querySelectorAll('.delete-form').forEach(form => {
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            const form = this;
            // Show confirmation dialog before deleting
            Swal.fire({
                title: 'Are you sure?',
                text: 'You won’t be able to revert this!',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#CA8787',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Yes, delete it!',
                cancelButtonText: 'Cancel'
            }).then((result) => {
                if (result.isConfirmed) {
                    form.submit();
                }
            });
        });
    });
});


$(document).ready(function () {
    console.log('jQuery is ready');
    // Event handler for file input change
    $('#new-image').change(function () {
        var file = this.files[0];
        if (file) {
            // Display the name of the chosen file
            $('#filename').text(`Image will be set to: ${file.name}`);
        } else {
            // Notify user if no file is chosen
            $('#filename').text('No file chosen');
        }
    });
});
