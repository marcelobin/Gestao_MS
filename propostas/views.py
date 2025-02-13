# propostas/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import Proposta, Veiculo, StatusProposta, PagamentoComissao
from .forms import (
    PropostaForm, ClienteForm, VeiculoForm,
    EnderecoClienteFormSet, ProfissaoClienteFormSet,ContatoClienteFormSet
)
from clientes.models import Cliente, EnderecoCliente, ProfissaoCliente, ContatoCliente
from financeiras.models import Financeira, Modalidade, Segmento, Produto
from usuarios.models import Operador
from lojas.models import Loja, Vendedor
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.db.models import F, Sum, DecimalField
from django.db import transaction  # Para garantir que a operação seja atômica
from django.http import HttpResponse
import os
import locale
from django.core.paginator import Paginator
from datetime import datetime, date, timedelta
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
import calendar
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from PIL import Image as PILImage





# Defina o locale para pt_BR (Brasil)
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def criar_formsets(request, cliente=None, proposta=None, veiculo=None):
    """
    Função auxiliar para criar os formulários e formsets necessários.
    """
    proposta_form = PropostaForm(request.POST or None, instance=proposta)
    cliente_form = ClienteForm(request.POST or None, instance=cliente)
    veiculo_form = VeiculoForm(request.POST or None, instance=veiculo)

    # Se cliente existe, usa o cliente para o formset, senão, usa um Cliente vazio.
    endereco_formset = EnderecoClienteFormSet(request.POST or None, instance=cliente or Cliente(), prefix="enderecos")
    profissao_formset = ProfissaoClienteFormSet(request.POST or None, instance=cliente or Cliente(), prefix="profissoes")
    contato_formset = ContatoClienteFormSet(request.POST or None, instance=cliente or Cliente(), prefix="contatos")

    return proposta_form, cliente_form, veiculo_form, endereco_formset, profissao_formset, contato_formset

