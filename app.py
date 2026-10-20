
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st


# Configuração da página
st.set_page_config(
    page_title="Análise de anúncios de veículos",
    page_icon="🚗",
    layout="wide",
)

st.title("Análise de anúncios de veículos")
st.write(
    "Explore os preços, a quilometragem e as características "
    "dos veículos anunciados."
)

# Carregamento dos dados
DATA_PATH = Path(__file__).resolve().parent / "vehicles_us.csv"


@st.cache_data
def load_data(path):
    data = pd.read_csv(path)
    data["date_posted"] = pd.to_datetime(
        data["date_posted"], errors="coerce"
    )
    return data


try:
    car_data = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(
        "Arquivo vehicles_us.csv não encontrado. "
        "Coloque-o na pasta principal do projeto."
    )
    st.stop()

# Indicadores gerais
col1, col2, col3 = st.columns(3)

col1.metric("Total de anúncios", f"{len(car_data):,}")
col2.metric(
    "Preço médio",
    f"US$ {car_data['price'].mean():,.2f}",
)
col3.metric(
    "Preço mediano",
    f"US$ {car_data['price'].median():,.2f}",
)

st.divider()

# Filtros
st.subheader("Filtros")

filter_col1, filter_col2 = st.columns(2)

# Tipo de veículo
with filter_col1:
    vehicle_types = sorted(
        car_data["type"].dropna().unique().tolist()
    )
    selected_types = st.multiselect(
        "Tipo de veículo",
        options=vehicle_types,
        default=vehicle_types,
    )

# Excluir anúncios com preço de US$ 1
with filter_col2:
    exclude_one_dollar = st.checkbox(
        "Excluir anúncios com preço de US$ 1 das visualizações",
        value=False,
    )

# Filtragem dos dados
filtered_data = car_data[
    car_data["type"].isin(selected_types)
].copy()

if exclude_one_dollar:
    filtered_data = filtered_data[
        filtered_data["price"] != 1
    ]

st.caption(
    f"{len(filtered_data):,} anúncios selecionados "
    f"de {len(car_data):,} anúncios totais."
)

if filtered_data.empty:
    st.warning("Nenhum anúncio corresponde aos filtros.")
    st.stop()

# Histograma de preços
st.subheader("1. Distribuição dos preços")

max_price = int(filtered_data["price"].max())
price_limit = st.slider(
    "Preço máximo exibido no histograma (US$)",
    min_value=1,
    max_value=max(1, max_price),
    value=min(100000, max(1, max_price)),
    step=max(1, max(1, max_price) // 1000),
)

hist_data = filtered_data[
    filtered_data["price"].between(1, price_limit)
]

fig_hist = px.histogram(
    hist_data,
    x="price",
    nbins=50,
    title="Quantidade de anúncios por faixa de preço",
    labels={
        "price": "Preço (US$)",
        "count": "Quantidade de anúncios",
    },
)
fig_hist.update_layout(
    xaxis_title="Preço (US$)",
    yaxis_title="Quantidade de anúncios",
)
st.plotly_chart(fig_hist, use_container_width=True)

# Dispersão entre quilometragem e preço
st.subheader("2. Quilometragem versus preço")

scatter_data = filtered_data.dropna(
    subset=["odometer", "price"]
).copy()

if len(scatter_data) > 10000:
    scatter_data = scatter_data.sample(
        n=10000,
        random_state=42,
    )

fig_scatter = px.scatter(
    scatter_data,
    x="odometer",
    y="price",
    color="type",
    opacity=0.5,
    title="Relação entre quilometragem e preço",
    labels={
        "odometer": "Quilometragem (milhas)",
        "price": "Preço (US$)",
        "type": "Tipo de veículo",
    },
)
fig_scatter.update_layout(
    xaxis_title="Quilometragem (milhas)",
    yaxis_title="Preço (US$)",
)
st.plotly_chart(fig_scatter, use_container_width=True)

# Tabela de dados
with st.expander("Visualizar os dados filtrados"):
    st.dataframe(
        filtered_data.head(100),
        use_container_width=True,
    )
