import streamlit as st
import pandas as pd
import altair as alt
from streamlit.runtime.scriptrunner import get_script_run_ctx

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"], .stTextInput, .stSelectbox, .stMetric, .stMarkdown, .stButton, .stRadio, .stSlider, .stChart {
        font-family: 'Space Grotesk', sans-serif !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("# OBTs :clipboard:")
# st.sidebar.markdown('Ceará Sem Fome')
st.divider()

df_obts = pd.read_csv('cnpjs_obts.csv', sep=';')
df_obts = df_obts.drop(columns='Unnamed: 0', axis=1)

# Layout
st.logo('logo-cesf-e-cegov.png')

# Coleta listas únicas
todas_regioes = df_obts['Região de Planejamento'].unique()
todas_ugs = df_obts['UG'].unique()
todos_items = df_obts['Descrição do Item\n'].unique()

# Estado inicial dos filtros
regiao = st.sidebar.selectbox("Região de Planejamento", todas_regioes, index=None, placeholder="Escolha...")
df_ugs = df_obts[df_obts['Região de Planejamento'] == regiao]
ugs = df_ugs['UG'].unique()
ug = st.sidebar.selectbox('UG:', ugs, index=None, placeholder="Escolha...")
df_items = df_obts[(df_obts["UG"] == ug) & (df_obts["Região de Planejamento"] == regiao)]
items = df_items["Descrição do Item\n"].unique()
item = st.sidebar.selectbox('Item:', items, index=None, placeholder="Escolha...")



df_obts_regioes_group_regiao_ug = round(df_obts.groupby(['Região de Planejamento', 'UG'])['Valor OBT']\
.sum(), 2).reset_index()
df_obts_regioes_group_regiao_ug['Valor OBT Num'] = df_obts_regioes_group_regiao_ug['Valor OBT']\
    .astype(float)
# Cria uma versão formatada apenas para exibição (como texto)
df_obts_regioes_group_regiao_ug['Valor OBT'] = df_obts_regioes_group_regiao_ug['Valor OBT Num']\
    .apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
df_obts_regioes_group_regiao_ug.sort_values("Valor OBT Num", ascending=False)

filtered = df_obts_regioes_group_regiao_ug[(df_obts_regioes_group_regiao_ug\
    ['Região de Planejamento'] == regiao)]\
        .sort_values('Valor OBT Num', ascending=False)

valor = filtered['Valor OBT Num'].sum()
# label_metric = st.markdown(f"Total Investido na Região de Planejamento <b style='color:red'>{regiao}</b>", unsafe_allow_html=True)
valor_formatado = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
st.metric(label="Total Investido na Região de Planejamento", value=valor_formatado)
st.markdown(f"<b style='color:red'>{regiao}</b>", unsafe_allow_html=True)
st.divider()


col1, col2 = st.columns(2)

st.divider()

    
# =========================================================
# Filtrar os dados por UG e Região de Planejamento
# =========================================================

with col1:
    st.markdown(f"<h5>UGs que compraram na Região de Planejamento <b style='color:red'>{regiao}</b></h5>", unsafe_allow_html=True)
    chart = alt.Chart(filtered).mark_bar().encode(
        x=alt.X("Valor OBT Num:Q"),
        y=alt.Y("UG:N", sort='-x'),
        tooltip=["UG", "Valor OBT"]
    ).properties(
        width=700,
        height=400
    )

    st.altair_chart(chart, use_container_width=True)


# =========================================================
# Filtrar os dados por UG e Região de Planejamento
# e mostrar as compras por Fornecedor
# =========================================================


    
    
with col2:   
    st.markdown(f"<h5>A UG <b style='color:red'>{ug}</b> comprou nos seguintes fornecedores em <b style='color:red'>{regiao}</b></h5>", unsafe_allow_html=True)
    # st.write("A UG ", ug, " comprou nos seguintes fornecedores em ", regiao)
    df_obts_regioes_group_regiao_ug_fornecedor = round(df_obts.groupby(['Região de Planejamento', 'UG', 'Fornecedor'])['Valor OBT'].sum(), 2).reset_index()
    # Mantém a coluna numérica original
    df_obts_regioes_group_regiao_ug_fornecedor['Valor OBT Num'] = df_obts_regioes_group_regiao_ug_fornecedor['Valor OBT'].astype(float)

    # Cria uma versão formatada apenas para exibição (como texto)
    df_obts_regioes_group_regiao_ug_fornecedor['Valor OBT'] = \
        df_obts_regioes_group_regiao_ug_fornecedor['Valor OBT Num']\
        .apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df_obts_regioes_group_regiao_ug_fornecedor.sort_values("Valor OBT Num", ascending=False)

    filtered_fornecedor = df_obts_regioes_group_regiao_ug_fornecedor\
        [(df_obts_regioes_group_regiao_ug_fornecedor['Região de Planejamento'] == regiao)\
            & (df_obts_regioes_group_regiao_ug_fornecedor['UG'] == ug)]
    chart2 = alt.Chart(filtered_fornecedor).mark_bar().encode(
        x=alt.X("Valor OBT Num:Q"),
        y=alt.Y("Fornecedor:N", sort='-x'),
        tooltip=[
            alt.Tooltip("Fornecedor:N", title="Nome do Fornecedor"),
            alt.Tooltip("Valor OBT:N", title="Valor Recebido")
        ]
    ).properties(
        width=700,
        height=400
    )

    st.altair_chart(chart2, use_container_width=True)
    
