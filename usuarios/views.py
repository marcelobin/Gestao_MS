from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .forms import UserForm, OperadorForm
from .models import Operador

def login_view(request):
    """Autentica o usuário e redireciona para a home."""
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')  # Redireciona para a home ou dashboard
        else:
            messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'login.html')


@login_required
def lista_usuarios(request):
    """Lista todos os usuários cadastrados."""
    operadores = Operador.objects.select_related('user')
    contexto = {
        'operadores': operadores,
        'titulo_pagina': 'Lista de Usuários'  # Adicionando o título ao contexto
    }
    return render(request, 'usuarios/lista_usuarios.html', contexto)




@login_required
def criar_usuario(request):
    """Cria um novo usuário e operador associado."""
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        operador_form = OperadorForm(request.POST)

        if user_form.is_valid() and operador_form.is_valid():
            user = user_form.save()  # Salva o User
            operador = operador_form.save(commit=False)
            operador.user = user  # Associa o Operador ao User
            operador.save()  # Salva o Operador
            messages.success(request, 'Usuário e operador criados com sucesso!')
            return redirect('usuarios:lista_usuarios')

        messages.error(request, 'Erro ao criar usuário. Verifique os campos.')
    else:
        user_form = UserForm()
        operador_form = OperadorForm()

    contexto = {
        'user_form': user_form,
        'operador_form': operador_form,
        'titulo_pagina': 'Criar Novo Usuário'  # Adicionando o título ao contexto
    }

    return render(request, 'usuarios/usuario_form.html', contexto)



@login_required
def editar_usuario(request, pk):
    """Edita um usuário e operador existente."""
    operador = get_object_or_404(Operador, pk=pk)
    user = operador.user

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        operador_form = OperadorForm(request.POST, instance=operador)

        if user_form.is_valid() and operador_form.is_valid():
            user = user_form.save(commit=False)
            password = user_form.cleaned_data.get('password')

            if password:  # Se o usuário informou uma nova senha, criptografa antes de salvar
                user.set_password(password)
            else:
                # Mantém a senha antiga se nenhum novo valor foi inserido
                user.password = User.objects.get(pk=user.pk).password

            user.save()
            operador_form.save()

            messages.success(request, 'Usuário e operador atualizados com sucesso!')
            return redirect('usuarios:lista_usuarios')

        else:
            messages.error(request, 'Erro ao editar usuário. Verifique os campos.')
            return render(request, 'usuarios/usuario_form.html', {
                'user_form': user_form,
                'operador_form': operador_form
            })
    else:
        user_form = UserForm(instance=user)
        operador_form = OperadorForm(instance=operador)
        
    contexto = {
        'user_form': user_form,
        'operador_form': operador_form,
        'titulo_pagina': 'Editar Usuário'  # Adicionando o título ao contexto
    }
    
    return render(request, 'usuarios/usuario_form.html', contexto)


@login_required
def excluir_usuario(request, pk):
    """Exclui um usuário e operador associado."""
    operador = get_object_or_404(Operador, pk=pk)
    user = operador.user

    if request.method == 'POST':
        user.delete()  # Exclui o User, o Operador será excluído automaticamente (CASCADE)
        messages.success(request, 'Usuário e operador excluídos com sucesso!')
        return redirect('usuarios:lista_usuarios')

    return render(request, 'usuarios/confirmar_exclusao.html', {'operador': operador})
