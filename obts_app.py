# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import altair as alt
# import numpy as np

# --- Configuração da Página e Estilo --- #

st.set_page_config(layout="wide")

# Aplica estilo CSS para a fonte da aplicação
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"], .stTextInput, .stSelectbox, .stMetric, .stMarkdown, .stButton, .stRadio, .stSlider, .stChart {
        font-family: 'Space Grotesk', sans-serif !important;
    }
    </style>
""", unsafe_allow_html=True)

# Título principal da aplicação
st.markdown("# Compras efetuadas pelas UGs - Ordem Bancária de Transações(OBTs) :clipboard:")
st.divider()

# --- Carregamento e Pré-processamento de Dados --- #

# @st.cache_data
# def load_data(file_path):
#     """Carrega os dados do arquivo CSV e realiza o pré-processamento inicial.
#     Inclui tratamento de erros para arquivo não encontrado e colunas numéricas.
#     """
#     try:
#         df = pd.read_csv(file_path, sep=";")
#         # Remove a coluna 'Unnamed: 0' se ela existir, tornando o código mais robusto
#         if 'Unnamed: 0' in df.columns:
#             df = df.drop(columns='Unnamed: 0', axis=1)
#         # Garante que 'Valor OBT' é numérico, tratando valores não conversíveis como NaN
#         df['Valor OBT'] = pd.to_numeric(df['Valor OBT'], errors='coerce')
#         # Remove linhas onde 'Valor OBT' é NaN após a conversão
#         df.dropna(subset=['Valor OBT'], inplace=True)
#         return df
#     except FileNotFoundError:
#         st.error(f"Erro: O arquivo de dados '{file_path}' não foi encontrado. Por favor, verifique o caminho.")
#         st.stop() # Interrompe a execução do Streamlit
#     except Exception as e:
#         st.error(f"Erro ao carregar ou processar os dados: {e}. Verifique o formato do arquivo.")
#         st.stop() # Interrompe a execução do Streamlit

# Carrega os dados e armazena em cache para performance
# df_obts = pd.read_csv('obts_final_2023_maio_2025_3.csv', sep=';')
df_obts = pd.read_csv('obts_junho.csv', sep=';')
df_coops = pd.read_csv('rel_cooperativa_csf_lotes.csv')

# itens_interesse = ['Deslocamento e Logística (combustiveis, locação de veiculos)\n',
#        'Gêneros Alimentícios ( Proteínas, Carboidratos, Hortaliças, Sódios e Lipídios)',
#        'Matérial de Higienização e Limpeza \n',
#        'Embalagens e Descartáveis  (marmita, colher e touca)\n',
#        'Serviço de preparo de alimento\n',
#        'Deslocamento e Logistica (combustiveis, locação de veiculos)\n',
#        'Material de Higienização e Limpeza \n',
#        'Manutenção de Equipamentos\n',
#        'Embalagens e Descartáveis  (marmita, colher e touca) \n', 
#        'Manutenção de equipamentos\n',
#        'Deslocamento e Logística (combustíveis, locação de veículos)\n',
#        'Manutenção de Equipamentos',
#        'Deslocamento e LogÍstica (combustiveis, locação de veiculos)\n',
#        'Manutenção de Equipamentos \n', 
#        'Manutenção de equipamentos']

itens_interesse = [
    'Gêneros Alimentícios ( Proteínas, Carboidratos, Hortaliças, Sódios e Lipídios)',
    'Deslocamento e Logística (combustíveis, locação de veículos)',
    'Material de Higienização e Limpeza',
    'Embalagens e Descartáveis  (marmita, colher e touca)',
    'Manutenção de Equipamentos'
]