def proposta_form_view(request, pk=None):
    if pk:
        proposta = get_object_or_404(Proposta, pk=pk)
        cliente = proposta.cliente
        veiculo = proposta.veiculo
        titulo_pagina = f"Proposta - {proposta.nr_proposta} - {cliente.nm_cliente}"
    else:
        proposta = None
        cliente = None
        veiculo = None
        titulo_pagina = "Cadastrar Proposta"

    if request.method == "POST":
        cpf = request.POST.get('nr_cpf', '').replace('.', '').replace('-', '')

        if cpf:
            cliente = Cliente.objects.filter(nr_cpf=cpf).first()

        # Cria os formsets
        proposta_form, cliente_form, veiculo_form, endereco_formset, profissao_formset, contato_formset = criar_formsets(
            request, cliente, proposta, veiculo
        )

        if all([
            proposta_form.is_valid(),
            cliente_form.is_valid(),
            veiculo_form.is_valid(),
            endereco_formset.is_valid(),
            profissao_formset.is_valid(),
            contato_formset.is_valid(),
        ]):
            cliente = cliente_form.save(commit=False)
            cliente.save()

            loja = proposta_form.cleaned_data.get('loja')
            operador = proposta_form.cleaned_data.get('operador')

            # Atualiza ou cria os endereços (evitando erro UNIQUE)
            for form in endereco_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    cep = form.cleaned_data.get('cep')
                    EnderecoCliente.objects.update_or_create(
                        cliente=cliente,
                        loja=loja,
                        operador=operador,
                        cep=cep,
                        defaults={
                            "endereco": form.cleaned_data.get("endereco"),
                            "bairro": form.cleaned_data.get("bairro"),
                            "cidade": form.cleaned_data.get("cidade"),
                            "uf": form.cleaned_data.get("uf"),
                        }
                    )

            # Atualiza ou cria as profissões (evitando erro UNIQUE)
            for form in profissao_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    cargo = form.cleaned_data.get('cargo')
                    ProfissaoCliente.objects.update_or_create(
                        cliente=cliente,
                        loja=loja,
                        operador=operador,
                        cargo=cargo,
                        defaults={
                            "renda": form.cleaned_data.get("renda"),
                            "outras_rendas": form.cleaned_data.get("outras_rendas"),
                            "local_trabalho": form.cleaned_data.get("local_trabalho"),
                        }
                    )

            # Atualiza ou cria os contatos (evitando erro UNIQUE)
            for form in contato_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    telefone = form.cleaned_data.get("telefone_fixo")
                    celular = form.cleaned_data.get("celular")
                    email   = form.cleaned_data.get("email")
                    ContatoCliente.objects.update_or_create(
                        cliente=cliente,
                        loja=loja,
                        operador=operador,
                        defaults={
                            "telefone_fixo": telefone,
                            "celular": celular,
                            "email": email,
                        }
                    )

            # Processa o formulário de veículo
            veiculo = veiculo_form.save()

            # Processa o formulário de proposta
            proposta = proposta_form.save(commit=False)
            proposta.cliente = cliente
            proposta.veiculo = veiculo

            # Extrai o vendedor do POST; se não houver valor, atribui None
            vendedor_id = request.POST.get('vendedor', '').strip()
            if vendedor_id:
                try:
                    from lojas.models import Vendedor  # Certifique-se de que esse import esteja correto
                    proposta.vendedor = Vendedor.objects.get(pk=vendedor_id)
                except Vendedor.DoesNotExist:
                    proposta.vendedor = None
            else:
                proposta.vendedor = None

            # Atribui automaticamente a filial do operador, se não estiver definida
            if not proposta.filial and proposta.operador:
                proposta.filial = proposta.operador.filial

            proposta.save()

            return redirect('propostas:listar_propostas')

    else:
        proposta_form, cliente_form, veiculo_form, endereco_formset, profissao_formset, contato_formset = criar_formsets(
            request, cliente, proposta, veiculo
        )

    # ✅ Aplicando a formatação correta ao `vl_veiculo` (igual `vl_financiado` e `vl_parcela`)
    if proposta:
        proposta_form.initial['vl_financiado'] = locale.format_string('%.2f', proposta.vl_financiado, grouping=True) if proposta.vl_financiado else ''
        proposta_form.initial['vl_parcela'] = locale.format_string('%.2f', proposta.vl_parcela, grouping=True) if proposta.vl_parcela else ''

    if veiculo:
        veiculo_form.initial['vl_veiculo'] = locale.format_string('%.2f', veiculo.vl_veiculo, grouping=True) if veiculo.vl_veiculo else ''

    if cliente:
        cliente_form.initial['renda'] = ''
        cliente_form.initial['outras_rendas'] = ''
        if cliente.profissoes.exists():
            maior_renda = 0
            maior_outras_rendas = 0
            for profissao in cliente.profissoes.all():
                if profissao.renda:
                    maior_renda = max(maior_renda, profissao.renda)
                if profissao.outras_rendas:
                    maior_outras_rendas = max(maior_outras_rendas, profissao.outras_rendas)
            cliente_form.initial['renda'] = locale.format_string('%.2f', maior_renda, grouping=True)
            cliente_form.initial['outras_rendas'] = locale.format_string('%.2f', maior_outras_rendas, grouping=True)

        for index, pform in enumerate(profissao_formset):
            if cliente.profissoes.all().count() > index:
                profissao = cliente.profissoes.all()[index]
                pform.initial['renda'] = locale.format_string('%.2f', profissao.renda, grouping=True) if profissao.renda else ''
                pform.initial['outras_rendas'] = locale.format_string('%.2f', profissao.outras_rendas, grouping=True) if profissao.outras_rendas else ''

    initial_data = {
        'loja_id': proposta.loja.id if proposta and proposta.loja else '',
        'vendedor_id': proposta.vendedor.id if proposta and proposta.vendedor else '',
        'segmento_id': proposta.segmento.id if proposta and proposta.segmento else '',
        'produto_id': proposta.produto.id if proposta and proposta.produto else '',
        'operador_id': proposta.operador.id if proposta and proposta.operador else '',
        'financeira_id': proposta.financeira.id if proposta and proposta.financeira else '',
        'modalidade_id': proposta.modalidade.id if proposta and proposta.modalidade else '',
    }

    return render(request, 'propostas/proposta_form.html', {
        'titulo_pagina': titulo_pagina,
        'proposta': proposta,
        'proposta_form': proposta_form,
        'cliente_form': cliente_form,
        'veiculo_form': veiculo_form,
        'endereco_formset': endereco_formset,
        'profissao_formset': profissao_formset,
        'contato_formset': contato_formset,
        'formsets': [endereco_formset, profissao_formset, contato_formset],
        **initial_data,
    })

