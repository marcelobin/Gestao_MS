from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from financeiras.models import Modalidade, Segmento
from usuarios.models import Perfil, Filial
from propostas.models import StatusProposta

from .forms import (
    ModalidadeForm, SegmentoForm, PerfilForm, FilialForm, StatusPropostaForm
)

class ConfiguracaoView(LoginRequiredMixin, TemplateView):
    template_name = 'configuracao/configuracao.html'

# ----------------------------
# Modalidade
# ----------------------------
class ModalidadeListView(LoginRequiredMixin, ListView):
    model = Modalidade
    template_name = 'configuracao/objeto_list.html'
    context_object_name = 'objetos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Passa para o template o plural e o nome do modelo
        context['titulo_plural'] = self.model._meta.verbose_name_plural
        context['nome_modelo'] = self.model._meta.model_name
        nome_modelo_lower = self.model._meta.model_name.lower()
        context['rota_create'] = f"configuracao:{nome_modelo_lower}_create"
        context['rota_update'] = f"configuracao:{nome_modelo_lower}_update"
        context['rota_delete'] = f"configuracao:{nome_modelo_lower}_delete"  
        context['rota_list'] = f"configuracao:{nome_modelo_lower}_list"       
        return context

class ModalidadeCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Modalidade
    form_class = ModalidadeForm
    template_name = 'configuracao/objeto_form.html'
    success_url = reverse_lazy('configuracao:modalidade_list')
    permission_required = 'financeiras.add_modalidade'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_plural'] = self.model._meta.verbose_name_plural
        context['nome_modelo'] = self.model._meta.model_name
        nome_modelo_lower = self.model._meta.model_name.lower()
        context['rota_create'] = f"configuracao:{nome_modelo_lower}_create"
        context['rota_update'] = f"configuracao:{nome_modelo_lower}_update"
        context['rota_delete'] = f"configuracao:{nome_modelo_lower}_delete"
        context['rota_list'] = f"configuracao:{nome_modelo_lower}_list"       
        return context
    

class ModalidadeUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Modalidade
    form_class = ModalidadeForm
    template_name = 'configuracao/objeto_form.html'
    success_url = reverse_lazy('configuracao:modalidade_list')
    permission_required = 'financeiras.change_modalidade'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_plural'] = self.model._meta.verbose_name_plural
        context['nome_modelo'] = self.model._meta.model_name
        nome_modelo_lower = self.model._meta.model_name.lower()
        context['rota_create'] = f"configuracao:{nome_modelo_lower}_create"
        context['rota_update'] = f"configuracao:{nome_modelo_lower}_update"
        context['rota_delete'] = f"configuracao:{nome_modelo_lower}_delete"
        context['rota_list'] = f"configuracao:{nome_modelo_lower}_list"       
        return context    

class ModalidadeDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Modalidade
    template_name = 'configuracao/objeto_confirm_delete.html'
    success_url = reverse_lazy('configuracao:modalidade_list')
    permission_required = 'financeiras.delete_modalidade'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_plural'] = self.model._meta.verbose_name_plural
        context['nome_modelo'] = self.model._meta.model_name
        nome_modelo_lower = self.model._meta.model_name.lower()
        context['rota_create'] = f"configuracao:{nome_modelo_lower}_create"
        context['rota_update'] = f"configuracao:{nome_modelo_lower}_update"
        context['rota_delete'] = f"configuracao:{nome_modelo_lower}_delete"
        context['rota_list'] = f"configuracao:{nome_modelo_lower}_list"       
        return context    


