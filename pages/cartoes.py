import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path
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

##################
# Funções
##################


def format_currency(value):
    """Formata um valor numérico para o formato de moeda brasileira (R$ X.XXX,XX)."""
    # Substitui vírgula por 'X' temporariamente, ponto por vírgula, e 'X' por ponto
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

@st.cache_data
def group_and_format_data(dataframe, group_cols, value_col='valor'):
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


col10, col11 = st.columns([1, 8], gap="small", vertical_alignment ="bottom")
with col10:
    st.header("Cartões CSF")
with col11:
    st.image("static/card_icon.png", width=60)

st.markdown("## Transações 🤝")
st.divider()

###################
# 1. Carregar dados
###################
df_transacoes = pd.read_csv('transacoes_2023_julho2025_agrupado_municipios_regioes.csv', encoding='latin-1')
# df_rede = pd.read_csv('df_rede_credenciada_first.csv')
df_rede_mun_regiao = pd.read_csv('qtd_estabelecimentos_credenciados_agrupado_por_municipio_regiao_julho.csv', encoding='latin-1')
df_lotes = pd.read_csv('lotes_municipios.csv')
df_benefs_cartao = pd.read_csv('cartao_csf_julho_2025_resumo.csv')
df_municipios_regioes= pd.read_csv('municipios_regioes.csv')



# --- Pré-processamento dos Dados --- #

df_lotes.rename(columns={'Nº LOTE': 'Lote', 
                         'Município': 'Nome Municipio'}, inplace=True)
df_lotes.drop(columns=['Unnamed: 0'], inplace=True)


df_merge_rede_mun_regiao_lotes = pd.merge(df_rede_mun_regiao, df_lotes, on='mun_upp', how='left')
df_merge_transacoes_lotes = pd.merge(df_transacoes, df_lotes, on='mun_upp', how='left')
df_merge_benefs_cartao_lotes_regioes = pd.merge(df_benefs_cartao, df_lotes, on='mun_upp', how='left')
# df_merge_benefs_cartao_lotes_regioes = pd.merge(df_merge_benefs_cartao_lotes, df_municipios_regioes, on='mun_upp', how='left')

# df_merge_benefs_cartao_lotes_regioes.rename(columns={'Município_x': 'Municipio', 
#                                                      'Região de Planejamento': 'Região de Planejamento', 
#                                                      'Nº LOTE': 'Lote'}, 
#                                             inplace=True)

# df_merge_benefs_cartao_lotes_regioes.drop(columns=['Município_y', 'Unnamed: 0'], inplace=True)

# df_merge_benefs_cartao_lotes_regioes = \
#     df_merge_benefs_cartao_lotes_regioes[['Municipio', 'Total', 'mun_upp', 'Lote', 'Região de Planejamento']].reset_index(drop=True)
# df_merge_benefs_cartao_lotes_regioes['Total'] = df_merge_benefs_cartao_lotes_regioes['Total'].astype(int)
# print(repr(list(df_merge_benefs_cartao_lotes_regioes.columns)))

# --- Layout e Logo --- #
st.logo('logo-cesf-e-cegov.png')


# --- Coleta de Listas Únicas para Filtros --- #

# Coleta todas as opções únicas das colunas relevantes para os filtros
todas_regioes = df_merge_transacoes_lotes['Região de Planejamento'].unique()
todos_municipios = df_merge_transacoes_lotes['mun_upp'].unique()
todos_lotes = df_merge_rede_mun_regiao_lotes['Lote'].unique()


# --- Estado Inicial e Lógica dos Filtros na Barra Lateral --- #

# Inicializa st.session_state para manter o estado dos filtros entre as execuções
# Isso é crucial para filtros encadeados e para evitar reruns desnecessários
if 'regiao_selecionada' not in st.session_state:
    st.session_state.regiao_selecionada = None
if 'lote_selecionado' not in st.session_state:
    st.session_state.lote_selecionado = None
if 'municipio_selecionado' not in st.session_state:
    st.session_state.municipio_selecionado = None
    


# Selectbox para Região de Planejamento
regiao = st.sidebar.selectbox(
    "Região de Planejamento", 
    todas_regioes, 
    index=None, 
    placeholder="Escolha...",
    key='regiao_filtro',
    on_change=lambda: st.session_state.update(municipio_selecionado=None)
)



# Atualiza o estado da sessão se a região mudar
if regiao != st.session_state.regiao_selecionada:
    st.session_state.regiao_selecionada = regiao
    # st.experimental_rerun() # Removido para evitar reruns excessivos com on_change


# Filtra o DataFrame base para os filtros dependentes

df_para_filtros = df_merge_transacoes_lotes.copy()
if regiao:
    df_para_filtros = df_para_filtros[df_para_filtros['Região de Planejamento'] == regiao]
    
# Selectbox para Lotes
lotes_disponiveis = sorted([m for m in df_para_filtros['Lote'].unique() if isinstance(m, str) and pd.notna(m)])
lote = st.sidebar.selectbox(
    "Lote", 
    lotes_disponiveis, 
    index=None, 
    placeholder="Escolha...",
    key='lote_filtro',
    on_change=lambda: st.session_state.update(municipio_selecionado=None)
)

