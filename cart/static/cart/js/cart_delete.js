document.addEventListener('DOMContentLoaded', function () {
    // Add click event listeners to remove links for confirming the removal action
    document.querySelectorAll('.remove-link').forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            const url = this.getAttribute('data-url');
            Swal.fire({
                title: 'Are you sure?',
                text: 'You won’t be able to revert this!',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#CA8787',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Yes, remove it!',
                cancelButtonText: 'Cancel'
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.href = url;
                }
            });
        });
    });
});
