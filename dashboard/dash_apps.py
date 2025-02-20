import pandas as pd
from django_plotly_dash import DjangoDash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
from propostas.models import Proposta
from datetime import datetime, timedelta
import calendar

app = DjangoDash('PropostaDashboard', external_stylesheets=['/static/css/custom.css'])

def carregar_dados():
    propostas = Proposta.objects.all().values(
        'nr_proposta', 'vl_financiado', 'receita', 'operador__nm_operador',
        'status__ds_status', 'dt_proposta', 'financeira__nome_financeira', 'loja__nm_fantasia'
    )
    df = pd.DataFrame(propostas)
    if df.empty:
        df = pd.DataFrame(columns=[
            'nr_proposta', 'vl_financiado', 'receita', 'operador__nm_operador',
            'status__ds_status', 'dt_proposta', 'financeira__nome_financeira', 'loja__nm_fantasia'
        ])
    df["dt_proposta"] = pd.to_datetime(df["dt_proposta"], errors="coerce")
    return df

def formatar_nome(nome):
    partes = nome.split()
    if len(partes) > 1:
        return f"{partes[0]} {partes[-1]}"
    return nome

app.layout = html.Div([
    # ------------------------------------------------------------
    # Filtros (todos em uma única linha)
    # ------------------------------------------------------------
    html.Div([
        html.Div([
            html.Label("Período:"),
            dcc.DatePickerRange(
                id='filtro-data',
                display_format="DD/MM/YYYY",
                start_date=datetime.today().replace(day=1).strftime('%Y-%m-%d'),
                end_date=datetime.today().strftime('%Y-%m-%d'),
                style={"font-size": "14px"}
            )
        ], className="col-md-3"),

        html.Div([
            html.Label("Operador:"),
            dcc.Dropdown(
                id='filtro-operador',
                options=[],
                placeholder="Todos os Operadores",
                multi=True
            )
        ], className="col-md-2"),

        html.Div([
            html.Label("Loja:"),
            dcc.Dropdown(
                id='filtro-loja',
                options=[],
                placeholder="Todas as Lojas",
                multi=True
            )
        ], className="col-md-2"),

        html.Div([
            html.Label("Financeira:"),
            dcc.Dropdown(
                id='filtro-financeira',
                options=[],
                placeholder="Todas as Financeiras",
                multi=True
            )
        ], className="col-md-2"),

        html.Div([
            html.Label("Status:"),
            dcc.Dropdown(
                id='filtro-status',
                options=[],
                placeholder="Todos os Status",
                multi=True
            )
        ], className="col-md-2"),
    ], className="row mb-3"),
    html.Hr(),

# ------------------------------------------------------------
# KPIs (uma linha, 4 colunas) dentro de cards estilizados
# ------------------------------------------------------------
    html.Div([
        # Produção Total (Paga)
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Produção Total"),
                    html.H3(id="total-producao", style={"color": "#0B2559"})
                ]),
                className="kpi-card"
            ), width=3
        ),

        # Total de Propostas Pagas
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Total de Propostas Pagas"),
                    html.H3(id="total-propostas", style={"color": "#0B2559"})
                ]),
                className="kpi-card"
            ), width=3
        ),

        # Receita Prevista (Paga)
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Receita Prevista"),
                    html.H3(id="projecao-receita", style={"color": "#0B2559"})
                ]),
                className="kpi-card"
            ), width=3
        ),

        # Valor Médio Financiado (Paga)
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Valor Médio Financiado"),
                    html.H3(id="valor-medio", style={"color": "#0B2559"})
                ]),
                className="kpi-card"
            ), width=3
        ),
    ], className="row g-3 mb-3"),  # "g-3" adiciona espaçamento entre as colunas

    # ------------------------------------------------------------
    # Gráficos de barras (Operador / Loja) - mesma linha
    # ------------------------------------------------------------
    html.Div([
        html.Div([
            dbc.Card([
            dcc.Graph(id="grafico-operador", animate=True)
            ]),
        ], className="col-md-6"),
        html.Div([
            dbc.Card([
            dcc.Graph(id="grafico-loja", animate=True)
            ]),
        ], className="col-md-6"),
    ], className="row g-3 mb-3"),

    # ------------------------------------------------------------
    # Gráfico de Tendência (linha) - abaixo, largura total
    # ------------------------------------------------------------
    html.Div([
        dbc.Card([
        dcc.Graph(id="grafico-tempo", animate=True)
        ]),
    ], className="col-md-12"),
])

@app.callback(
    [
        Output('filtro-operador', 'options'),
        Output('filtro-financeira', 'options'),
        Output('filtro-loja', 'options'),
        Output('filtro-status', 'options')
    ],
    Input('filtro-data', 'start_date')
)
def atualizar_opcoes_filtros(start_date):
    df = carregar_dados()
    opcoes_operador = [
        {'label': op, 'value': op}
        for op in sorted(df['operador__nm_operador'].dropna().unique())
    ]
    opcoes_financeira = [
        {'label': fin, 'value': fin}
        for fin in sorted(df['financeira__nome_financeira'].dropna().unique())
    ]
    opcoes_loja = [
        {'label': loja, 'value': loja}
        for loja in sorted(df['loja__nm_fantasia'].dropna().unique())
    ]
    opcoes_status = [
        {'label': st, 'value': st}
        for st in sorted(df['status__ds_status'].dropna().unique())
    ]
    return opcoes_operador, opcoes_financeira, opcoes_loja, opcoes_status

