import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# ===== Estilo global =====
st.set_page_config(page_title="E-commerce Insights", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <style>
    h1, h2, h3 {
        color: #003366;
        font-family: 'Segoe UI', sans-serif;
    }
    .stApp {
        background-color: #ffffff;
        padding: 1rem;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ===== Título principal =====
st.title("Dashboard de Análise de E-commerce")

# ===== Carregar dados =====
@st.cache_data
def load_data():
    df = pd.read_csv("ecommerce-data.csv", encoding='ISO-8859-1')
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
    df['YearMonth'] = df['InvoiceDate'].dt.to_period('M')
    df['Weekday'] = df['InvoiceDate'].dt.day_name()
    return df

df = load_data()

# ===== Filtros interativos  =====
st.sidebar.header("Filtros")

# Filtro de datas com slider
date_min = df['InvoiceDate'].min()
date_max = df['InvoiceDate'].max()
date_range = st.sidebar.slider(
    "Período:",
    min_value=date_min.date(),
    max_value=date_max.date(),
    value=(date_min.date(), date_max.date()),
    format="DD/MM/YYYY"
)


# Filtro de países com múltipla seleção
country_options = sorted(df['Country'].unique().tolist())
selected_countries = st.sidebar.multiselect(
    label="Selecione os países:",
    options=country_options,
    default=country_options,
    placeholder="Filtrar países...",
    key="country_selector"
)

# Aplicar filtros
df = df[df['Country'].isin(selected_countries)]
df = df[(df['InvoiceDate'].dt.date >= date_range[0]) & (df['InvoiceDate'].dt.date <= date_range[1])]

# ===== KPIs =====
col1, col2, col3 = st.columns(3)
with col1:
    receita = df['TotalPrice'].sum()
    st.metric("Receita Total", f"£{receita:,.0f}".replace(",", "."))
with col2:
    pedidos = df['InvoiceNo'].nunique()
    st.metric("Nº de Pedidos", f"{pedidos:,}".replace(",", "."))
with col3:
    ticket_medio = receita / pedidos if pedidos > 0 else 0
    st.metric("Ticket Médio", f"£{ticket_medio:,.2f}".replace(",", "."))

# ===== Receita por país =====
st.subheader("Receita Total por País (Top 10)")
country_revenue = df.groupby("Country")["TotalPrice"].sum().sort_values(ascending=False).head(10)
st.bar_chart(country_revenue)



# ===== Receita mensal =====
st.subheader("Receita Mensal")
monthly = df.groupby('YearMonth')['TotalPrice'].sum().reset_index()
monthly['YearMonth'] = monthly['YearMonth'].astype(str)
fig, ax = plt.subplots(figsize=(16, 6))
ax.plot(monthly['YearMonth'], monthly['TotalPrice'], marker='o', color='#0066cc', linewidth=2)

# Rótulos de dados
for i, row in monthly.iterrows():
    if i % 2 == 1:  
        ax.text(i, row['TotalPrice'], f"£{row['TotalPrice']:,.0f}".replace(",", "."), 
                ha='left', va='bottom', fontsize=10)

ax.set_title("Evolução da Receita Mensal", fontsize=14)
ax.set_xlabel("Ano-Mês")
ax.set_ylabel("Receita (£)")
ax.set_xticks(range(len(monthly)))
ax.set_xticklabels(monthly['YearMonth'], rotation=45, ha='right')
plt.grid(False)
st.pyplot(fig)


# ===== Receita por dia da semana =====
st.subheader("Receita por Dia da Semana")
weekday = df.groupby('Weekday')['TotalPrice'].sum().reindex(
    ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
)
fig2, ax2 = plt.subplots()
sns.barplot(x=weekday.index, y=weekday.values, palette="Blues_d", ax=ax2)
for i, value in enumerate(weekday.values):
    ax2.text(i, value, f"£{value:,.0f}".replace(",", "."), ha='center', va='bottom', fontsize=8)
ax2.set_title("Receita por Dia da Semana")
ax2.set_ylabel("Receita (£)")
ax2.set_xlabel("")
st.pyplot(fig2)

# ===== Curva ABC de produtos =====
st.subheader("Curva ABC de Produtos")
product_revenue = df.groupby('Description')['TotalPrice'].sum().sort_values(ascending=False).reset_index()
product_revenue['cumulative_pct'] = product_revenue['TotalPrice'].cumsum() / product_revenue['TotalPrice'].sum()
def classifica_abc(p):
    if p <= 0.8:
        return 'A'
    elif p <= 0.95:
        return 'B'
    else:
        return 'C'
product_revenue['Classificacao'] = product_revenue['cumulative_pct'].apply(classifica_abc)
abc_summary = product_revenue['Classificacao'].value_counts().sort_index()
fig3, ax3 = plt.subplots()
sns.barplot(x=abc_summary.index, y=abc_summary.values, palette="pastel", ax=ax3)
for i, value in enumerate(abc_summary.values):
    ax3.text(i, value, f"{value}", ha='center', va='bottom', fontsize=9)
ax3.set_title("Distribuição dos Produtos por Classe ABC")
ax3.set_ylabel("Número de Produtos")
ax3.set_xlabel("Classe ABC")
st.pyplot(fig3)

# ===== Clusterização de países =====
st.subheader("Clusterização de Países")
country_stats = df.groupby('Country').agg({
    'TotalPrice': 'sum',
    'InvoiceNo': 'nunique',
    'Quantity': 'sum'
}).rename(columns={
    'TotalPrice': 'ReceitaTotal',
    'InvoiceNo': 'NumPedidos',
    'Quantity': 'QtdTotalVendida'
}).reset_index()
country_stats['TicketMedio'] = country_stats['ReceitaTotal'] / country_stats['NumPedidos']

features = country_stats[['ReceitaTotal', 'NumPedidos', 'QtdTotalVendida', 'TicketMedio']]
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
country_stats['Cluster'] = kmeans.fit_predict(scaled_features)

fig4, ax4 = plt.subplots(figsize=(10, 5))
sns.scatterplot(data=country_stats, x='ReceitaTotal', y='NumPedidos', hue='Cluster', palette='Set2', s=120, ax=ax4)

ax4.set_title('Clusters de Países por Receita e Pedidos')
ax4.set_xlabel('Receita Total (£)')
ax4.set_ylabel('Número de Pedidos')
st.pyplot(fig4)