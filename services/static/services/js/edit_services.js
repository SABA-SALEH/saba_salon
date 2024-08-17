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