@app.callback(
    [
        Output("total-producao", "children"),
        Output("total-propostas", "children"),
        Output("projecao-receita", "children"),
        Output("valor-medio", "children"),
        Output("grafico-operador", "figure"),
        Output("grafico-loja", "figure"),
        Output("grafico-tempo", "figure"),
    ],
    [
        Input("filtro-data", "start_date"),
        Input("filtro-data", "end_date"),
        Input("filtro-operador", "value"),
        Input("filtro-financeira", "value"),
        Input("filtro-loja", "value"),
        Input("filtro-status", "value"),
    ]
)
def atualizar_dashboard(start_date, end_date, operadores, financeiras, lojas, status):
    # Carrega dados
    df_full = carregar_dados()

    # Filtros
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df_filtro = df_full[
        (df_full["dt_proposta"] >= start_date) &
        (df_full["dt_proposta"] <= end_date)
    ]
    if operadores:
        df_filtro = df_filtro[df_filtro["operador__nm_operador"].isin(operadores)]
    if financeiras:
        df_filtro = df_filtro[df_filtro["financeira__nome_financeira"].isin(financeiras)]
    if lojas:
        df_filtro = df_filtro[df_filtro["loja__nm_fantasia"].isin(lojas)]
    if status:
        df_filtro = df_filtro[df_filtro["status__ds_status"].isin(status)]

    # Considerar apenas as propostas com status Paga
    df_paga = df_filtro[df_filtro["status__ds_status"].str.lower() == "paga"]

    # KPIs
    total_producao_val = df_paga['vl_financiado'].sum()
    receita_total_val = df_paga['receita'].sum()
    total_propostas_pagas_val = len(df_paga)
    valor_medio_val = (
        total_producao_val / total_propostas_pagas_val
        if total_propostas_pagas_val > 0 else 0
    )

    total_producao = f"R$ {total_producao_val:,.2f}"
    total_propostas = f"{total_propostas_pagas_val}"
    projecao_receita = f"R$ {receita_total_val:,.2f}"
    valor_medio = f"R$ {valor_medio_val:,.2f}"

    # Gráfico de Produção por Operador
    df_operador = df_paga.groupby('operador__nm_operador')['vl_financiado'].sum().reset_index()
    df_operador.rename(columns={"operador__nm_operador": "Operador", "vl_financiado": "Valor Financiado"}, inplace=True)
    if df_operador.empty:
        df_operador = pd.DataFrame({"Operador": ["Sem Dados"], "Valor Financiado": [0]})
    df_operador["Operador"] = df_operador["Operador"].apply(formatar_nome)

    fig_operador = px.bar(
        df_operador,
        x="Valor Financiado",
        y="Operador",
        orientation="h",
        title="Produção por Operador (Paga)",
        text="Valor Financiado",
        labels={"Valor Financiado": "Valor Financiado (R$)", "Operador": "Operador"}
    )
    fig_operador.update_traces(texttemplate='%{x:,.2f}', textposition='inside')
    fig_operador.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        transition=dict(
            duration=500,   # milissegundos
            easing="cubic-in-out")        
    )

    # Gráfico de Produção por Loja
    df_loja = df_paga.groupby('loja__nm_fantasia')['vl_financiado'].sum().reset_index()
    df_loja.rename(columns={"loja__nm_fantasia": "Loja", "vl_financiado": "Valor Financiado"}, inplace=True)
    if df_loja.empty:
        df_loja = pd.DataFrame({"Loja": ["Sem Dados"], "Valor Financiado": [0]})

    fig_loja = px.bar(
        df_loja,
        x="Valor Financiado",
        y="Loja",
        orientation="h",
        title="Produção por Loja (Paga)",
        text="Valor Financiado",
        labels={"Valor Financiado": "Valor Financiado (R$)", "Loja": "Loja"}
    )
    fig_loja.update_traces(texttemplate='%{x:,.2f}', textposition='inside')
    fig_loja.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        transition=dict(
            duration=500,   # milissegundos
            easing="cubic-in-out")            
    )

    # Gráfico de Tendência (últimos 12 meses, Paga)
    hoje = datetime.today()
    doze_meses_atras = hoje.replace(day=1) - timedelta(days=365)
    df_paga_12m = df_paga[df_paga["dt_proposta"] >= doze_meses_atras]

    df_paga_12m["mes_ano_label"] = df_paga_12m["dt_proposta"].dt.strftime('%m/%Y')
    df_paga_12m["ano_mes"] = df_paga_12m["dt_proposta"].dt.strftime('%Y-%m')

    df_time_grouped = (
        df_paga_12m
        .groupby(["ano_mes","mes_ano_label"])["vl_financiado"]
        .sum()
        .reset_index()
        .sort_values("ano_mes")
    )

    fig_tempo = px.line(
        df_time_grouped,
        x="mes_ano_label",
        y="vl_financiado",
        title="Tendência de Produção (Últimos 12 meses, Paga)",
        markers=True,
        labels={"mes_ano_label": "Mês/Ano", "vl_financiado": "Valor Financiado (R$)"}
    )
    fig_tempo.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        transition=dict(
            duration=500,   # milissegundos
            easing="cubic-in-out")
    )

    return (
        total_producao,
        total_propostas,
        projecao_receita,
        valor_medio,
        fig_operador,
        fig_loja,
        fig_tempo
    )