def listar_propostas(request):
    propostas = Proposta.objects.select_related('cliente', 'veiculo', 'status').all()
    titulo_pagina = "Minhas Propostas"
    # Aplicando filtros
    filtro_financeira = request.GET.get('financeira')
    filtro_loja = request.GET.get('loja')
    filtro_operador = request.GET.get('operador')
    filtro_status = request.GET.get('status')
    filtro_dt_proposta_inicio = request.GET.get('dt_proposta_inicio')
    filtro_dt_proposta_fim = request.GET.get('dt_proposta_fim')
    filtro_dt_pagamento_inicio = request.GET.get('dt_pagamento_inicio')
    filtro_dt_pagamento_fim = request.GET.get('dt_pagamento_fim')

    if filtro_financeira:
        propostas = propostas.filter(financeira_id=filtro_financeira)
    if filtro_loja:
        propostas = propostas.filter(loja_id=filtro_loja)
    if filtro_operador:
        propostas = propostas.filter(operador_id=filtro_operador)
    if filtro_status:
        propostas = propostas.filter(status__ds_status=filtro_status)
    if filtro_dt_proposta_inicio:
        propostas = propostas.filter(dt_proposta__gte=filtro_dt_proposta_inicio)
    if filtro_dt_proposta_fim:
        propostas = propostas.filter(dt_proposta__lte=filtro_dt_proposta_fim)
    if filtro_dt_pagamento_inicio:
        propostas = propostas.filter(dt_pagamento__gte=filtro_dt_pagamento_inicio)
    if filtro_dt_pagamento_fim:
        propostas = propostas.filter(dt_pagamento__lte=filtro_dt_pagamento_fim)

    # Ordenação
    ordering = request.GET.get('ordering', 'nr_proposta')
    reverse = request.GET.get('reverse', 'false')

    if reverse == 'true':
        propostas = propostas.order_by(f"-{ordering}")
    else:
        propostas = propostas.order_by(ordering)

    # Paginação
    registros_por_pagina = int(request.GET.get('registros_por_pagina', 100))  # Padrão: 10 registros por página
    paginator = Paginator(propostas, registros_por_pagina)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Obter todos os objetos relacionados para os menus de filtro
    lojas = Loja.objects.all()
    financeiras = Financeira.objects.all()
    operadores = Operador.objects.all()
    status_list = StatusProposta.objects.all()

    # Contexto para o template
    context = {
        'page_obj': page_obj,
        'lojas': lojas,
        'financeiras': financeiras,
        'operadores': operadores,
        'status_list': status_list,
        'filtro_financeira': filtro_financeira,
        'filtro_loja': filtro_loja,
        'filtro_operador': filtro_operador,
        'filtro_status': filtro_status,
        'filtro_dt_proposta_inicio': filtro_dt_proposta_inicio,
        'filtro_dt_proposta_fim': filtro_dt_proposta_fim,
        'filtro_dt_pagamento_inicio': filtro_dt_pagamento_inicio,
        'filtro_dt_pagamento_fim': filtro_dt_pagamento_fim,
        'ordering': ordering,
        'reverse': reverse,
        'registros_por_pagina': registros_por_pagina,
        'titulo_pagina': titulo_pagina,

    }

    return render(request, 'propostas/listar_propostas.html', context)


def detalhe_proposta(request, pk):
    # Busca a proposta pelo ID (pk)
    proposta = get_object_or_404(Proposta, pk=pk)

    # Relacionamentos: cliente e veículo
    cliente = proposta.cliente  # Ajuste conforme o modelo
    veiculo = proposta.veiculo  # Ajuste conforme o modelo

    # Busca endereços e contatos relacionados ao cliente
    enderecos = cliente.enderecos.all()  # Converte RelatedManager para QuerySet
    contatos = cliente.contatos.all()  # Converte RelatedManager para QuerySet

    # Renderiza o template com os dados
    return render(request, 'propostas/detalhe_proposta.html', {
        'titulo_pagina': f'Detalhes da Proposta #{proposta.nr_proposta}',
        'proposta': proposta,
        'cliente': cliente,
        'enderecos': enderecos,  # Passa o QuerySet
        'contatos': contatos,  # Passa o QuerySet
        'veiculo': veiculo,
    })

