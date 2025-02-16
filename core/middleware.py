from datetime import timedelta, datetime
from django.utils.timezone import now
from django.conf import settings
from django.shortcuts import redirect

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')

            if last_activity:
                try:
                    # Converte a string ISO 8601 para um objeto datetime
                    last_activity = datetime.fromisoformat(last_activity)
                    
                    # Calcula o tempo decorrido
                    elapsed_time = now() - last_activity
                    
                    if elapsed_time > timedelta(seconds=settings.SESSION_COOKIE_AGE):
                        # Expira a sessão e redireciona para login
                        request.session.flush()  # Remove todos os dados da sessão
                        return redirect('login')
                except ValueError:
                    # Caso haja um erro na conversão, reinicia a sessão
                    request.session.flush()
                    return redirect('login')

            # Atualiza a última atividade com um valor serializável
            request.session['last_activity'] = now().isoformat()

        response = self.get_response(request)
        return response
