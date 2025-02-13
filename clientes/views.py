from django.shortcuts import render, redirect, get_object_or_404
from .models import Cliente, EnderecoCliente, ProfissaoCliente, ContatoCliente
from .forms import ClienteForm, EnderecoClienteForm, ProfissaoClienteForm, ContatoClienteForm
from rest_framework.viewsets import ModelViewSet
from .serializers import ClienteSerializer


# ---------------------- VIEWSET PARA API ---------------------- #
class ClienteViewSet(ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer


# ---------------------- CRIAR CLIENTE ---------------------- #
def cliente_create(request):
    if request.method == "POST":
        cliente_form = ClienteForm(request.POST)
        endereco_form = EnderecoClienteForm(request.POST)
        profissao_form = ProfissaoClienteForm(request.POST)
        contato_form = ContatoClienteForm(request.POST)

        if cliente_form.is_valid() and endereco_form.is_valid() and profissao_form.is_valid() and contato_form.is_valid():
            # Salva o cliente
            cliente = cliente_form.save()

            # Salva o endereço vinculado ao cliente
            endereco = endereco_form.save(commit=False)
            endereco.cliente = cliente
            endereco.save()

            # Salva a profissão vinculada ao cliente
            profissao = profissao_form.save(commit=False)
            profissao.cliente = cliente
            profissao.save()

            # Salva o contato vinculado ao cliente
            contato = contato_form.save(commit=False)
            contato.cliente = cliente
            contato.save()

            return redirect('clientes:cliente_list')

    else:
        cliente_form = ClienteForm()
        endereco_form = EnderecoClienteForm()
        profissao_form = ProfissaoClienteForm()
        contato_form = ContatoClienteForm()

    return render(request, 'clientes/cliente_form.html', {
        'cliente_form': cliente_form,
        'endereco_form': endereco_form,
        'profissao_form': profissao_form,
        'contato_form': contato_form
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
    endereco = get_object_or_404(EnderecoCliente, cliente=cliente)
    profissao = get_object_or_404(ProfissaoCliente, cliente=cliente)
    contato = get_object_or_404(ContatoCliente, cliente=cliente)

    if request.method == "POST":
        cliente_form = ClienteForm(request.POST, instance=cliente)
        endereco_form = EnderecoClienteForm(request.POST, instance=endereco)
        profissao_form = ProfissaoClienteForm(request.POST, instance=profissao)
        contato_form = ContatoClienteForm(request.POST, instance=contato)

        if cliente_form.is_valid() and endereco_form.is_valid() and profissao_form.is_valid() and contato_form.is_valid():
            cliente_form.save()
            endereco_form.save()
            profissao_form.save()
            contato_form.save()
            return redirect('clientes:cliente_detail', pk=cliente.pk)

    else:
        cliente_form = ClienteForm(instance=cliente)
        endereco_form = EnderecoClienteForm(instance=endereco)
        profissao_form = ProfissaoClienteForm(instance=profissao)
        contato_form = ContatoClienteForm(instance=contato)

    return render(request, 'clientes/cliente_form.html', {
        'cliente_form': cliente_form,
        'endereco_form': endereco_form,
        'profissao_form': profissao_form,
        'contato_form': contato_form
    })