def get_segmentos(request):
    """ Substitui o antigo get_subsegmentos. Filtra Segmento a partir da Modalidade. """
    modalidade_id = request.GET.get('modalidade_id')
    if modalidade_id and modalidade_id.isdigit():
        segs = Segmento.objects.filter(modalidade_id=modalidade_id).values('id', 'nome_segmento')
        return JsonResponse(list(segs), safe=False)
    return JsonResponse([], safe=False)

def get_produtos(request):
    """ Filtra Produto com base em (financeira_id, segmento_id). """
    financeira_id = request.GET.get('financeira_id')
    segmento_id = request.GET.get('segmento_id')
    if financeira_id and segmento_id and financeira_id.isdigit() and segmento_id.isdigit():
        produtos = Produto.objects.filter(
            financeira_id=financeira_id,
            segmento_id=segmento_id
        ).values('id', 'nome_produto')
        return JsonResponse(list(produtos), safe=False)
    return JsonResponse([], safe=False)

def get_lojas(request):
    operador_id = request.GET.get('operador_id')
    if operador_id:
        lojas = Loja.objects.filter(operador_id=operador_id).values('id', 'nm_fantasia')
        return JsonResponse(list(lojas), safe=False)
    return JsonResponse([], safe=False)

def editar_proposta(request, pk):
    proposta = get_object_or_404(Proposta, pk=pk)
    cliente = proposta.cliente
    veiculo = proposta.veiculo

    if request.method == "POST":
        proposta_form = PropostaForm(request.POST, instance=proposta)
        cliente_form = ClienteForm(request.POST, instance=cliente)
        veiculo_form = VeiculoForm(request.POST, instance=veiculo)

        endereco_formset = EnderecoClienteFormSet(request.POST, instance=cliente)
        profissao_formset = ProfissaoClienteFormSet(request.POST, instance=cliente)

        if (
            proposta_form.is_valid()
            and cliente_form.is_valid()
            and veiculo_form.is_valid()
            and endereco_formset.is_valid()
            and profissao_formset.is_valid()
        ):
            proposta_form.save()
            cliente_form.save()
            veiculo_form.save()
            endereco_formset.save()
            profissao_formset.save()
            return redirect('propostas:listar_propostas')
    else:
        proposta_form = PropostaForm(instance=proposta)
        cliente_form = ClienteForm(instance=cliente)
        veiculo_form = VeiculoForm(instance=veiculo)
        endereco_formset = EnderecoClienteFormSet(instance=cliente)
        profissao_formset = ProfissaoClienteFormSet(instance=cliente)

    return render(request, 'propostas/editar_proposta.html', {
        'proposta_form': proposta_form,
        'cliente_form': cliente_form,
        'veiculo_form': veiculo_form,
        'endereco_formset': endereco_formset,
        'profissao_formset': profissao_formset,
        'proposta': proposta,
    })

