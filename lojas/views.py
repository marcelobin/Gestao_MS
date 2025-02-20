#lojas/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from .models import Loja, Socio, Vendedor, DadosBancarios, LojaAnexo
from usuarios.models import Operador, Filial, Perfil
from .forms import (
    LojaForm,
    SocioLojaFormSet,
    VendedorLojaFormSet,
    DadosBancariosFormSet,
    LojaFinanceiraAcessoFormSet,
    LojaAnexoFormSet,
    LojaFormPreCadastro
)
from django.http import JsonResponse
from django.conf import settings
import json
import os
import zipfile
from django.core.files.storage import default_storage
from io import BytesIO
from django.http import HttpResponse
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt


# View para listar lojas
def listar_lojas(request):
    if request.user.is_superuser or (hasattr(request.user, "operador") and request.user.operador.perfil.ds_perfil == Perfil.ADMINISTRADOR):
        # Administrador vê todas as lojas
        lojas = Loja.objects.all()
    elif hasattr(request.user, "operador") and request.user.operador.perfil.ds_perfil == Perfil.OPERADOR:
        # Operador vê apenas as lojas vinculadas a ele
        lojas = Loja.objects.filter(operador=request.user.operador)
    else:
        # Se o usuário não for um operador válido, não vê nenhuma loja
        lojas = Loja.objects.none()


    # Aplicando filtros
    filtro_nome_fantasia = request.GET.get('nome_fantasia')
    filtro_razao_social = request.GET.get('razao_social')
    filtro_filial = request.GET.get('filial')
    filtro_operador = request.GET.get('operador')

    if filtro_nome_fantasia:
        lojas = lojas.filter(nm_fantasia__icontains=filtro_nome_fantasia)
    if filtro_razao_social:
        lojas = lojas.filter(razao_social__icontains=filtro_razao_social)
    if filtro_filial:
        lojas = lojas.filter(filial_id=filtro_filial)  # Filtrando pelo ID da filial
    if filtro_operador:
        lojas = lojas.filter(operador_id=filtro_operador)

    operadores = Operador.objects.all()
    filiais = Filial.objects.all()  # Obtém todas as filiais


    context = {
        'lojas': lojas,
        'operadores': operadores,
        'filiais': filiais,  # Passa as filiais para o contexto
        'titulo_pagina': 'Lojas Cadastradas',
        
    }
    return render(request, 'lojas/listar_lojas.html', context)


# View para criar ou editar loja
def criar_editar_loja(request, loja_id=None):
    loja = get_object_or_404(Loja, pk=loja_id) if loja_id else None
    
    # Carregar o JSON de bancos
    bancos_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'banco_codigo.json')
    with open(bancos_path, 'r') as file:
        bancos_data = json.load(file)

    if request.method == 'POST':
        form = LojaForm(request.POST, instance=loja)
        socio_formset = SocioLojaFormSet(request.POST, instance=loja, prefix='socios')
        vendedor_formset = VendedorLojaFormSet(request.POST, instance=loja, prefix='vendedores')
        dadosbancarios_formset = DadosBancariosFormSet(request.POST, instance=loja, prefix='dadosbancarios')
        acesso_formset = LojaFinanceiraAcessoFormSet(request.POST, instance=loja, prefix='acessos_financeiras')
        anexo_formset = LojaAnexoFormSet(request.POST, request.FILES, instance=None, prefix='anexos')
        

        if form.is_valid() and socio_formset.is_valid() and vendedor_formset.is_valid() and dadosbancarios_formset.is_valid() and acesso_formset.is_valid() and anexo_formset.is_valid():
            loja = form.save()
            socio_formset.instance = loja
            socio_formset.save()
            vendedor_formset.instance = loja
            vendedor_formset.save()
            dadosbancarios_formset.instance = loja
            dadosbancarios_formset.save()
            acesso_formset.instance = loja
            acesso_formset.save()
            anexo_formset.instance = loja
            anexo_formset.save()
            
            return redirect('lojas:listar_lojas')
    else:
        form = LojaForm(instance=loja)
        socio_formset = SocioLojaFormSet(instance=loja, prefix='socios')
        vendedor_formset = VendedorLojaFormSet(instance=loja, prefix='vendedores')
        dadosbancarios_formset = DadosBancariosFormSet(instance=loja, prefix='dadosbancarios')
        acesso_formset = LojaFinanceiraAcessoFormSet(instance=loja, prefix='acessos_financeiras')
        anexo_formset = LojaAnexoFormSet(instance=loja, prefix='anexos')


    return render(request, 'lojas/criar_editar_loja.html', {
        'form': form,
        'socio_formset': socio_formset,
        'vendedor_formset': vendedor_formset,
        'dadosbancarios_formset': dadosbancarios_formset,
        'acesso_formset': acesso_formset,
        'anexo_formset': anexo_formset,
        'bancos_data': bancos_data,  # Passar o JSON ao template
        
    })


# View para deletar loja
def deletar_loja(request, loja_id):
    loja = get_object_or_404(Loja, pk=loja_id)
    if request.method == 'POST':
        loja.delete()
        return redirect('lojas:listar_lojas')  # Agora com namespace correto
    return render(request, 'lojas/deletar_loja.html', {'loja': loja})

