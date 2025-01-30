import pandas as pd
import streamlit as st
import plotly_express as px

# Estilização do Streamlit
st.set_page_config(layout="wide")
st.title("Dashboard Coffee Shop Sales")

# Definindo o tema de cores
st.markdown("""
    <style>
        .css-1d391kg {
            color: #ff6347;
        }
        .css-1lcbg5v {
            font-size: 24px;
            color: #003366;
        }
        .css-4t4jmj {
            background-color: #e7f7f0;
        }
        .stButton>button {
            background-color: #ff7043;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# Carregar os dados
df = pd.read_csv("Coffee Shop Sales.csv")
df["transaction_date"] = pd.to_datetime(df["transaction_date"])
df = df.sort_values("transaction_date")

# Criando a coluna de Mês
df["Month"] = df["transaction_date"].apply(lambda x: str(x.year) + "-" + str(x.month))

# Opção para selecionar o mês (ou todos os meses ou meses específicos)
month_option = st.sidebar.radio("Selecione o filtro de mês", ("Todos os meses", "Meses específicos"))

if month_option == "Todos os meses":
    df_filtered = df
else:
    months = st.sidebar.multiselect("Selecione os meses", df["Month"].unique().tolist(), default=df["Month"].unique()[:3])
    df_filtered = df[df["Month"].isin(months)]

# Filtros de Loja
store_options = ["Todas"] + sorted(df["store_location"].unique().tolist())
selected_stores = st.sidebar.multiselect("Selecione a loja", store_options, default="Todas")

# Filtragem por loja
if "Todas" not in selected_stores:
    df_filtered = df_filtered[df_filtered["store_location"].isin(selected_stores)]

# Filtros de categoria de produto
product_categories = sorted(df["product_category"].unique().tolist())
selected_categories = st.sidebar.multiselect("Selecione a categoria de produto", product_categories, default=product_categories)

# Filtragem por categoria de produto
if selected_categories:
    df_filtered = df_filtered[df_filtered["product_category"].isin(selected_categories)]

# Cálculos das Métricas
total_vendas = df_filtered["transaction_qty"].sum()
ticket_medio = (df_filtered["transaction_qty"] * df_filtered["unit_price"]).sum() / len(df_filtered)

# Exibir as métricas lado a lado (usando cartões estilizados)
col1, col2 = st.columns(2)
col1.markdown('<div style="background-color: #ff7043; padding: 20px; border-radius: 10px; color: white;">' 
              f'<h3>Quantidade de Vendas</h3><p style="font-size: 24px;">{total_vendas:,}</p></div>', unsafe_allow_html=True)
col2.markdown('<div style="background-color: #ff7043; padding: 20px; border-radius: 10px; color: white;">' 
              f'<h3>Ticket Médio</h3><p style="font-size: 24px;">R$ {ticket_medio:.2f}</p></div>', unsafe_allow_html=True)

# Gráfico: Produto mais vendido
produtos_vendidos = df_filtered.groupby("product_category")["transaction_qty"].sum().reset_index()
fig_produtos = px.bar(produtos_vendidos, x="product_category", y="transaction_qty",
                      title="Produto Mais Vendido", labels={"transaction_qty": "Quantidade Vendida"},
                      color="transaction_qty", color_continuous_scale="Viridis", text_auto=True)

# Gráfico: Hora do dia com mais vendas
df_filtered["transaction_time"] = pd.to_datetime(df_filtered["transaction_time"], format="%H:%M:%S").dt.hour
horas_venda = df_filtered.groupby("transaction_time")["transaction_qty"].sum().reset_index()
fig_horas = px.line(horas_venda, x="transaction_time", y="transaction_qty", 
                    title="Hora do Dia com Mais Vendas", labels={"transaction_time": "Hora", "transaction_qty": "Quantidade Vendida"},
                    line_shape="spline", markers=True, template="plotly_dark")

# Exibir gráficos um abaixo do outro
col3 = st.container()  # Container para o primeiro gráfico
col4 = st.container()  # Container para o segundo gráfico

# Gráfico 1: Produto mais vendido
with col3:
    st.plotly_chart(fig_produtos, use_container_width=True)

# Gráfico 2: Hora do dia com mais vendas
with col4:
    st.plotly_chart(fig_horas, use_container_width=True)