df_obts.replace({'Gêneros Alimentícios ( Proteínas, Carboidratos, Hortaliças, Sódios e Lipídios) \n': 'Gêneros Alimentícios ( Proteínas, Carboidratos, Hortaliças, Sódios e Lipídios)',
                                        'Gêneros Alimentícios ( Proteínas, Carboidratos, Hortaliças, Sódios e Lipídios)\n' : 'Gêneros Alimentícios ( Proteínas, Carboidratos, Hortaliças, Sódios e Lipídios)',
                                        'Deslocamento e Logística (combustiveis, locação de veiculos)\n': 'Deslocamento e Logística (combustíveis, locação de veículos)',
                                        'Deslocamento e Logistica (combustiveis, locação de veiculos)\n': 'Deslocamento e Logística (combustíveis, locação de veículos)',
                                        'Deslocamento e Logística (combustíveis, locação de veículos)\n': 'Deslocamento e Logística (combustíveis, locação de veículos)',
                                        'Deslocamento e LogÍstica (combustiveis, locação de veiculos)\n': 'Deslocamento e Logística (combustíveis, locação de veículos)',
                                        'Matérial de Higienização e Limpeza \n': 'Material de Higienização e Limpeza',
                                        'Material de Higienização e Limpeza \n': 'Material de Higienização e Limpeza',
                                        'Embalagens e Descartáveis  (marmita, colher e touca)\n': 'Embalagens e Descartáveis  (marmita, colher e touca)',
                                        'Embalagens e Descartáveis  (marmita, colher e touca) \n': 'Embalagens e Descartáveis  (marmita, colher e touca)',
                                        'Manutenção de Equipamentos\n': 'Manutenção de Equipamentos',
                                        'Manutenção de equipamentos\n': 'Manutenção de Equipamentos',
                                        'Manutenção de Equipamentos': 'Manutenção de Equipamentos',
                                        'Manutenção de Equipamentos \n': 'Manutenção de Equipamentos',
                                        'Manutenção de equipamentos': 'Manutenção de Equipamentos',
}, inplace=True)

# Exibe mensagem e interrompe se o DataFrame estiver vazio após o carregamento
if df_obts.empty:
    st.warning("Nenhum dado disponível para análise após o carregamento e pré-processamento. Verifique o arquivo CSV.")
    st.stop()

# --- Funções Auxiliares para Processamento e Formatação de Dados --- #

def format_currency(value):
    """Formata um valor numérico para o formato de moeda brasileira (R$ X.XXX,XX)."""
    # Substitui vírgula por 'X' temporariamente, ponto por vírgula, e 'X' por ponto
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

@st.cache_data
def group_and_format_data(dataframe, group_cols, value_col='Valor OBT'):
    """Agrupa o DataFrame pelas colunas especificadas, soma a coluna de valor,
    e cria uma coluna formatada para exibição.
    """
    # Agrupa e soma os valores, arredondando para 2 casas decimais
    grouped_df = round(dataframe.groupby(group_cols)[value_col].sum(), 2).reset_index()
    # Cria uma coluna numérica para ordenação e cálculos
    grouped_df[f'{value_col} Num'] = grouped_df[value_col].astype(float)
    # Cria uma coluna formatada para exibição nos tooltips e tabelas
    grouped_df[value_col] = grouped_df[f'{value_col} Num'].apply(format_currency)
    # Retorna o DataFrame agrupado e ordenado pelo valor numérico em ordem decrescente
    return grouped_df.sort_values(f'{value_col} Num', ascending=False)

def create_altair_bar_chart(dataframe, x_col, y_col, title, tooltip_cols):
    """Cria um gráfico de barras Altair genérico.
    x_col: coluna para o eixo X (quantitativa)
    y_col: coluna para o eixo Y (nominal), com ordenação decrescente por x_col
    title: título do gráfico
    tooltip_cols: lista de colunas para exibir no tooltip
    """
    chart = alt.Chart(dataframe).mark_bar().encode(
        x=alt.X(f"{x_col}:Q", title="Valor OBT"), # Eixo X como quantitativo
        y=alt.Y(f"{y_col}:N", sort=alt.EncodingSortField(field=x_col, op="sum", order='descending'), title=y_col), # Eixo Y como nominal, ordenado
        tooltip=tooltip_cols # Colunas para o tooltip
    ).properties(
        width=700,
        height=400,
        title=title
    ).interactive() # Permite zoom e pan
    return chart

# --- Layout e Logo --- #
st.logo('logo-cesf-e-cegov.png')

# --- Coleta de Listas Únicas para Filtros --- #

# Coleta todas as opções únicas das colunas relevantes para os filtros
todas_regioes = df_obts['Região de Planejamento'].unique()
todas_ugs = df_obts['Orgão'].unique()
todos_items = df_obts['IPT'].unique()
todos_municipios = df_obts['mun_upp'].unique()
todos_lotes = df_obts['Nº LOTE'].unique()

# Filtra e ordena municípios, removendo valores NaN e garantindo que são strings
municipios_sem_nan = [m for m in todos_municipios if isinstance(m, str) and pd.notna(m)]
municipios_ordenados = sorted(municipios_sem_nan)

