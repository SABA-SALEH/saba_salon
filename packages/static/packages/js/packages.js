
document.addEventListener('DOMContentLoaded', function () {
    // Add click event listener to delete links
    document.querySelectorAll('.delete-link').forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault(); // Prevent default link action
            const url = this.getAttribute('data-url'); // Get URL from data attribute
            Swal.fire({
                title: 'Are you sure?',
                text: 'You will not be able to recover this package!',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#CA8787',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Yes, delete it!',
                cancelButtonText: 'Cancel'
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.href = url; // Redirect to the delete URL
                }
            });
        });
    });
});
