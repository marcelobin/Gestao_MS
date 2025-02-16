# propostas/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import Proposta, Veiculo, StatusProposta, PagamentoComissao
from .forms import (
    PropostaForm, ClienteForm, VeiculoForm,
    EnderecoClienteForm, ProfissaoClienteForm, ContatoClienteForm
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
from django.views.decorators.csrf import csrf_exempt






# Defina o locale para pt_BR (Brasil)
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

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


def proposta_form_view(request, pk=None):
    """
    View corrigida para evitar duplicados em (cliente, loja, operador) e
    preencher corretamente os campos de profissão/contato/endereço.
    """
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

    # Endereço, profissão e contato, inicialmente None
    endereco = None
    profissao = None
    contato = None

    if request.method == "POST":
        # Tenta identificar o cliente via CPF
        cpf = request.POST.get('nr_cpf', '').replace('.', '').replace('-', '')
        if cpf:
            cliente = Cliente.objects.filter(nr_cpf=cpf).first()

        # Primeiro criamos o PropostaForm para descobrir loja/operador
        proposta_form = PropostaForm(request.POST, instance=proposta)
        cliente_form = ClienteForm(request.POST, instance=cliente)
        veiculo_form = VeiculoForm(request.POST, instance=veiculo)

        # Precisamos validar a proposta para obter 'loja' e 'operador'
        if proposta_form.is_valid():
            loja = proposta_form.cleaned_data['loja']
            operador = proposta_form.cleaned_data['operador']
        else:
            loja = None
            operador = None

        # Se temos cliente, loja e operador, buscamos registros existentes
        if cliente and loja and operador:
            endereco = EnderecoCliente.objects.filter(
                cliente=cliente, loja=loja, operador=operador
            ).first()
            profissao = ProfissaoCliente.objects.filter(
                cliente=cliente, loja=loja, operador=operador
            ).first()
            contato = ContatoCliente.objects.filter(
                cliente=cliente, loja=loja, operador=operador
            ).first()

        # Instancia os forms com as instâncias corretas
        endereco_form = EnderecoClienteForm(request.POST, instance=endereco, prefix="endereco")
        profissao_form = ProfissaoClienteForm(request.POST, instance=profissao, prefix="profissao")
        contato_form = ContatoClienteForm(request.POST, instance=contato, prefix="contato")

        # Valida todos
        forms_validos = (
            proposta_form.is_valid() and
            cliente_form.is_valid() and
            veiculo_form.is_valid() and
            endereco_form.is_valid() and
            profissao_form.is_valid() and
            contato_form.is_valid()
        )

        if forms_validos:
            # Salva/atualiza o cliente
            cliente = cliente_form.save()

            # Salva ou atualiza endereço
            end_inst = endereco_form.save(commit=False)
            end_inst.cliente = cliente
            end_inst.loja = loja
            end_inst.operador = operador
            end_inst.save()

            # Salva ou atualiza profissão
            prof_inst = profissao_form.save(commit=False)
            prof_inst.cliente = cliente
            prof_inst.loja = loja
            prof_inst.operador = operador
            prof_inst.save()

            # Salva ou atualiza contato
            cont_inst = contato_form.save(commit=False)
            cont_inst.cliente = cliente
            cont_inst.loja = loja
            cont_inst.operador = operador
            cont_inst.save()

            # Salva o veículo
            veiculo = veiculo_form.save()

            # Salva a proposta
            proposta = proposta_form.save(commit=False)
            proposta.cliente = cliente
            proposta.veiculo = veiculo

            # Ajusta vendedor
            vendedor_id = request.POST.get('vendedor', '').strip()
            if vendedor_id:
                try:
                    from lojas.models import Vendedor
                    proposta.vendedor = Vendedor.objects.get(pk=vendedor_id)
                except Vendedor.DoesNotExist:
                    proposta.vendedor = None
            else:
                proposta.vendedor = None

            # Atribui filial do operador, se não estiver definida
            if not proposta.filial and proposta.operador:
                proposta.filial = proposta.operador.filial

            proposta.save()
            return redirect('propostas:listar_propostas')

    else:
        # GET
        if cliente:
            # Se já existe, filtra (cliente, loja, operador) da proposta (se houver)
            loja = proposta.loja if proposta and proposta.loja else None
            operador = proposta.operador if proposta and proposta.operador else None
            if loja and operador:
                endereco = EnderecoCliente.objects.filter(cliente=cliente, loja=loja, operador=operador).first()
                profissao = ProfissaoCliente.objects.filter(cliente=cliente, loja=loja, operador=operador).first()
                contato = ContatoCliente.objects.filter(cliente=cliente, loja=loja, operador=operador).first()

        proposta_form = PropostaForm(instance=proposta)
        cliente_form = ClienteForm(instance=cliente)
        veiculo_form = VeiculoForm(instance=veiculo)
        endereco_form = EnderecoClienteForm(instance=endereco, prefix="endereco")
        profissao_form = ProfissaoClienteForm(instance=profissao, prefix="profissao")
        contato_form = ContatoClienteForm(instance=contato, prefix="contato")

    # Ajuste de formatação de valores monetários
    if proposta:
        if proposta.vl_financiado:
            proposta_form.initial['vl_financiado'] = locale.format_string('%.2f', proposta.vl_financiado, grouping=True)
        if proposta.vl_parcela:
            proposta_form.initial['vl_parcela'] = locale.format_string('%.2f', proposta.vl_parcela, grouping=True)

    if veiculo and veiculo.vl_veiculo:
        veiculo_form.initial['vl_veiculo'] = locale.format_string('%.2f', veiculo.vl_veiculo, grouping=True)

    # Dados para o JS
    initial_data = {
        'loja_id': proposta.loja.id if (proposta and proposta.loja) else '',
        'vendedor_id': proposta.vendedor.id if (proposta and proposta.vendedor) else '',
        'segmento_id': proposta.segmento.id if (proposta and proposta.segmento) else '',
        'produto_id': proposta.produto.id if (proposta and proposta.produto) else '',
        'operador_id': proposta.operador.id if (proposta and proposta.operador) else '',
        'financeira_id': proposta.financeira.id if (proposta and proposta.financeira) else '',
        'modalidade_id': proposta.modalidade.id if (proposta and proposta.modalidade) else '',
    }

    return render(request, 'propostas/proposta_form.html', {
        'titulo_pagina': titulo_pagina,
        'proposta': proposta,
        'proposta_form': proposta_form,
        'cliente_form': cliente_form,
        'veiculo_form': veiculo_form,
        'endereco_form': endereco_form,
        'profissao_form': profissao_form,
        'contato_form': contato_form,
        'formsets': [],
        **initial_data,
    })



def listar_propostas(request):
    propostas = Proposta.objects.select_related('cliente', 'veiculo', 'status').all()
    titulo_pagina = "Minhas Propostas"

    # Obtendo os parâmetros da requisição GET
    filtro_financeira = request.GET.get('financeira')
    filtro_loja = request.GET.get('loja')
    filtro_operador = request.GET.get('operador')
    filtro_status = request.GET.get('status')
    filtro_dt_proposta_inicio = request.GET.get('dt_proposta_inicio')
    filtro_dt_proposta_fim = request.GET.get('dt_proposta_fim')
    filtro_dt_pagamento_inicio = request.GET.get('dt_pagamento_inicio')
    filtro_dt_pagamento_fim = request.GET.get('dt_pagamento_fim')
    filtro_search_cliente = request.GET.get('search_cliente', '').strip()

    # Aplicação dos filtros
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

    # Filtrando por CPF ou Nome do Cliente
    if filtro_search_cliente:
        if filtro_search_cliente.replace('.', '').replace('-', '').isdigit():
            # Se for um CPF (apenas números), buscar por CPF
            propostas = propostas.filter(cliente__nr_cpf__icontains=filtro_search_cliente.replace(".", "").replace("-", ""))
        else:
            # Se for texto, buscar pelo Nome do Cliente
            propostas = propostas.filter(cliente__nm_cliente__icontains=filtro_search_cliente)

    # Ordenação
    ordering = request.GET.get('ordering', 'nr_proposta')
    reverse = request.GET.get('reverse', 'false')

    if reverse == 'true':
        propostas = propostas.order_by(f"-{ordering}")
    else:
        propostas = propostas.order_by(ordering)

    # Paginação
    registros_por_pagina = int(request.GET.get('registros_por_pagina', 100))
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
        'filtro_search_cliente': filtro_search_cliente,
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


def verificar_cliente_api(request):
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
            data['sexo']         = cliente.sexo or ''

            # Agora, filtra endereços, contatos e profissões apenas se
            # a loja_id e operador_id forem compatíveis com as instâncias
            enderecos = []
            contatos  = []
            profissoes= []

            if loja_id and operador_id:
                end_objs = EnderecoCliente.objects.filter(
                    cliente=cliente,
                    loja_id=loja_id,
                    operador_id=operador_id
                )
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

                cont_objs = ContatoCliente.objects.filter(
                    cliente=cliente,
                    loja_id=loja_id,
                    operador_id=operador_id
                )
                contatos = [{
                    'id': c.id,
                    'telefone_fixo': c.telefone_fixo,
                    'celular': c.celular,
                    'email': c.email,
                } for c in cont_objs]

                prof_objs = ProfissaoCliente.objects.filter(
                    cliente=cliente,
                    loja_id=loja_id,
                    operador_id=operador_id
                )
                profissoes = [{
                    'id': p.id,
                    'profissao': p.profissao,
                    'cargo': p.cargo,
                    'local_trabalho': p.local_trabalho or '',
                    'data_admissao': str(p.data_admissao) if p.data_admissao else '',
                    'renda': str(p.renda or ''),
                    'outras_rendas': str(p.outras_rendas or ''),
                    'fone_lt': p.fone_lt or ''
                } for p in prof_objs]

            data['enderecos']   = enderecos
            data['contatos']    = contatos
            data['profissoes']  = profissoes
            data['reutilizar_enderecos'] = True
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

    propostas_do_periodo = Proposta.objects.filter(dt_proposta__gte=start_date, dt_proposta__lte=end_date)
    lojas_ids = propostas_do_periodo.values_list('loja', flat=True).distinct()

    lojas_elegiveis_list = []
    for loja_id in lojas_ids:
        loja = get_object_or_404(Loja, pk=loja_id)

        # Só consideramos propostas pagas (dt_pagamento preenchido)
        propostas_pagas = propostas_do_periodo.filter(loja=loja, financeira__nome_financeira__iexact="Daycoval", dt_pagamento__isnull=False)

        total_financiado = propostas_pagas.aggregate(
            Sum('vl_financiado')
        )['vl_financiado__sum'] or Decimal("0.00")

        # Propostas pagas da financeira Daycoval
        propostas_daycoval = propostas_pagas

        # Comissão pendente (retorno não pago)
        total_pendente = propostas_daycoval.filter(dt_pagamento_retorno__isnull=True).aggregate(
            total_comissao=Sum(F('vl_financiado') * Decimal("0.012"), output_field=DecimalField())
        )['total_comissao'] or Decimal("0.00")

        # Comissão paga (retorno já efetivado)
        total_comissao_paga = propostas_daycoval.filter(dt_pagamento_retorno__isnull=False).aggregate(
            total_comissao=Sum(F('vl_financiado') * Decimal("0.012"), output_field=DecimalField())
        )['total_comissao'] or Decimal("0.00")

        propostas_formatadas = []
        for proposta in propostas_daycoval:
            vl_financiado = Decimal(proposta.vl_financiado or 0)
            comissao = vl_financiado * Decimal("0.012")

            propostas_formatadas.append({
                "id": proposta.id,
                "nr_proposta": proposta.nr_proposta,
                "cliente": proposta.cliente.nm_cliente if proposta.cliente else "Sem Cliente",
                "financeira": "Daycoval",
                "dt_pagamento": proposta.dt_pagamento,
                "vl_financiado": vl_financiado,
                "comissao": comissao,
                "dt_pagamento_retorno": proposta.dt_pagamento_retorno,
            })

        # Loja é elegível se a produção total paga >= 30.000
        elegivel = total_financiado >= Decimal("30000")

        # >>> Se não for elegível, não adiciona na lista final <<<
        if not elegivel:
            continue

        lojas_elegiveis_list.append({
            'loja': loja,
            'total_pendente': total_pendente,
            'total_financiado': total_financiado,
            'total_comissao_paga': total_comissao_paga,
            'todas_propostas': propostas_formatadas,
            'elegivel': elegivel,
        })

    periodos = gerar_lista_periodos(12)
    lojas_all = Loja.objects.all()
    operadores = Operador.objects.all()
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