# Atualiza o estado da sessão se o lote mudar
if lote != st.session_state.lote_selecionado:
    st.session_state.lote_selecionado = lote
    # st.experimental_rerun() # Removido para evitar reruns excessivos com on_change

# Filtra o DataFrame para UGs
if lote:
    df_para_filtros = df_para_filtros[df_para_filtros['Lote'] == lote]
    
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
    st.session_state.municipio_selecionado = municipios
    # st.experimental_rerun()
    
st.sidebar.text('Fonte: SPS - Julho/2025')    

# --- Lógica de Filtragem Principal para Visualizações --- #

# DataFrame base para os gráficos, filtrado pelas seleções do usuário
# Usamos o DataFrame original e aplicamos os filtros em cascata
df_visualizacao_transacoes = df_merge_transacoes_lotes.copy()
df_visualizacao_lote_transacoes = df_merge_transacoes_lotes.copy()
df_visualizacao_municipios_transacoes = df_merge_transacoes_lotes.copy()
df_visualizacao_rede = df_merge_rede_mun_regiao_lotes.copy()
df_visualizacao_municipios_rede = df_merge_rede_mun_regiao_lotes.copy()
df_visualizacao_benefs_cartao = df_merge_benefs_cartao_lotes_regioes.copy()
df_visualizacao_lote_benefs_cartao = df_merge_benefs_cartao_lotes_regioes.copy()
df_visualizacao_municipio_benefs_cartao = df_merge_benefs_cartao_lotes_regioes.copy()


if regiao:
    df_visualizacao_transacoes = df_visualizacao_transacoes[df_visualizacao_transacoes['Região de Planejamento'] == regiao]
    df_visualizacao_rede = df_visualizacao_rede[df_visualizacao_rede['Região de Planejamento'] == regiao]
    df_visualizacao_benefs_cartao = df_visualizacao_benefs_cartao[df_visualizacao_benefs_cartao['Região de Planejamento'] == regiao.upper() if isinstance(regiao, str) else regiao]
if lote:
    df_visualizacao_lote_transacoes = df_visualizacao_lote_transacoes[df_visualizacao_lote_transacoes['Lote'] == lote]
    df_visualizacao_lote_rede = df_visualizacao_municipios_rede[df_visualizacao_municipios_rede['Lote'] == lote]
    df_visualizacao_lote_benefs_cartao = df_visualizacao_lote_benefs_cartao[df_visualizacao_lote_benefs_cartao['Lote'] == lote]
# Aplica filtro de município
if municipios:
    df_visualizacao_municipios_transacoes = df_visualizacao_municipios_transacoes[df_visualizacao_municipios_transacoes['mun_upp'] == municipios]
    df_visualizacao_municipios_rede = df_visualizacao_rede[df_visualizacao_rede['mun_upp'] == municipios]
    df_visualizacao_municipio_benefs_cartao = df_visualizacao_municipio_benefs_cartao[df_visualizacao_municipio_benefs_cartao['mun_upp'] == municipios]

# Verifica se DataFrame filtrado está vazio
if df_visualizacao_transacoes.empty:
    st.info("Nenhum dado encontrado para os filtros selecionados. Tente ajustar suas seleções.")
    st.stop()



# Exibe mensagem se o DataFrame estiver vazio após a filtragem e interrompe a execução
# if df_visualizacao_transacoes_municipio.empty:
#     st.info("Nenhum dado encontrado para os filtros selecionados. Tente ajustar suas seleções.")
#     st.stop()

# --- Métricas e Resumos --- #

# Agrupa por Região e UG para o cálculo do valor total da região selecionada
df_agrupado_regiao_transacoes = group_and_format_data(df_visualizacao_transacoes, ['Região de Planejamento'])
df_agrupado_lote_transacoes = group_and_format_data(df_visualizacao_lote_transacoes, ['Lote'])
df_agrupado_municipio_transacoes = group_and_format_data(df_visualizacao_municipios_transacoes, ['mun_upp'])
df_agrupado_regiao_rede = df_visualizacao_rede[df_visualizacao_rede['Região de Planejamento']==regiao]
df_agrupado_lote_rede = df_visualizacao_rede[df_visualizacao_rede['Lote']==lote]
df_agrupado_municipios_rede = df_visualizacao_municipios_rede[df_visualizacao_municipios_rede['mun_upp']==municipios]

if regiao:
    df_agrupado_regiao_benefs = df_visualizacao_benefs_cartao[
        df_visualizacao_benefs_cartao['Região de Planejamento'] == regiao.upper()
    ]
    valor_total_regiao_benefs = df_agrupado_regiao_benefs['Total'].sum().astype(int)


# df_agrupado_regiao_benefs = df_visualizacao_benefs_cartao[df_visualizacao_benefs_cartao['Região de Planejamento']==regiao.upper()]
df_agrupado_lote_benefs = df_visualizacao_lote_benefs_cartao[df_visualizacao_lote_benefs_cartao['Lote']==lote]
df_agrupado_municipios_benefs = df_visualizacao_municipio_benefs_cartao[df_visualizacao_municipio_benefs_cartao['mun_upp']==municipios]