# --- Estado Inicial e Lógica dos Filtros na Barra Lateral --- #

# Inicializa st.session_state para manter o estado dos filtros entre as execuções
# Isso é crucial para filtros encadeados e para evitar reruns desnecessários
if 'regiao_selecionada' not in st.session_state:
    st.session_state.regiao_selecionada = None
if 'lote_selecionado' not in st.session_state:
    st.session_state.lote_selecionado = None
if 'municipio_selecionado' not in st.session_state:
    st.session_state.municipio_selecionado = None
if 'ug_selecionada' not in st.session_state:
    st.session_state.ug_selecionada = None
if 'item_selecionado' not in st.session_state:
    st.session_state.item_selecionado = None

# Selectbox para Região de Planejamento
regiao = st.sidebar.selectbox(
    "Região de Planejamento", 
    todas_regioes, 
    index=None, 
    placeholder="Escolha...",
    key='regiao_filtro',
    on_change=lambda: st.session_state.update(municipio_selecionado=None, ug_selecionada=None, item_selecionado=None)
)



# Atualiza o estado da sessão se a região mudar
if regiao != st.session_state.regiao_selecionada:
    st.session_state.regiao_selecionada = regiao
    # st.experimental_rerun() # Removido para evitar reruns excessivos com on_change


# Filtra o DataFrame base para os filtros dependentes

df_para_filtros = df_obts.copy()
if regiao:
    df_para_filtros = df_para_filtros[df_para_filtros['Região de Planejamento'] == regiao]

# Selectbox para Lotes
lotes_disponiveis = sorted([m for m in df_para_filtros['Nº LOTE'].unique() if isinstance(m, str) and pd.notna(m)])
lote = st.sidebar.selectbox(
    "Lote", 
    lotes_disponiveis, 
    index=None, 
    placeholder="Escolha...",
    key='lote_filtro',
    on_change=lambda: st.session_state.update(municipio_selecionado=None, ug_selecionada=None, item_selecionado=None)
)

# Atualiza o estado da sessão se o lote mudar
if lote != st.session_state.lote_selecionado:
    st.session_state.lote_selecionado = lote
    # st.experimental_rerun() # Removido para evitar reruns excessivos com on_change

# Filtra o DataFrame para UGs
if lote:
    df_para_filtros = df_para_filtros[df_para_filtros['Nº LOTE'] == lote]

# Selectbox para Município
municipios_disponiveis = sorted([m for m in df_para_filtros['mun_upp'].unique() if isinstance(m, str) and pd.notna(m)])
municipios = st.sidebar.selectbox(
    'Município: ',
    municipios_disponiveis,
    index=None,
    placeholder="Escolha...",
    key='municipio_filtro',
    on_change=lambda: st.session_state.update(ug_selecionada=None, item_selecionado=None)
)

# Atualiza o estado da sessão se o município mudar
if municipios != st.session_state.municipio_selecionado:
    st.session_state.municipio_selecionada = municipios
    # st.experimental_rerun()

# Filtra o DataFrame para UGs
if municipios:
    df_para_filtros = df_para_filtros[df_para_filtros['mun_upp'] == municipios]

# Selectbox para UG
ugs_disponiveis = sorted([ug for ug in df_para_filtros['Orgão'].unique() if isinstance(ug, str) and pd.notna(ug)])
ug = st.sidebar.selectbox(
    'Convenente:',
    ugs_disponiveis,
    index=None,
    placeholder="Escolha...",
    key='ug_filtro',
    on_change=lambda: st.session_state.update(item_selecionado=None)
)

# Atualiza o estado da sessão se a UG mudar
if ug != st.session_state.ug_selecionada:
    st.session_state.ug_selecionada = ug
    # st.experimental_rerun()

# Filtra o DataFrame para Itens
if ug:
    df_para_filtros = df_para_filtros[df_para_filtros['Orgão'] == ug]

# Selectbox para Item
items_disponiveis = sorted([item for item in df_para_filtros['IPT'].unique() if isinstance(item, str) and pd.notna(item)])
item = st.sidebar.selectbox(
    'Item:',
    items_disponiveis,
    index=None,
    placeholder="Escolha...",
    key='item_filtro'
)

# Atualiza o estado da sessão se o item mudar
if item != st.session_state.item_selecionado:
    st.session_state.item_selecionado = item

# --- Lógica de Filtragem Principal para Visualizações --- #