def verificar_cliente_api(request):
    """
    Verifica se um cliente com CPF existe.
    Se sim, retorna dados básicos e, se a 'loja_id' e 'operador_id' baterem,
    retorna também endereços/contatos/profissoes para reutilizar.
    """
    cpf      = request.GET.get('cpf', '').replace('.', '').replace('-', '')
    loja_id  = request.GET.get('loja_id')
    operador_id = request.GET.get('operador_id')

    data = {'existe': False}
    if len(cpf) == 11:
        cliente = Cliente.objects.filter(nr_cpf=cpf).first()
        if cliente:
            data['existe']       = True
            data['id']           = cliente.id
            data['nm_cliente']   = cliente.nm_cliente
            data['dt_nascimento']= str(cliente.dt_nascimento) if cliente.dt_nascimento else ''
            data['rg_cliente']   = cliente.rg_cliente or ''
            data['nm_mae']       = cliente.nm_mae or ''
            # etc

            # Verifica se o user deve "reutilizar" endereços, contatos, etc.
            # Critério: se "loja_id" e "operador_id" coincidem com as do EnderecoCliente/ContatoCliente...
            # MAS primeiro precisamos ter adicionado "loja" e "operador" a EnderecoCliente se for esse o critério
            # Exemplo:
            #   enderecos = EnderecoCliente.objects.filter(cliente=cliente, loja_id=loja_id, operador_id=operador_id)
            # Se não existirem esses campos, você decide outra lógica.

            enderecos = []
            contatos  = []
            profissoes= []
            
            # Exemplo de verificação:
            # if ... (some logic) ...
            #   Reaproveita
            end_objs = EnderecoCliente.objects.filter(cliente=cliente)
            enderecos = [{
                'id': e.id,
                'cep': e.cep,
                'endereco': e.endereco,
                'nro': e.nro,
                'complemento': e.complemento,
                'bairro': e.bairro,
                'cidade': e.cidade,
                'uf': e.uf,
            } for e in end_objs]

            cont_objs = ContatoCliente.objects.filter(cliente=cliente)
            contatos = [{
                'id': c.id,
                'telefone_fixo': c.telefone_fixo,
                'celular': c.celular,
                'email': c.email,
            } for c in cont_objs]

            prof_objs = ProfissaoCliente.objects.filter(cliente=cliente)
            profissoes = [{
                'id': p.id,
                'profissao': p.profissao,
                'cargo': p.cargo,
                # ...
            } for p in prof_objs]

            data['enderecos']   = enderecos
            data['contatos']    = contatos
            data['profissoes']  = profissoes
            # Se a lógica diz "só reutiliza se for a mesma loja/operador", decida se retorna
            data['reutilizar_enderecos'] = True  # ou False conforme a regra
    return JsonResponse(data)

def get_modalidades_por_financeira(request):
    """Retorna (de forma DISTINCT) as Modalidades disponíveis para a Financeira informada,
       baseado nos produtos cadastrados."""
    financeira_id = request.GET.get('financeira_id')
    if financeira_id and financeira_id.isdigit():
        # Query em Produto: filtra finance = essa, extraindo produto.segmento.modalidade de forma distinta
        produtos = Produto.objects.filter(financeira_id=financeira_id).select_related('segmento__modalidade')
        modalidades_distintas = set(p.segmento.modalidade for p in produtos)
        # Transformar em lista de dicionários
        data = [{
            'id': mod.id,
            'nome_modalidade': mod.nome_modalidade
        } for mod in modalidades_distintas if mod is not None]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)


def get_segmentos_por_financeira_modalidade(request):
    """Retorna DISTINCT Segmentos para dada Financeira + Modalidade,
       baseado nos produtos cadastrados."""
    financeira_id = request.GET.get('financeira_id')
    modalidade_id = request.GET.get('modalidade_id')
    if financeira_id and financeira_id.isdigit() and modalidade_id and modalidade_id.isdigit():
        produtos = Produto.objects.filter(
            financeira_id=financeira_id,
            segmento__modalidade_id=modalidade_id
        ).select_related('segmento__modalidade')
        segmentos_distintos = set(p.segmento for p in produtos)
        data = [{
            'id': seg.id,
            'nome_segmento': seg.nome_segmento
        } for seg in segmentos_distintos]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)


def get_produtos_por_financeira_modalidade_segmento(request):
    """Retorna os Produtos (Financeira + Modalidade + Segmento)"""
    financeira_id = request.GET.get('financeira_id')
    modalidade_id = request.GET.get('modalidade_id')
    segmento_id = request.GET.get('segmento_id')
    if (financeira_id and financeira_id.isdigit() and 
        modalidade_id and modalidade_id.isdigit() and
        segmento_id and segmento_id.isdigit()):
        
        produtos = Produto.objects.filter(
            financeira_id=financeira_id,
            segmento_id=segmento_id,
            segmento__modalidade_id=modalidade_id
        )
        data = [{
            'id': prod.id,
            'nome_produto': prod.nome_produto
        } for prod in produtos]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)


