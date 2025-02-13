from django.shortcuts import render

def dashboard_view(request):
    titulo_pagina = 'Dashboard'
    context = {
        'titulo_pagina': titulo_pagina,
    }
    return render(request, 'dashboard/dashboard.html', context)