# View para visualizar os detalhes de uma loja

def loja_detail(request, loja_id):
    loja = get_object_or_404(Loja, pk=loja_id)
    socios = loja.socios.all()
    vendedores = loja.vendedores.all()
    dadosbancarios = loja.dadosbancarios.all()
    acessos = loja.acessos_financeiras.all()
    anexos = loja.anexos.all()  # Obtendo os anexos da loja

    return render(request, 'lojas/loja_detail.html', {
        'loja': loja,
        'socios': socios,
        'vendedores': vendedores,
        'dadosbancarios': dadosbancarios,
        'acessos': acessos,
        'anexos': anexos,
    })
    
def buscar_bancos(request):
    """
    Retorna a lista de bancos em JSON.
    """
    caminho_arquivo = os.path.join(settings.STATIC_ROOT, 'data/banco_codigo.json')
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    
def pre_cadastro_loja(request):
    if request.method == "POST":
        form = LojaFormPreCadastro(request.POST, request.FILES)
        socio_formset = SocioLojaFormSet(request.POST, request.FILES, instance=None, prefix='socios')
        vendedor_formset = VendedorLojaFormSet(request.POST, request.FILES, instance=None, prefix='vendedores')
        dadosbancarios_formset = DadosBancariosFormSet(request.POST, request.FILES, instance=None, prefix='dadosbancarios')
        anexo_formset = LojaAnexoFormSet(request.POST, request.FILES, instance=None, prefix='anexos')
        
        if form.is_valid() and socio_formset.is_valid() and vendedor_formset.is_valid() and dadosbancarios_formset.is_valid() and anexo_formset.is_valid():
            loja = form.save(commit=False)
            loja.status = 'P'  # Definir explicitamente o status antes de salvar
            loja.save()
            
            socio_formset.instance = loja
            vendedor_formset.instance = loja
            dadosbancarios_formset.instance = loja
            anexo_formset.instance = loja
            
            socio_formset.save()
            vendedor_formset.save()
            dadosbancarios_formset.save()
            anexo_formset.save()
            
            return redirect('lojas:listar_pre_cadastros')
        else:
            print("\n🚨 Erros no Formulário de Loja 🚨", form.errors)
    else:
        form = LojaForm()
        form.fields['status'].initial = 'P'  # Define "Pendente" como valor inicial diretamente no form
        socio_formset = SocioLojaFormSet(instance=None, prefix='socios')
        vendedor_formset = VendedorLojaFormSet(instance=None, prefix='vendedores')
        dadosbancarios_formset = DadosBancariosFormSet(instance=None, prefix='dadosbancarios')
        anexo_formset = LojaAnexoFormSet(instance=None, prefix='anexos')
    
    return render(request, 'lojas/pre_cadastro.html', {
        'titulo_pagina': f'Solicitação de Cadastramento de Loja',
        'form': form,
        'socio_formset': socio_formset,
        'vendedor_formset': vendedor_formset,
        'dadosbancarios_formset': dadosbancarios_formset,
        'anexo_formset': anexo_formset,
    })



def listar_pre_cadastros(request):
    pre_cadastros = Loja.objects.filter(status='P')
    return render(request, 'lojas/listar_pre_cadastros.html', {'lojas': pre_cadastros})


@csrf_exempt
def criar_vendedor(request):
    if request.method == "POST":
        nome_vendedor = request.POST.get("nome_vendedor")
        cpf_vendedor = request.POST.get("cpf_vendedor")
        celular_vendedor = request.POST.get("celular_vendedor")
        email_vendedor = request.POST.get("email_vendedor", "")
        chave_pix = request.POST.get("chave_pix", "")
        loja_id = request.POST.get("loja")

        if not nome_vendedor or not cpf_vendedor or not celular_vendedor or not loja_id:
            return JsonResponse({"success": False, "error": "Dados inválidos"})

        try:
            loja = Loja.objects.get(id=loja_id)
            vendedor = Vendedor.objects.create(
                nome_vendedor=nome_vendedor,
                cpf_vendedor=cpf_vendedor,
                celular_vendedor=celular_vendedor,
                email_vendedor=email_vendedor,
                chave_pix=chave_pix,
                loja=loja
            )

            return JsonResponse({"success": True, "vendedor_id": vendedor.id})
        except Loja.DoesNotExist:
            return JsonResponse({"success": False, "error": "Loja não encontrada"})
    return JsonResponse({"success": False, "error": "Método inválido"})


def baixar_todos_anexos(request, loja_id):
    loja = get_object_or_404(Loja, id=loja_id)
    anexos = LojaAnexo.objects.filter(loja=loja)
    
    if not anexos.exists():
        return HttpResponse("Nenhum anexo disponível para download.", status=404)
    
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for anexo in anexos:
            if anexo.arquivo:
                file_path = anexo.arquivo.path
                file_name = os.path.basename(file_path)
                with default_storage.open(file_path, 'rb') as file:
                    zip_file.writestr(file_name, file.read())
    
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type='application/zip')
    zip_filename = f"{loja.nm_fantasia}_anexos.zip"
    response['Content-Disposition'] = f'attachment; filename={zip_filename}'
    return response