# DataFrame base para os gráficos, filtrado pelas seleções do usuário
# Usamos o DataFrame original e aplicamos os filtros em cascata
df_visualizacao_obts = df_obts.copy()
df_visualizacao_obts_lote = df_obts.copy()
df_visualizacao_obts_municipio = df_obts.copy()
df_visualizacao_coops = df_coops.copy()

if regiao:
    df_visualizacao_obts = df_visualizacao_obts[df_visualizacao_obts['Região de Planejamento'] == regiao]
    df_visualizacao_coops = df_visualizacao_coops[df_visualizacao_coops['Região de Planejamento'] == regiao]
if lote:
    df_visualizacao_obts_lote = df_visualizacao_obts_lote[df_visualizacao_obts_lote['Nº LOTE'] == lote]
    df_visualizacao_coops = df_visualizacao_coops[df_visualizacao_coops['Nº LOTE'] == lote]
if municipios:
    df_visualizacao_obts_municipio = df_visualizacao_obts_municipio[df_visualizacao_obts_municipio['mun_upp'] == municipios]
    df_visualizacao_coops = df_visualizacao_coops[df_visualizacao_coops['mun_upp'] == municipios]
if ug:
    df_visualizacao_obts = df_visualizacao_obts[df_visualizacao_obts['Orgão'] == ug]
if item:
    df_visualizacao_obts = df_visualizacao_obts[df_visualizacao_obts['IPT'] == item]

# Exibe mensagem se o DataFrame estiver vazio após a filtragem e interrompe a execução
if df_visualizacao_obts.empty:
    st.info("Nenhum dado encontrado para os filtros selecionados. Tente ajustar suas seleções.")
    st.stop()

# --- Métricas e Resumos --- #

# Agrupa por Região e UG para o cálculo do valor total da região selecionada
df_agrupado_regiao_ug = group_and_format_data(df_visualizacao_obts, ['Região de Planejamento', 'Orgão'])
df_agrupado_regiao_ug_lote = group_and_format_data(df_visualizacao_obts_lote, ['Nº LOTE'])
df_agrupado_regiao_ug_lote_municipio = group_and_format_data(df_visualizacao_obts_municipio, ['mun_upp'])
df_agrupado_regiao_ug_coops = group_and_format_data(df_visualizacao_coops, ['Convenente'])

valor_total_regiao = df_agrupado_regiao_ug['Valor OBT Num'].sum()
valor_total_regiao_lote = df_agrupado_regiao_ug_lote['Valor OBT Num'].sum()
valor_total_regiao_lote_municipio = df_agrupado_regiao_ug_lote_municipio['Valor OBT Num'].sum()
valor_total_regiao_formatado = format_currency(valor_total_regiao)
valor_total_regiao_lote_formatado = format_currency(valor_total_regiao_lote)
valor_total_regiao_lote_municipio_formatado = format_currency(valor_total_regiao_lote_municipio)
valor_total_regiao_coops = df_agrupado_regiao_ug_coops['Valor OBT Num'].sum()
valor_total_regiao_coops_formatado = format_currency(valor_total_regiao_coops)

# Divide o layout em duas colunas para as métricas
label_coop = 'Total de compras em Cooperativas'
if regiao:
    label_coop = "Total de compras em Cooperativas na Região de Planejamento"
if regiao and lote:
    label_coop = "Total de compras em Cooperativas no Lote"
if regiao and lote and municipios:
    label_coop = "Total de compras em Cooperativas no Município"
                
col1, col2, col3, col4 = st.columns(4)
with col1:
    # Exibe a métrica do valor total investido na região
    st.metric(label="Total Investido na Região de Planejamento", value=valor_total_regiao_formatado)
    if regiao:
        st.markdown(f"<b style='color:red'>{regiao}</b>", unsafe_allow_html=True)
with col2:
    # Exibe a métrica do valor total investido na região
    if not lote:
        st.info('Aguardando você escolher um lote', icon="🤔")
    else:
        st.metric(label="Total Investido no Lote", value=valor_total_regiao_lote_formatado)
        st.markdown(f"<b style='color:red'>{lote}</b>", unsafe_allow_html=True)
with col3:
    # Exibe a métrica do valor total investido na região
    if not municipios:
        st.info('Aguardando você escolher um município', icon="🤔")
    else:
        st.metric(label="Total Investido no Município", value=valor_total_regiao_lote_municipio_formatado)
        st.markdown(f"<b style='color:red'>{municipios}</b>", unsafe_allow_html=True)
