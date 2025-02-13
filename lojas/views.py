#lojas/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from .models import Loja, Socio, Vendedor, DadosBancarios, LojaAnexo
from usuarios.models import Operador, Filial
from .forms import (
    LojaForm,
    SocioLojaFormSet,
    VendedorLojaFormSet,
    DadosBancariosFormSet,
    LojaFinanceiraAcessoFormSet,
    LojaAnexoFormSet
)
from django.http import JsonResponse
from django.conf import settings
import json
import os
from pathlib import Path


# View para listar lojas
def listar_lojas(request):
    lojas = Loja.objects.all()

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

        if form.is_valid() and socio_formset.is_valid() and vendedor_formset.is_valid() and dadosbancarios_formset.is_valid() and acesso_formset.is_valid():
            loja = form.save()
            socio_formset.instance = loja
            socio_formset.save()
            vendedor_formset.instance = loja
            vendedor_formset.save()
            dadosbancarios_formset.instance = loja
            dadosbancarios_formset.save()
            acesso_formset.instance = loja
            acesso_formset.save()

            return redirect('lojas:listar_lojas')
    else:
        form = LojaForm(instance=loja)
        socio_formset = SocioLojaFormSet(instance=loja, prefix='socios')
        vendedor_formset = VendedorLojaFormSet(instance=loja, prefix='vendedores')
        dadosbancarios_formset = DadosBancariosFormSet(instance=loja, prefix='dadosbancarios')
        acesso_formset = LojaFinanceiraAcessoFormSet(instance=loja, prefix='acessos_financeiras')

    return render(request, 'lojas/criar_editar_loja.html', {
        'form': form,
        'socio_formset': socio_formset,
        'vendedor_formset': vendedor_formset,
        'dadosbancarios_formset': dadosbancarios_formset,
        'acesso_formset': acesso_formset,
        'bancos_data': bancos_data,  # Passar o JSON ao template
        
    })


# View para deletar loja
def deletar_loja(request, loja_id):
    loja = get_object_or_404(Loja, pk=loja_id)
    if request.method == 'POST':
        loja.delete()
        return redirect('listar_lojas')
    return render(request, 'lojas/deletar_loja.html', {'loja': loja})

# View para visualizar loja
def loja_detail(request, loja_id):
    loja = get_object_or_404(Loja, pk=loja_id)
    socios = loja.socios.all()
    vendedores = loja.vendedores.all()
    dadosbancarios = loja.dadosbancarios.all()
    acessos = loja.acessos_financeiras.all()  # Obtem os acessos associados à loja

    return render(request, 'lojas/loja_detail.html', {
        'loja': loja,
        'socios': socios,
        'vendedores': vendedores,
        'dadosbancarios': dadosbancarios,
        'acessos': acessos,  # Inclui os acessos no contexto
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
    if request.method == 'POST':
        form = LojaForm(request.POST, request.FILES)
        socio_formset = SocioLojaFormSet(request.POST, request.FILES, instance=None, prefix='socios')
        vendedor_formset = VendedorLojaFormSet(request.POST, instance=None, prefix='vendedores')
        dadosbancarios_formset = DadosBancariosFormSet(request.POST, instance=None, prefix='dadosbancarios')
        acesso_formset = LojaFinanceiraAcessoFormSet(request.POST, instance=None, prefix='acessos_financeiras')
        anexo_formset = LojaAnexoFormSet(request.POST, request.FILES, instance=None, prefix='anexos')
        
        if (form.is_valid() and socio_formset.is_valid() and vendedor_formset.is_valid() and 
            dadosbancarios_formset.is_valid() and acesso_formset.is_valid() and anexo_formset.is_valid()):
            
            loja = form.save(commit=False)
            loja.status = 'P'  # Pré-cadastro
            loja.operador = request.user.operador  # Ajuste conforme sua lógica
            loja.save()

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

            return redirect('alguma_view_de_sucesso')
    else:
        form = LojaForm()
        socio_formset = SocioLojaFormSet(instance=None, prefix='socios')
        vendedor_formset = VendedorLojaFormSet(instance=None, prefix='vendedores')
        dadosbancarios_formset = DadosBancariosFormSet(instance=None, prefix='dadosbancarios')
        acesso_formset = LojaFinanceiraAcessoFormSet(instance=None, prefix='acessos_financeiras')
        anexo_formset = LojaAnexoFormSet(instance=None, prefix='anexos')
    
    context = {
        'form': form,
        'socio_formset': socio_formset,
        'vendedor_formset': vendedor_formset,
        'dadosbancarios_formset': dadosbancarios_formset,
        'acesso_formset': acesso_formset,
        'anexo_formset': anexo_formset,
    }
    return render(request, 'lojas/pre_cadastro.html', context)

    if request.method == 'POST':
        form = LojaForm(request.POST, request.FILES)
        socio_formset = SocioLojaFormSet(request.POST, request.FILES, instance=None, prefix='socios')
        vendedor_formset = VendedorLojaFormSet(request.POST, instance=None, prefix='vendedores')
        dadosbancarios_formset = DadosBancariosFormSet(request.POST, instance=None, prefix='dadosbancarios')
        acesso_formset = LojaFinanceiraAcessoFormSet(request.POST, instance=None, prefix='acessos_financeiras')
        
        if (form.is_valid() and socio_formset.is_valid() and vendedor_formset.is_valid() and
            dadosbancarios_formset.is_valid() and acesso_formset.is_valid()):
            
            loja = form.save(commit=False)
            loja.status = 'P'
            loja.operador = request.user.operador  # ou conforme sua lógica
            loja.save()
            
            socio_formset.instance = loja
            socio_formset.save()
            
            vendedor_formset.instance = loja
            vendedor_formset.save()
            
            dadosbancarios_formset.instance = loja
            dadosbancarios_formset.save()
            
            acesso_formset.instance = loja
            acesso_formset.save()
            
            return redirect('alguma_view_de_sucesso')
    else:
        form = LojaForm()
        socio_formset = SocioLojaFormSet(instance=None, prefix='socios')
        vendedor_formset = VendedorLojaFormSet(instance=None, prefix='vendedores')
        dadosbancarios_formset = DadosBancariosFormSet(instance=None, prefix='dadosbancarios')
        acesso_formset = LojaFinanceiraAcessoFormSet(instance=None, prefix='acessos_financeiras')
    
    context = {
        'form': form,
        'socio_formset': socio_formset,
        'vendedor_formset': vendedor_formset,
        'dadosbancarios_formset': dadosbancarios_formset,
        'acesso_formset': acesso_formset,
    }
    return render(request, 'lojas/pre_cadastro.html', context)



def listar_pre_cadastros(request):
    pre_cadastros = Loja.objects.filter(status='P')
    return render(request, 'lojas/lista_pre_cadastros.html', {'lojas': pre_cadastros})