valor_total_regiao = df_agrupado_regiao_transacoes['valor Num'].sum()
valor_total_regiao_formatado = format_currency(valor_total_regiao)
valor_total_lote = df_agrupado_lote_transacoes['valor Num'].sum()
valor_total_lote_formatado = format_currency(valor_total_lote)
valor_total_municipio = df_agrupado_municipio_transacoes['valor Num'].sum()
valor_total_municipio_formatado = format_currency(valor_total_municipio)
valor_total_regiao_rede = df_agrupado_regiao_rede['qtd_credenciados'].sum()
valor_total_municipios_rede = df_agrupado_municipios_rede['qtd_credenciados'].sum()
valor_total_lote_rede = df_agrupado_lote_rede['qtd_credenciados'].sum()

valor_total_municipios_benefs = df_agrupado_municipios_benefs['Total'].sum()
valor_total_lote_benefs = df_agrupado_lote_benefs['Total'].sum()
# valor_total_lote_rede = df_agrupado_lote_rede['mun_upp'].count()
# valor_total_regiao_rede_formatado = format_currency(valor_total_regiao_rede)
# valor_total_municipios_rede_formatado = format_currency(valor_total_municipios_rede)


# Divide o layout em duas colunas para as métricas
col1, col2, col3 = st.columns(3)
with col1:
    # Exibe a métrica do valor total investido na região
    st.metric(label="Total de transações efetivadas através do Cartão CSF na Região de Planejamento", value=valor_total_regiao_formatado)
    if regiao:
        st.markdown(f"<b style='color:red'>{regiao}</b>", unsafe_allow_html=True)
with col2:
    # Exibe a métrica do valor total investido na região
    if not lote:
        st.info('Aguardando você escolher um lote', icon="🤔")
    else:
        
        st.metric(label="Total de transações efetivadas através do Cartão CSF no Lote", value=valor_total_lote_formatado)
        
        st.markdown(f"<b style='color:red'>{lote}</b>", unsafe_allow_html=True)
with col3:
    # Exibe a métrica do valor total investido na região
    if not municipios:
        st.info('Aguardando você escolher um município', icon="🤔")
    else:
        
        st.metric(label="Total de transações efetivadas através do Cartão CSF no Município", value=valor_total_municipio_formatado)
        
        st.markdown(f"<b style='color:red'>{municipios}</b>", unsafe_allow_html=True)



st.divider()
st.markdown("## Rede Credenciada 🛒")
st.divider()
col4, col5, col6 = st.columns(3)
with col4:
    # Exibe a métrica do valor total investido na região
    if regiao:
        st.metric(label="Total de estabelecimentos credenciados na Região de Planejamento", value=valor_total_regiao_rede)
        st.markdown(f"<b style='color:red'>{regiao}</b>", unsafe_allow_html=True)
    else:
        st.metric("Total de estabelecimentos credenciados", value=df_merge_rede_mun_regiao_lotes['qtd_credenciados'].sum())
with col5:
    # Exibe a métrica do valor total investido na região
    if not lote:
        st.info('Aguardando você escolher um lote', icon="🤔")
    else:
        
        st.metric(label="Total de estabelecimentos credenciados no Lote", value=valor_total_lote_rede)
        
        st.markdown(f"<b style='color:red'>{lote}</b>", unsafe_allow_html=True)
with col6:
    # Exibe a métrica do valor total investido na região
    if not municipios:
        st.info('Aguardando você escolher um município', icon="🤔")
    else:
        
        st.metric(label="Total de estabelecimentos credenciados no Município", value=valor_total_municipios_rede)
        
        st.markdown(f"<b style='color:red'>{municipios}</b>", unsafe_allow_html=True)

st.divider()
st.markdown("## Quantidade de Beneficiários 👨‍👩‍👧")
st.divider()
col7, col8, col9 = st.columns(3)
with col7:
    # Exibe a métrica do valor total investido na região
    if regiao:
        st.metric(label="Total de beneficiários na Região de Planejamento", value=valor_total_regiao_benefs)
        st.markdown(f"<b style='color:red'>{regiao}</b>", unsafe_allow_html=True)
    else:
        st.metric("Total de beneficiários", value=df_benefs_cartao['Total'].sum())
with col8:
    # Exibe a métrica do valor total investido na região
    if not lote:
        st.info('Aguardando você escolher um lote', icon="🤔")
    else:
        
        st.metric(label="Total de beneficiários no Lote", value=valor_total_lote_benefs)
        
        st.markdown(f"<b style='color:red'>{lote}</b>", unsafe_allow_html=True)
with col9:
    # Exibe a métrica do valor total investido na região
    if not municipios:
        st.info('Aguardando você escolher um município', icon="🤔")
    else:
        
        st.metric(label="Total de beneficiários no Município", value=valor_total_municipios_benefs)
        
        st.markdown(f"<b style='color:red'>{municipios}</b>", unsafe_allow_html=True)