def get_vendedores_por_loja(request):
    """Retorna todos os Vendedores vinculados a uma determinada Loja."""
    loja_id = request.GET.get('loja_id')
    if loja_id and loja_id.isdigit():
        # Filtra todos os Vendedores onde loja_id = loja_id recebido
        vendedores = Vendedor.objects.filter(loja_id=loja_id)
        # Transforma em lista de dicionários para serializar em JSON
        data = [
            {
                'id': vend.id,
                'nome_vendedor': vend.nome_vendedor
                # adicione outros campos se precisar
            }
            for vend in vendedores
        ]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

def atualizar_status_proposta(request, pk):
    """
    Atualiza apenas o status (e dt_pagamento se for 'Paga') de uma proposta,
    via AJAX.
    """
    if request.method == 'POST':
        proposta = get_object_or_404(Proposta, pk=pk)
        
        novo_status = request.POST.get('novo_status')
        dt_pagamento = request.POST.get('dt_pagamento', '')  # pode vir vazio

        # Busca o objeto StatusProposta correspondendo a 'novo_status'
        try:
            status_obj = StatusProposta.objects.get(ds_status__iexact=novo_status)
        except StatusProposta.DoesNotExist:
            return JsonResponse({'erro': 'Status inválido'}, status=400)

        # Atualiza a proposta
        proposta.status = status_obj

        # Se novo status for 'Paga', atualizar dt_pagamento
        if novo_status.lower() == 'paga' and dt_pagamento:
            try:
                proposta.dt_pagamento = datetime.strptime(dt_pagamento, '%Y-%m-%d').date()
            except ValueError:
                proposta.dt_pagamento = None
        else:
            # Se não é "Paga", pode opcionalmente limpar dt_pagamento
            # proposta.dt_pagamento = None  # se fizer sentido
            pass
        
        proposta.save()

        return JsonResponse({
            'mensagem': 'Status atualizado com sucesso',
            'novo_status': status_obj.ds_status,      # ex. 'Aprovada'
            'dt_pagamento': str(proposta.dt_pagamento or '')  
        })
    return JsonResponse({'erro': 'Método inválido'}, status=405)


def gerar_lista_periodos(qtd=12):
    """
    Retorna uma lista de períodos no formato (valor, label), onde:
      - valor: string "AAAA-MM"
      - label: string legível, ex.: "Maio 2023"
    Retorna os últimos 'qtd' meses, incluindo o mês atual.
    """
    meses = []
    hoje = timezone.now().date().replace(day=1)
    for i in range(qtd):
        mes_date = hoje - timedelta(days=i * 30)  # Retrocede aproximadamente 1 mês por iteração
        ano = mes_date.year
        mes = mes_date.month
        valor = f"{ano}-{mes:02d}"
        label = date(ano, mes, 1).strftime("%B %Y").capitalize()  # ex.: "Maio 2023"
        meses.append((valor, label))
    
    return meses

