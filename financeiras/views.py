from django.shortcuts import render, redirect, get_object_or_404
from .models import Financeira, Segmento, Modalidade
from .forms import FinanceiraForm, DepartamentoFormSet, ProdutoFormSet
from django.http import JsonResponse



def financeira_create(request):
    if request.method == "POST":
        financeira_form = FinanceiraForm(request.POST)
        departamento_formset = DepartamentoFormSet(request.POST)
        produto_formset = ProdutoFormSet(request.POST)

        if financeira_form.is_valid() and departamento_formset.is_valid() and produto_formset.is_valid():
            financeira = financeira_form.save()
            departamento_formset.instance = financeira
            produto_formset.instance = financeira
            departamento_formset.save()
            produto_formset.save()
            return redirect('financeiras:financeira_list')
    else:
        financeira_form = FinanceiraForm()
        departamento_formset = DepartamentoFormSet()
        produto_formset = ProdutoFormSet()

    return render(request, 'financeiras/financeira_form.html', {
        'financeira_form': financeira_form,
        'departamento_formset': departamento_formset,
        'produto_formset': produto_formset,
    })


def financeira_list(request):
    """Lista todas as financeiras cadastradas."""
    financeiras = Financeira.objects.all()
    
    contexto = {
        'financeiras': financeiras,
        'titulo_pagina': 'Financeiras'  # Adicionando o título ao contexto
    }

    return render(request, 'financeiras/financeira_list.html', contexto)



def financeira_detail(request, pk):
    financeira = get_object_or_404(Financeira, pk=pk)
    departamentos = financeira.departamentos.all()
    produtos = financeira.produtos.all()
    return render(request, 'financeiras/financeira_detail.html', {
        'financeira': financeira,
        'departamentos': departamentos,
        'produtos': produtos,
    })


def financeira_update(request, pk):
    financeira = get_object_or_404(Financeira, pk=pk)
    if request.method == "POST":
        financeira_form = FinanceiraForm(request.POST, instance=financeira)
        departamento_formset = DepartamentoFormSet(request.POST, instance=financeira)
        produto_formset = ProdutoFormSet(request.POST, instance=financeira)

        if (financeira_form.is_valid() and 
            departamento_formset.is_valid() and 
            produto_formset.is_valid()):
            
            financeira = financeira_form.save()
            departamento_formset.save()
            produto_formset.save()
            return redirect('financeiras:financeira_detail', pk=financeira.pk)
    else:
        financeira_form = FinanceiraForm(instance=financeira)
        departamento_formset = DepartamentoFormSet(instance=financeira)
        produto_formset = ProdutoFormSet(instance=financeira)

    return render(request, 'financeiras/financeira_form.html', {
        'financeira_form': financeira_form,
        'departamento_formset': departamento_formset,
        'produto_formset': produto_formset,
    })
    
def get_segmentos_por_modalidade(request):
    """Retorna os Segmentos de uma dada Modalidade"""
    modalidade_id = request.GET.get('modalidade_id')

    if modalidade_id and modalidade_id.isdigit():
        segmentos = Segmento.objects.filter(modalidade_id=modalidade_id)
        data = [{
            'id': seg.id,
            'nome': seg.nome_segmento  # ou 'nome', dependendo do nome do campo no seu modelo
        } for seg in segmentos]
        return JsonResponse(data, safe=False)

    return JsonResponse([], safe=False)    
