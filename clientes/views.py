from django.shortcuts import render, redirect, get_object_or_404
from .models import Cliente, EnderecoCliente, ProfissaoCliente, ContatoCliente
from .forms import ClienteForm, EnderecoClienteForm, ProfissaoClienteForm, ContatoClienteForm
from rest_framework.viewsets import ModelViewSet
from .serializers import ClienteSerializer

# ---------------------- VIEWSET PARA API ---------------------- #
class ClienteViewSet(ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer


# ---------------------- CRIAR OU ATUALIZAR CLIENTE ---------------------- #
def cliente_create_or_update(request):
    if request.method == "POST":
        cpf = request.POST.get("nr_cpf", "").replace(".", "").replace("-", "")  # Remove formatação do CPF
        loja_id = request.POST.get("loja")  # Captura a loja do formulário
        operador_id = request.POST.get("operador")  # Captura o operador do formulário
        
        cliente = Cliente.objects.filter(nr_cpf=cpf).first()  # Busca o cliente

        # Busca registros existentes com base no unique_together
        endereco = EnderecoCliente.objects.filter(cliente=cliente, loja_id=loja_id, operador_id=operador_id).first()
        profissao = ProfissaoCliente.objects.filter(cliente=cliente, loja_id=loja_id, operador_id=operador_id).first()
        contato = ContatoCliente.objects.filter(cliente=cliente, loja_id=loja_id, operador_id=operador_id).first()

        # Se já existe um cliente na loja e operador, atualiza. Senão, cria um novo.
        cliente_form = ClienteForm(request.POST, instance=cliente)
        endereco_form = EnderecoClienteForm(request.POST, instance=endereco if endereco else None)
        profissao_form = ProfissaoClienteForm(request.POST, instance=profissao if profissao else None)
        contato_form = ContatoClienteForm(request.POST, instance=contato if contato else None)

        if cliente_form.is_valid() and endereco_form.is_valid() and profissao_form.is_valid() and contato_form.is_valid():
            cliente = cliente_form.save()  # Salva ou atualiza cliente

            # Atualiza ou cria um novo registro de endereço, profissão e contato
            endereco_form.instance.cliente = cliente
            endereco_form.save()

            profissao_form.instance.cliente = cliente
            profissao_form.save()

            contato_form.instance.cliente = cliente
            contato_form.save()

            return redirect("clientes:cliente_list")  # Redireciona após sucesso

    else:
        cliente_form = ClienteForm()
        endereco_form = EnderecoClienteForm()
        profissao_form = ProfissaoClienteForm()
        contato_form = ContatoClienteForm()

    return render(request, "clientes/cliente_form.html", {
        "cliente_form": cliente_form,
        "endereco_form": endereco_form,
        "profissao_form": profissao_form,
        "contato_form": contato_form,
    })


# ---------------------- LISTAR CLIENTES ---------------------- #
def cliente_list(request):
    clientes = Cliente.objects.all()
    return render(request, 'clientes/cliente_list.html', {'clientes': clientes})


# ---------------------- DETALHES DO CLIENTE ---------------------- #
def cliente_detail(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    enderecos = EnderecoCliente.objects.filter(cliente=cliente)
    profissoes = ProfissaoCliente.objects.filter(cliente=cliente)
    contatos = ContatoCliente.objects.filter(cliente=cliente)

    return render(request, 'clientes/cliente_detail.html', {
        'cliente': cliente,
        'enderecos': enderecos,
        'profissoes': profissoes,
        'contatos': contatos,
    })


# ---------------------- ATUALIZAR CLIENTE ---------------------- #
def cliente_update(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)

    # Pega a loja e operador enviados no formulário para checar duplicatas
    loja_id = request.POST.get("loja")
    operador_id = request.POST.get("operador")

    endereco = EnderecoCliente.objects.filter(cliente=cliente, loja_id=loja_id, operador_id=operador_id).first()
    profissao = ProfissaoCliente.objects.filter(cliente=cliente, loja_id=loja_id, operador_id=operador_id).first()
    contato = ContatoCliente.objects.filter(cliente=cliente, loja_id=loja_id, operador_id=operador_id).first()

    if request.method == "POST":
        cliente_form = ClienteForm(request.POST, instance=cliente)
        endereco_form = EnderecoClienteForm(request.POST, instance=endereco if endereco else None)
        profissao_form = ProfissaoClienteForm(request.POST, instance=profissao if profissao else None)
        contato_form = ContatoClienteForm(request.POST, instance=contato if contato else None)

        if cliente_form.is_valid() and endereco_form.is_valid() and profissao_form.is_valid() and contato_form.is_valid():
            cliente_form.save()
            endereco_form.save()
            profissao_form.save()
            contato_form.save()
            return redirect('clientes:cliente_detail', pk=cliente.pk)

    else:
        cliente_form = ClienteForm(instance=cliente)
        endereco_form = EnderecoClienteForm(instance=endereco if endereco else None)
        profissao_form = ProfissaoClienteForm(instance=profissao if profissao else None)
        contato_form = ContatoClienteForm(instance=contato if contato else None)

    return render(request, 'clientes/cliente_form.html', {
        'cliente_form': cliente_form,
        'endereco_form': endereco_form,
        'profissao_form': profissao_form,
        'contato_form': contato_form
    })
