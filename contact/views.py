from django.shortcuts import render


def contact_us(request):
    return render(request, 'contact/contact_us.html', {
        'address': '37 Willows Ave, Cardiff CF24 2SU',
        'phone': '+11223344550',
        'email': 'info@example.com',
        'opening_hours': 'Saturday - Friday: 9:00 AM - 6:00 PM',
    })