def lojas_elegiveis(request):
    # Obtém o período selecionado no formato "AAAA-MM"
    periodo = request.GET.get('periodo')
    if periodo:
        try:
            ano, mes = map(int, periodo.split("-"))
            start_date = date(year=ano, month=mes, day=1)
            last_day = calendar.monthrange(ano, mes)[1]
            end_date = start_date.replace(day=last_day)
        except Exception:
            hoje = timezone.now().date()
            start_date = hoje.replace(day=1)
            last_day = calendar.monthrange(hoje.year, hoje.month)[1]
            end_date = hoje.replace(day=last_day)
            periodo = f"{hoje.year}-{hoje.month:02d}"
    else:
        hoje = timezone.now().date()
        start_date = hoje.replace(day=1)
        last_day = calendar.monthrange(hoje.year, hoje.month)[1]
        end_date = hoje.replace(day=last_day)
        periodo = f"{hoje.year}-{hoje.month:02d}"

    # Filtra as propostas do período
    propostas_do_periodo = Proposta.objects.filter(dt_proposta__gte=start_date, dt_proposta__lte=end_date)
    lojas_ids = propostas_do_periodo.values_list('loja', flat=True).distinct()

    lojas_elegiveis_list = []
    for loja_id in lojas_ids:
        loja = get_object_or_404(Loja, pk=loja_id)

        # Todas as propostas (incluindo pagas)
        todas_propostas = propostas_do_periodo.filter(loja=loja)

        # Calcula o total financiado
        total_financiado = todas_propostas.aggregate(Sum('vl_financiado'))['vl_financiado__sum'] or Decimal("0.00")

        # Propostas pendentes de pagamento de comissão
        propostas_pendentes = todas_propostas.filter(dt_pagamento_retorno__isnull=True)
        total_pendente = propostas_pendentes.aggregate(
            total_comissao=Sum(F('vl_financiado') * Decimal("0.012"), output_field=DecimalField())
        )['total_comissao'] or Decimal("0.00")

        # Calcula o total da comissão paga
        total_comissao_paga = todas_propostas.filter(dt_pagamento_retorno__isnull=False).aggregate(
            total_comissao=Sum(F('vl_financiado') * Decimal("0.012"), output_field=DecimalField())
        )['total_comissao'] or Decimal("0.00")

        # Cria a lista de propostas formatadas
        propostas_formatadas = []
        for proposta in todas_propostas:
            vl_financiado = Decimal(proposta.vl_financiado or 0)
            comissao = vl_financiado * Decimal("0.012")
            propostas_formatadas.append({
                "id": proposta.id,
                "nr_proposta": proposta.nr_proposta,
                "cliente": proposta.cliente.nm_cliente if proposta.cliente else "Sem Cliente",
                "vl_financiado": vl_financiado,
                "comissao": comissao,
                "dt_pagamento_retorno": proposta.dt_pagamento_retorno,
            })

        # Define a elegibilidade com base na comissão pendente
        elegivel = total_pendente >= Decimal("300")

        lojas_elegiveis_list.append({
            'loja': loja,
            'total_pendente': total_pendente,
            'total_financiado': total_financiado,
            'total_comissao_paga': total_comissao_paga,
            'todas_propostas': propostas_formatadas,
            'elegivel': elegivel,
        })

    # Dados adicionais para preencher os filtros no template
    periodos = gerar_lista_periodos(12)
    lojas_all = Loja.objects.all()
    operadores = Operador.objects.all()
    # Se o modelo Loja possuir o campo 'filial', extrai os valores únicos; ajuste se necessário
    filiais = list({loja.filial for loja in lojas_all if getattr(loja, 'filial', None)})

    context = {
        'lojas_elegiveis': lojas_elegiveis_list,
        'periodo_selecionado': periodo,
        'periodos': periodos,
        'lojas': lojas_all,
        'operadores': operadores,
        'filiais': filiais,
    }
    return render(request, 'propostas/lojas_elegiveis.html', context)



