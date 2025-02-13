import pandas as pd
from django_plotly_dash import DjangoDash
from dash import dcc, html, Input, Output
import plotly.express as px
from propostas.models import Proposta
from datetime import datetime, timedelta
import calendar

# Criar o Dash App
app = DjangoDash('PropostaDashboard', external_stylesheets=['/static/css/custom.css'])

# Definir o primeiro e o último dia do mês atual
hoje = datetime.today()
primeiro_dia = datetime(hoje.year, hoje.month, 1).strftime('%Y-%m-%d')
ultimo_dia = datetime(hoje.year, hoje.month, calendar.monthrange(hoje.year, hoje.month)[1]).strftime('%Y-%m-%d')

# Função para carregar os dados do banco
def carregar_dados():
    propostas = Proposta.objects.all().values(
        'nr_proposta', 'vl_financiado', 'receita', 'operador__nm_operador',
        'status__ds_status', 'dt_proposta', 'financeira__nome_financeira'
    )
    df = pd.DataFrame(propostas)
    
    if df.empty:
        df = pd.DataFrame(columns=[
            'nr_proposta', 'vl_financiado', 'receita', 'operador__nm_operador',
            'status__ds_status', 'dt_proposta', 'financeira__nome_financeira'
        ])
    
    return df

# Layout do Dashboard com Filtros Interativos
app.layout = html.Div([
    # Filtros
    html.Div([
        html.Div([
            html.Label("Selecione um Período:"),
            dcc.DatePickerRange(
                id='filtro-data',
                display_format="DD/MM/YYYY",
                start_date=primeiro_dia,
                end_date=ultimo_dia,
                style={"font-size": "6px"}
            )
        ], className="col-md-3"),  # Tamanho da fonte do filtro de data

        html.Div([
            html.Label("Selecione um Operador:"),
            dcc.Dropdown(
                id='filtro-operador',
                options=[],  # Será preenchido dinamicamente
                placeholder="Todos os Operadores",
                multi=True
            )
        ], className="col-md-3"),

        html.Div([
            html.Label("Selecione uma Financeira:"),
            dcc.Dropdown(
                id='filtro-financeira',
                options=[],  # Será preenchido dinamicamente
                placeholder="Todas as Financeiras",
                multi=True
            )
        ], className="col-md-3"),

        html.Div([
            html.Label("Selecione um Status:"),
            dcc.Dropdown(
                id='filtro-status',
                options=[],  # Será preenchido dinamicamente
                placeholder="Todos os Status",
                multi=True
            )
        ], className="col-md-3"),
    ], className="row mb-3", style={"justify-content": "space-around"}),

    # Indicadores principais
    html.Div([
        html.Div([
            html.P("Produção Total"),
            html.H3(id="total-producao", style={"font-size": "2rem", "color": "#0B2559"}),
        ], className="card-dash col-md-4 text-center"),
        
        html.Div([
            html.P("Total de Propostas"),
            html.H3(id="total-propostas", style={"font-size": "2rem", "color": "#0B2559"}),
        ], className="card-dash col-md-4 text-center"),

        html.Div([
            html.P("Projeção de Receita"),
            html.H3(id="projecao-receita", style={"font-size": "2rem", "color": "#0B2559"}),
        ], className="card-dash col-md-4 text-center"),
    ], className="row mb-4", style={"justify-content": "space-between"}),

    # Gráficos - Produção por Operador e Produção por Financeira
    html.Div([
        html.Div([
            dcc.Graph(id="grafico-operador")
        ], className="card-dash col-md-6"),

        html.Div([
            dcc.Graph(id="grafico-financeira")
        ], className="card-dash col-md-6"),
    ], className="row mt-4", style={"justify-content": "space-between"}),

])

# Callback para Atualizar os Opções dos Filtros
@app.callback(
    [Output('filtro-operador', 'options'),
     Output('filtro-financeira', 'options'),
     Output('filtro-status', 'options')],
    Input('filtro-data', 'start_date')
)
def atualizar_opcoes_filtros(start_date):
    df = carregar_dados()

    return [
        [{'label': op, 'value': op} for op in df['operador__nm_operador'].unique()],
        [{'label': fin, 'value': fin} for fin in df['financeira__nome_financeira'].unique()],
        [{'label': st, 'value': st} for st in df['status__ds_status'].unique()]
    ]

# Callback para atualizar os dados e gráficos dinamicamente
@app.callback(
    [Output("total-producao", "children"),
     Output("total-propostas", "children"),
     Output("projecao-receita", "children"),
     Output("grafico-operador", "figure"),
     Output("grafico-financeira", "figure"),
],
    [Input("filtro-data", "start_date"),
     Input("filtro-data", "end_date"),
     Input("filtro-operador", "value"),
     Input("filtro-financeira", "value"),
     Input("filtro-status", "value")]
)
def atualizar_graficos(start_date, end_date, operadores, financeiras, status):
    df = carregar_dados()

    # Filtrar por Data
    df["dt_proposta"] = pd.to_datetime(df["dt_proposta"])
    # Criar uma nova coluna com o formato "Mês/Ano"
    df["mes_ano"] = df["dt_proposta"].dt.strftime('%Y-%m')
    df = df[(df["dt_proposta"] >= pd.to_datetime(start_date)) & (df["dt_proposta"] <= pd.to_datetime(end_date))]

    # Aplicar Filtros
    if operadores:
        df = df[df["operador__nm_operador"].isin(operadores)]
    if financeiras:
        df = df[df["financeira__nome_financeira"].isin(financeiras)]
    if status:
        df = df[df["status__ds_status"].isin(status)]

    # Atualizar Indicadores
    total_producao = f"R$ {df['vl_financiado'].sum():,.2f}"
    total_propostas = f"{len(df)}"
    projecao_receita = f"R$ {df['receita'].sum():,.2f}"

    # Gráfico de Produção por Operador (Ordenado do maior para o menor)
    df_operador = df.groupby('operador__nm_operador')['vl_financiado'].sum().reset_index()
    df_operador = df_operador.sort_values(by="vl_financiado", ascending=True)

    fig_operador = px.bar(
        df_operador,
        y='operador__nm_operador',
        x='vl_financiado',
        title="Produção por Operador",
        labels={
            'operador__nm_operador': 'Operador',  # Título do eixo X
            'vl_financiado': 'Valor Financiado R$'},
        text_auto=True
    )
    # Personalizações
    fig_operador.update_traces(
        texttemplate='%{x:,.2f}',  # Define os rótulos com duas casas decimais, sem abreviação
        textposition='inside'    # Garante que os rótulos fiquem fora das barras
    )
    
    # Remove os valores do eixo Y (mantendo apenas os rótulos dentro das barras)
    fig_operador.update_layout(
        xaxis=dict(showticklabels=False),  # Esconde os valores do eixo Y
        yaxis_title="Operador",
        xaxis_title="",  # Remove o título do eixo Y
        plot_bgcolor='rgba(0,0,0,0)',  # Remove o fundo do gráfico
        paper_bgcolor='rgba(0,0,0,0)'   # Remove o fundo da área externa do gráfico        
    )

    # Gráfico de Produção por Financeira
    fig_financeira = px.pie(
        df.groupby('financeira__nome_financeira')['vl_financiado'].sum().reset_index(),
        names='financeira__nome_financeira',
        values='vl_financiado',
        title="Produção por Financeira",
        hole=0.4
    )


    return total_producao, total_propostas, projecao_receita, fig_operador, fig_financeira