# ----------------------------
# Segmento
# ----------------------------
class SegmentoListView(LoginRequiredMixin, ListView):
    model = Segmento
    template_name = 'configuracao/objeto_list.html'
    context_object_name = 'objetos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_plural'] = self.model._meta.verbose_name_plural
        context['nome_modelo'] = self.model._meta.model_name
        nome_modelo_lower = self.model._meta.model_name.lower()
        context['rota_create'] = f"configuracao:{nome_modelo_lower}_create"
        context['rota_update'] = f"configuracao:{nome_modelo_lower}_update"
        context['rota_delete'] = f"configuracao:{nome_modelo_lower}_delete"
        context['rota_list'] = f"configuracao:{nome_modelo_lower}_list"       
        
        return context

class SegmentoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Segmento
    form_class = SegmentoForm
    template_name = 'configuracao/objeto_form.html'
    success_url = reverse_lazy('configuracao:segmento_list')
    permission_required = 'financeiras.add_segmento'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_plural'] = self.model._meta.verbose_name_plural
        context['nome_modelo'] = self.model._meta.model_name
        nome_modelo_lower = self.model._meta.model_name.lower()
        context['rota_create'] = f"configuracao:{nome_modelo_lower}_create"
        context['rota_update'] = f"configuracao:{nome_modelo_lower}_update"
        context['rota_delete'] = f"configuracao:{nome_modelo_lower}_delete"
        context['rota_list'] = f"configuracao:{nome_modelo_lower}_list"       
        return context    

class SegmentoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Segmento
    form_class = SegmentoForm
    template_name = 'configuracao/objeto_form.html'
    success_url = reverse_lazy('configuracao:segmento_list')
    permission_required = 'financeiras.change_segmento'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_plural'] = self.model._meta.verbose_name_plural
        context['nome_modelo'] = self.model._meta.model_name
        nome_modelo_lower = self.model._meta.model_name.lower()
        context['rota_create'] = f"configuracao:{nome_modelo_lower}_create"
        context['rota_update'] = f"configuracao:{nome_modelo_lower}_update"
        context['rota_delete'] = f"configuracao:{nome_modelo_lower}_delete"
        context['rota_list'] = f"configuracao:{nome_modelo_lower}_list"       
        return context    

class SegmentoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Segmento
    template_name = 'configuracao/objeto_confirm_delete.html'
    success_url = reverse_lazy('configuracao:segmento_list')
    permission_required = 'financeiras.delete_segmento'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_plural'] = self.model._meta.verbose_name_plural
        context['nome_modelo'] = self.model._meta.model_name
        nome_modelo_lower = self.model._meta.model_name.lower()
        context['rota_create'] = f"configuracao:{nome_modelo_lower}_create"
        context['rota_update'] = f"configuracao:{nome_modelo_lower}_update"
        context['rota_delete'] = f"configuracao:{nome_modelo_lower}_delete"
        context['rota_list'] = f"configuracao:{nome_modelo_lower}_list"       
        return context    


# ----------------------------
# Perfil
# ----------------------------
class PerfilListView(LoginRequiredMixin, ListView):
    model = Perfil
    template_name = 'configuracao/objeto_list.html'
    context_object_name = 'objetos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_plural'] = self.model._meta.verbose_name_plural
        context['nome_modelo'] = self.model._meta.model_name
        nome_modelo_lower = self.model._meta.model_name.lower()
        context['rota_create'] = f"configuracao:{nome_modelo_lower}_create"
        context['rota_update'] = f"configuracao:{nome_modelo_lower}_update"
        context['rota_delete'] = f"configuracao:{nome_modelo_lower}_delete"    
        context['rota_list'] = f"configuracao:{nome_modelo_lower}_list"       
            
        return context

class PerfilCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Perfil
    form_class = PerfilForm
    template_name = 'configuracao/objeto_form.html'
    success_url = reverse_lazy('configuracao:perfil_list')
    permission_required = 'usuarios.add_perfil'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_plural'] = self.model._meta.verbose_name_plural
        context['nome_modelo'] = self.model._meta.model_name
        nome_modelo_lower = self.model._meta.model_name.lower()
        context['rota_create'] = f"configuracao:{nome_modelo_lower}_create"
        context['rota_update'] = f"configuracao:{nome_modelo_lower}_update"
        context['rota_delete'] = f"configuracao:{nome_modelo_lower}_delete"
        context['rota_list'] = f"configuracao:{nome_modelo_lower}_list"       
        return context    

class PerfilUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Perfil
    form_class = PerfilForm
    template_name = 'configuracao/objeto_form.html'
    success_url = reverse_lazy('configuracao:perfil_list')
    permission_required = 'usuarios.change_perfil'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_plural'] = self.model._meta.verbose_name_plural
        context['nome_modelo'] = self.model._meta.model_name
        nome_modelo_lower = self.model._meta.model_name.lower()
        context['rota_create'] = f"configuracao:{nome_modelo_lower}_create"
        context['rota_update'] = f"configuracao:{nome_modelo_lower}_update"
        context['rota_delete'] = f"configuracao:{nome_modelo_lower}_delete"
        context['rota_list'] = f"configuracao:{nome_modelo_lower}_list"       
        return context    

class PerfilDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Perfil
    template_name = 'configuracao/objeto_confirm_delete.html'
    success_url = reverse_lazy('configuracao:perfil_list')
    permission_required = 'usuarios.delete_perfil'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_plural'] = self.model._meta.verbose_name_plural
        context['nome_modelo'] = self.model._meta.model_name
        nome_modelo_lower = self.model._meta.model_name.lower()
        context['rota_create'] = f"configuracao:{nome_modelo_lower}_create"
        context['rota_update'] = f"configuracao:{nome_modelo_lower}_update"
        context['rota_delete'] = f"configuracao:{nome_modelo_lower}_delete"
        context['rota_list'] = f"configuracao:{nome_modelo_lower}_list"       
        return context    


# ----------------------------
# Filial
# ----------------------------
class FilialListView(LoginRequiredMixin, ListView):
    model = Filial
    template_name = 'configuracao/objeto_list.html'
    context_object_name = 'objetos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_plural'] = self.model._meta.verbose_name_plural
        context['nome_modelo'] = self.model._meta.model_name
        nome_modelo_lower = self.model._meta.model_name.lower()
        context['rota_create'] = f"configuracao:{nome_modelo_lower}_create"
        context['rota_update'] = f"configuracao:{nome_modelo_lower}_update"
        context['rota_delete'] = f"configuracao:{nome_modelo_lower}_delete"        
        context['rota_list'] = f"configuracao:{nome_modelo_lower}_list"       
        
        return context

class FilialCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Filial
    form_class = FilialForm
    template_name = 'configuracao/objeto_form.html'
    success_url = reverse_lazy('configuracao:filial_list')
    permission_required = 'usuarios.add_filial'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_plural'] = self.model._meta.verbose_name_plural
        context['nome_modelo'] = self.model._meta.model_name
        nome_modelo_lower = self.model._meta.model_name.lower()
        context['rota_create'] = f"configuracao:{nome_modelo_lower}_create"
        context['rota_update'] = f"configuracao:{nome_modelo_lower}_update"
        context['rota_delete'] = f"configuracao:{nome_modelo_lower}_delete"
        context['rota_list'] = f"configuracao:{nome_modelo_lower}_list"       
        return context    

class FilialUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Filial
    form_class = FilialForm
    template_name = 'configuracao/objeto_form.html'
    success_url = reverse_lazy('configuracao:filial_list')
    permission_required = 'usuarios.change_filial'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_plural'] = self.model._meta.verbose_name_plural
        context['nome_modelo'] = self.model._meta.model_name
        nome_modelo_lower = self.model._meta.model_name.lower()
        context['rota_create'] = f"configuracao:{nome_modelo_lower}_create"
        context['rota_update'] = f"configuracao:{nome_modelo_lower}_update"
        context['rota_delete'] = f"configuracao:{nome_modelo_lower}_delete"
        context['rota_list'] = f"configuracao:{nome_modelo_lower}_list"       
        return context    

class FilialDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Filial
    template_name = 'configuracao/objeto_confirm_delete.html'
    success_url = reverse_lazy('configuracao:filial_list')
    permission_required = 'usuarios.delete_filial'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_plural'] = self.model._meta.verbose_name_plural
        context['nome_modelo'] = self.model._meta.model_name
        nome_modelo_lower = self.model._meta.model_name.lower()
        context['rota_create'] = f"configuracao:{nome_modelo_lower}_create"
        context['rota_update'] = f"configuracao:{nome_modelo_lower}_update"
        context['rota_delete'] = f"configuracao:{nome_modelo_lower}_delete"
        context['rota_list'] = f"configuracao:{nome_modelo_lower}_list"       
        return context    


# ----------------------------
# StatusProposta
# ----------------------------

class StatusPropostaListView(LoginRequiredMixin, ListView):
    model = StatusProposta
    template_name = 'configuracao/objeto_list.html'
    context_object_name = 'objetos'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_plural'] = self.model._meta.verbose_name_plural
        context['nome_modelo'] = self.model._meta.model_name
        nome_modelo_lower = self.model._meta.model_name.lower()
        context['rota_create'] = f"configuracao:{nome_modelo_lower}_create"
        context['rota_update'] = f"configuracao:{nome_modelo_lower}_update"
        context['rota_delete'] = f"configuracao:{nome_modelo_lower}_delete"
        context['rota_list'] = f"configuracao:{nome_modelo_lower}_list"       
        return context
    
class StatusPropostaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = StatusProposta
    form_class = StatusPropostaForm
    template_name = 'configuracao/objeto_form.html'
    success_url = reverse_lazy('configuracao:statusproposta_list')  # Adicione o underline correto
    permission_required = 'propostas.add_statusproposta'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_plural'] = self.model._meta.verbose_name_plural
        context['nome_modelo'] = self.model._meta.model_name
        nome_modelo_lower = self.model._meta.model_name.lower()
        context['rota_create'] = f"configuracao:{nome_modelo_lower}_create"
        context['rota_update'] = f"configuracao:{nome_modelo_lower}_update"
        context['rota_delete'] = f"configuracao:{nome_modelo_lower}_delete"
        context['rota_list'] = f"configuracao:{nome_modelo_lower}_list"       
        return context
    
class StatusPropostaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = StatusProposta
    form_class = StatusPropostaForm
    template_name = 'configuracao/objeto_form.html'
    success_url = reverse_lazy('configuracao:statusproposta_list')
    permission_required = 'propostas.change_statusproposta'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_plural'] = self.model._meta.verbose_name_plural
        context['nome_modelo'] = self.model._meta.model_name
        nome_modelo_lower = self.model._meta.model_name.lower()
        context['rota_create'] = f"configuracao:{nome_modelo_lower}_create"
        context['rota_update'] = f"configuracao:{nome_modelo_lower}_update"
        context['rota_delete'] = f"configuracao:{nome_modelo_lower}_delete"
        context['rota_list'] = f"configuracao:{nome_modelo_lower}_list"       
        return context
    
class StatusPropostaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = StatusProposta
    template_name = 'configuracao/objeto_confirm_delete.html'
    success_url = reverse_lazy('configuracao:statusproposta_list')
    permission_required = 'propostas.delete_statusproposta'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_plural'] = self.model._meta.verbose_name_plural
        context['nome_modelo'] = self.model._meta.model_name
        nome_modelo_lower = self.model._meta.model_name.lower()
        context['rota_create'] = f"configuracao:{nome_modelo_lower}_create"
        context['rota_update'] = f"configuracao:{nome_modelo_lower}_update"
        context['rota_delete'] = f"configuracao:{nome_modelo_lower}_delete"
        context['rota_list'] = f"configuracao:{nome_modelo_lower}_list"
        return context
    