# st.divider()
    
st.markdown(f"<h5>Itens comprados por <b style='color:red'>{ug}</b> na região <b style='color:red'>{regiao}</b></h5>", unsafe_allow_html=True)
df_obts_regioes_group_regiao_ug_item = round(df_obts.groupby(['Região de Planejamento', 'UG', 'Descrição do Item\n'])['Valor OBT']\
.sum(), 2).reset_index()
df_obts_regioes_group_regiao_ug_item.rename(columns={'Descrição do Item\n': 'Descrição do Item'}, inplace=True)
df_obts_regioes_group_regiao_ug_item['Valor OBT Num'] = df_obts_regioes_group_regiao_ug_item['Valor OBT']\
    .astype(float)
# Cria uma versão formatada apenas para exibição (como texto)
df_obts_regioes_group_regiao_ug_item['Valor OBT'] = df_obts_regioes_group_regiao_ug_item['Valor OBT Num']\
    .apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
df_obts_regioes_group_regiao_ug_item.sort_values("Valor OBT Num", ascending=False)


filtered_regiao = df_obts_regioes_group_regiao_ug_item[df_obts_regioes_group_regiao_ug_item\
    ['Região de Planejamento'] == regiao]


if ug:
    filtered_regiao = filtered_regiao[filtered_regiao\
        ['UG'] == ug]
    
agrupado = (filtered_regiao.groupby('Descrição do Item')["Valor OBT Num"].sum()
            .reset_index().sort_values("Valor OBT Num", ascending=False))

valor_chart3 = agrupado['Valor OBT Num'].sum()
agrupado['Valor OBT format'] = f"{valor_chart3:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
chart3 = alt.Chart(agrupado).mark_bar().encode(
    x=alt.X("Valor OBT Num:Q"),
    y=alt.Y("Descrição do Item:N", sort='-x'),
    tooltip=["Descrição do Item", "Valor OBT format"]
).properties(
    width=700,
    height=400
)

st.altair_chart(chart3, use_container_width=True)  


st.markdown(f"<h5>Fornecedores de <b style='color:red'>{item}</b> comprado por <b style='color:red'>{ug}</b> na região <b style='color:red'>{regiao}</b></h5>", unsafe_allow_html=True)
df_obts_regioes_group_regiao_ug_fornecedor = round(df_obts.groupby(['Região de Planejamento', 'UG', 'Fornecedor', 'Descrição do Item\n'])['Valor OBT'].sum(), 2).reset_index()
df_obts_regioes_group_regiao_ug_fornecedor.rename(columns={'Descrição do Item\n': 'Descrição do Item'}, inplace=True)

# Mantém a coluna numérica original
df_obts_regioes_group_regiao_ug_fornecedor['Valor OBT Num'] = df_obts_regioes_group_regiao_ug_fornecedor['Valor OBT'].astype(float)

# Cria uma versão formatada apenas para exibição (como texto)
df_obts_regioes_group_regiao_ug_fornecedor['Valor OBT'] = df_obts_regioes_group_regiao_ug_fornecedor['Valor OBT Num'].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
df_obts_regioes_group_regiao_ug_fornecedor.sort_values("Valor OBT Num", ascending=False)

df_obts_regioes_group_regiao_ug_fornecedor_filtered_regiao = df_obts_regioes_group_regiao_ug_fornecedor\
    [df_obts_regioes_group_regiao_ug_fornecedor['Região de Planejamento'] == regiao]

df_obts_regioes_group_regiao_ug_fornecedor_filtered_regiao_ug = df_obts_regioes_group_regiao_ug_fornecedor_filtered_regiao\
    [df_obts_regioes_group_regiao_ug_fornecedor_filtered_regiao['UG'] == ug]

if item:
    df_obts_regioes_group_regiao_ug_fornecedor_filtered_regiao_ug = \
        df_obts_regioes_group_regiao_ug_fornecedor_filtered_regiao_ug\
            [df_obts_regioes_group_regiao_ug_fornecedor_filtered_regiao_ug\
                ['Descrição do Item'] == item]
            
agrupado_item = (df_obts_regioes_group_regiao_ug_fornecedor_filtered_regiao_ug\
    .groupby('Fornecedor')["Valor OBT Num"].sum().reset_index().sort_values("Valor OBT Num", ascending=False))

st.dataframe(agrupado_item['Fornecedor'], hide_index=True)