def gerar_recibo_pagamento(request):
    if request.method == 'POST':
        proposta_ids = request.POST.getlist('propostas')
        loja_id = request.POST.get('loja')
        action = request.POST.get('action', 'gerar')  # valor padrão "gerar"

        if not proposta_ids or not loja_id:
            return JsonResponse({"success": False, "error": "Nenhuma proposta selecionada."}, status=400)

        if action == 'gerar':
            # Seleciona apenas as propostas que ainda não foram pagas
            propostas = Proposta.objects.filter(id__in=proposta_ids, dt_pagamento_retorno__isnull=True)
        elif action == 'recuperar':
            # Seleciona as propostas que já foram pagas
            propostas = Proposta.objects.filter(id__in=proposta_ids, dt_pagamento_retorno__isnull=False)
        else:
            propostas = Proposta.objects.filter(id__in=proposta_ids)

        if not propostas.exists():
            print("❌ Nenhuma proposta encontrada para pagamento!")
            return JsonResponse({"success": False, "error": "Nenhuma proposta elegível para pagamento."}, status=400)

        print(f"🔎 Propostas encontradas: {[p.id for p in propostas]}")
        total_financiado = propostas.aggregate(total=Sum('vl_financiado'))['total'] or 0.00
        total_financiado = Decimal(str(total_financiado))
        total_comissao = (total_financiado * Decimal("0.012")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        numero_recibo = f"{loja_id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"

        if action == 'gerar':
            # Cria um novo registro de pagamento e atualiza as propostas pendentes
            pagamento = PagamentoComissao.objects.create(
                loja_id=loja_id,
                total_financiado=total_financiado,
                total_comissao=total_comissao,
                numero_recibo=numero_recibo,
                data_pagamento=timezone.now()
            )
            pagamento.propostas.set(propostas)
            propostas.update(dt_pagamento_retorno=timezone.now())
        else:  # action == 'recuperar'
            # Tenta recuperar o pagamento já efetuado associado a essas propostas
            pagamento = PagamentoComissao.objects.filter(propostas__in=propostas).first()
            if not pagamento:
                return JsonResponse({"success": False, "error": "Recibo não encontrado."}, status=400)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": True, "recibo_url": f"/propostas/recibo/{pagamento.id}/"})
        return redirect('propostas:detalhe_recibo', pk=pagamento.pk)
    
    return JsonResponse({"success": False, "error": "Método inválido."}, status=405)



def detalhe_recibo(request, pk):
    """
    Exibe o recibo de pagamento detalhado, listando cada proposta com:
      - Número da proposta
      - Nome do cliente
      - Valor financiado
      - Data do pagamento da comissão (dt_pagamento_retorno)
    """
    recibo = get_object_or_404(PagamentoComissao, pk=pk)
    propostas = recibo.propostas.all()
    context = {
        'recibo': recibo,
        'propostas': propostas,
    }
    return render(request, 'propostas/detalhe_recibo.html', context)


def pagamentos_list(request):
    pagamentos = PagamentoComissao.objects.all().order_by('-data_pagamento')
    return render(request, 'propostas/pagamentos_list.html', {'pagamentos': pagamentos})

def gerar_recibo_pdf(request, pk):
    # Obtém o pagamento e as propostas associadas
    recibo = PagamentoComissao.objects.get(pk=pk)
    propostas = recibo.propostas.all()

    # Configura o response como um PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Recibo_{recibo.numero_recibo}.pdf"'

    # Criando o PDF
    pdf = SimpleDocTemplate(response, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=50, bottomMargin=50)
    elements = []
    styles = getSampleStyleSheet()

    # Caminho da logo
    logo_path = os.path.join("static", "images", "MS_Logo_Azul.png")

    # ✅ Ajustando a logo para manter a proporção e evitar problemas
    if os.path.exists(logo_path):
        with PILImage.open(logo_path) as pil_image:
            pil_image.thumbnail((220, 80))  # Redimensiona mantendo a proporção
            temp_path = os.path.join("static", "images", "temp_logo.png")
            pil_image.save(temp_path)  # Salva a imagem temporária
            img = Image(temp_path, width=pil_image.width, height=pil_image.height)
            elements.append(img)

    # 🏆 Título estilizado
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<strong>MS FINANCIAMENTOS - PAGAMENTO COMISSÃO - BANCO DAYCOVAL</strong>", styles['Title']))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(f"<strong><i>LOJA - {recibo.loja.nm_fantasia}</i></strong>", styles['Heading2']))
    elements.append(Paragraph(f"<strong>Data do Pagamento:</strong> {recibo.data_pagamento.strftime('%d/%m/%Y')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Criando a tabela de propostas
    data = [["DATA FINANC.", "CLIENTE", "VALOR FINANC. R$", "COMISSÃO R$", "DATA CRÉDITO"]]

    for proposta in propostas:
        data.append([
            proposta.dt_proposta.strftime('%d/%m/%Y') if proposta.dt_proposta else "-",
            proposta.cliente.nm_cliente,
            f"R$ {proposta.vl_financiado:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            f"R$ {Decimal(proposta.vl_financiado) * Decimal(0.012):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            proposta.dt_pagamento_retorno.strftime('%d/%m/%Y') if proposta.dt_pagamento_retorno else "-"
        ])

    # Adicionando a linha de totais
    data.append(["", "VALORES DO PERÍODO", f"R$ {recibo.total_financiado:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                 f"R$ {recibo.total_comissao:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), ""])

    # Criando e estilizando a tabela
    tabela = Table(data, colWidths=[90, 200, 100, 100, 100])
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),  # Cabeçalho azul escuro
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Texto branco no cabeçalho
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#b3d9ff")),  # Fundo azul claro para totais
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 2, colors.black),  # Linha grossa no total
    ]))

    elements.append(tabela)

    # Construindo o PDF
    pdf.build(elements)

    return response

