function confirmDelete(reviewId) {
    // Get the delete URL from the button's data attribute
    const deleteUrl = document.querySelector(`[data-delete-url]`).getAttribute('data-delete-url');
    
    Swal.fire({
        title: 'Are you sure?',
        text: "Do you want to delete this review? This action cannot be undone.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Yes, delete it!'
    }).then((result) => {
        if (result.isConfirmed) {
            // Submit the form to delete the review
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = deleteUrl;
            const csrfToken = document.createElement('input');
            csrfToken.type = 'hidden';
            csrfToken.name = 'csrfmiddlewaretoken';
            csrfToken.value = document.querySelector('[name=csrfmiddlewaretoken]').value;
            form.appendChild(csrfToken);
            const reviewIdInput = document.createElement('input');
            reviewIdInput.type = 'hidden';
            reviewIdInput.name = 'review_id';
            reviewIdInput.value = reviewId;
            form.appendChild(reviewIdInput);
            const deleteInput = document.createElement('input');
            deleteInput.type = 'hidden';
            deleteInput.name = 'delete_review';
            deleteInput.value = 'true';
            form.appendChild(deleteInput);
            document.body.appendChild(form);
            form.submit();
        }
    });
}