with col2:
    # Exibe a métrica do valor total investido na região
    st.metric(label=label_coop, value=valor_total_regiao_coops_formatado)
st.divider()

# --- Visualizações --- #

# Divide o layout em duas colunas para os gráficos
col3, col4 = st.columns(2)

with col3:
    st.markdown(f"<h5>UGs que compraram na Região de Planejamento <b style='color:red'>{regiao if regiao else 'selecionada'}</b></h5>", unsafe_allow_html=True)
    
    # Cria o gráfico de barras para UGs
    chart_ug_compras = create_altair_bar_chart(
        df_agrupado_regiao_ug,
        x_col="Valor OBT Num",
        y_col="Orgão",
        title="Compras por Unidade Gestora",
        tooltip_cols=["Orgão", "Valor OBT"]
    )
    st.altair_chart(chart_ug_compras, use_container_width=True)

with col4:
    st.markdown(f"<h5>A UG <b style='color:red'>{ug if ug else 'selecionada'}</b> comprou nos seguintes fornecedores em <b style='color:red'>{regiao if regiao else 'região selecionada'}</b></h5>", unsafe_allow_html=True)
    
    # Agrupa dados por Fornecedor para o gráfico
    df_agrupado_fornecedor = group_and_format_data(df_visualizacao_obts, ['Região de Planejamento', 'Orgão', 'Fornecedor'])
    
    # Filtra por UG e Região para o gráfico de fornecedores
    # Se UG ou Região não estiverem selecionadas, o DataFrame filtrado será vazio para este gráfico específico
    filtered_fornecedor = df_agrupado_fornecedor[
        (df_agrupado_fornecedor['Região de Planejamento'] == regiao) &
        (df_agrupado_fornecedor['Orgão'] == ug)
    ] if regiao and ug else pd.DataFrame() # Retorna DataFrame vazio se filtros não selecionados

    if filtered_fornecedor.empty:
        st.info(f"Nenhum fornecedor encontrado para a UG {ug if ug else 'selecionada'} na região {regiao if regiao else 'selecionada'}. Por favor, selecione uma UG e Região.")
    else:
        # Cria o gráfico de barras para Fornecedores
        chart_fornecedor_compras = create_altair_bar_chart(
            filtered_fornecedor,
            x_col="Valor OBT Num",
            y_col="Fornecedor",
            title="Compras por Fornecedor",
            tooltip_cols=[
                alt.Tooltip("Fornecedor:N", title="Nome do Fornecedor"),
                alt.Tooltip("Valor OBT:N", title="Valor Recebido")
            ]
        )
        st.altair_chart(chart_fornecedor_compras, use_container_width=True)

st.divider()

st.markdown(f"<h5>Itens comprados por <b style='color:red'>{ug if ug else 'UG selecionada'}</b> na região <b style='color:red'>{regiao if regiao else 'região selecionada'}</b></h5>", unsafe_allow_html=True)

# Agrupa dados por Item para o gráfico
df_agrupado_item = group_and_format_data(df_visualizacao_obts, ['Região de Planejamento', 'Orgão', 'IPT'])
df_agrupado_item.rename(columns={'IPT': 'Descrição do Item'}, inplace=True)

# Filtra por UG e Região para o gráfico de itens
# event_item = None

filtered_item = df_agrupado_item[
    (df_agrupado_item['Região de Planejamento'] == regiao) &
    (df_agrupado_item['Orgão'] == ug)
] if regiao and ug else pd.DataFrame() # Retorna DataFrame vazio se filtros não selecionados

if filtered_item.empty:
    st.info(f"Nenhum item encontrado para a UG {ug if ug else 'selecionada'} na região {regiao if regiao else 'selecionada'}. Por favor, selecione uma UG e Região.")
else:
    # Agrupa novamente para o gráfico de itens, caso haja múltiplas entradas para o mesmo item após a filtragem
    agrupado_final_item = (filtered_item.groupby('Descrição do Item')['Valor OBT Num'].sum()
                            .reset_index().sort_values("Valor OBT Num", ascending=False))

    # Cria um seletor para exibir informações ao clicar no gráfico
    selector_item = alt.selection_point("select_item")
    # Cria o gráfico de barras para Itens Comprados
    # chart_itens_comprados = create_altair_bar_chart(
    #     agrupado_final_item,
    #     x_col="Valor OBT Num",
    #     y_col="Descrição do Item",
    #     title="Itens Comprados",
    #     tooltip_cols=["Descrição do Item", alt.Tooltip("Valor OBT Num", format=".2f", title="Valor OBT")]
    # )
    # st.altair_chart(chart_itens_comprados, use_container_width=True).add_params(selector_item)
    chart_itens_comprados = alt.Chart(agrupado_final_item)\
                                                        .mark_bar()\
                                                        .encode(
                                                            x=alt.X("Valor OBT Num:Q", title="Valor OBT"),
                                                            y=alt.Y("Descrição do Item:N", title="Descrição do Item"),
                                                            tooltip=["Descrição do Item", alt.Tooltip("Valor OBT Num", format=".2f", title="Valor OBT")]
                                                        )\
                                                        .add_params(selector_item)
    event_item = st.altair_chart(chart_itens_comprados, key="chart_item", on_select="rerun")
    # Mostrar informações diferentes para cada gráfico
    # if event_item and event_item.selection and event_item.selection.selector_item:
    @st.dialog("Detalhes do Item")
    def dialog_item(item):
        st.write("Item Selecionado:", item)
        df = df_obts.copy()
        df_filtered = df[df['IPT']==item]
        valor_total = df_filtered['Valor OBT'].sum()
        valor_formatado = f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        st.write("Valor Total Comprado:", valor_formatado)
        df_filtered_agrupado_regiao = df_filtered.groupby('Região de Planejamento')['Valor OBT'].sum().reset_index().sort_values('Valor OBT', ascending=False)
        df_filtered_agrupado_regiao['Valor Obt Formatado'] = df_filtered_agrupado_regiao['Valor OBT'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        chart_item_detalhe = create_altair_bar_chart(
            df_filtered_agrupado_regiao,
            x_col="Valor OBT",
            y_col="Região de Planejamento",
            title="Compras por Região",
            tooltip_cols=[
                # alt.Tooltip("Fornecedor:N", title="Nome do Fornecedor"),
                alt.Tooltip("Valor Obt Formatado:N", title="Valor Investido")
            ]
        )
        st.altair_chart(chart_item_detalhe, use_container_width=True)
    if event_item.selection.select_item:
        # print(f'Event_Item: {event_item}\n Event_Item_Selection: {event_item.selection}')
        dialog_item(event_item['selection']['select_item'][0]['Descrição do Item'])
        # st.write("Informações do gráfico 1:", event_item.selection.selector_item)


st.markdown(f"<h5>Fornecedores de <b style='color:red'>{item if item else 'item selecionado'}</b> comprado por <b style='color:red'>{ug if ug else 'UG selecionada'}</b> na região <b style='color:red'>{regiao if regiao else 'região selecionada'}</b></h5>", unsafe_allow_html=True)

# Agrupa dados por Fornecedor e Item para a tabela
df_agrupado_fornecedor_item = group_and_format_data(df_visualizacao_obts, ['Região de Planejamento', 'Orgão', 'Fornecedor', 'IPT'])
df_agrupado_fornecedor_item.rename(columns={'IPT': 'Descrição do Item'}, inplace=True)

# Filtra por Região, UG e Item para a tabela de fornecedores por item
filtered_fornecedor_item = df_agrupado_fornecedor_item[
    (df_agrupado_fornecedor_item['Região de Planejamento'] == regiao) &
    (df_agrupado_fornecedor_item['Orgão'] == ug) &
    (df_agrupado_fornecedor_item['Descrição do Item'] == item)
] if regiao and ug and item else pd.DataFrame() # Retorna DataFrame vazio se filtros não selecionados

if filtered_fornecedor_item.empty:
    st.info(f"Nenhum fornecedor encontrado para o item {item if item else 'selecionado'} da UG {ug if ug else 'selecionada'} na região {regiao if regiao else 'selecionada'}. Por favor, selecione um Item, UG e Região.")
else:
    # Agrupa novamente para a tabela, caso haja múltiplas entradas para o mesmo fornecedor após a filtragem
    agrupado_final_fornecedor_item = (filtered_fornecedor_item.groupby('Fornecedor')['Valor OBT Num'].sum()
                                      .reset_index().sort_values("Valor OBT Num", ascending=False))
    # Exibe a tabela de fornecedores
    st.dataframe(agrupado_final_fornecedor_item[['Fornecedor', 'Valor OBT Num']], hide_index=True, use_container_width=True)





# %%
