#  Dashboard de Análise de E-commerce

Este repositório contém um projeto de análise exploratória e visualização interativa de um dataset de e-commerce utilizando **Python** e **Streamlit**, desenvolvido como parte do trabalho de **Mineração de Dados** da FATEC.

---

##  Objetivo

Explorar padrões de compra, comportamento de clientes e indicadores de desempenho comercial por meio de visualizações dinâmicas e interativas. O projeto também busca apoiar estratégias de expansão e otimização comercial com base em insights obtidos do histórico de transações.

---

##  Estrutura do Repositório

- `app.py` — Aplicação principal em Streamlit
- `ecommerce-data.csv` — Base de dados original
- `analise_exploratoria_ecommerce.ipynb` — Análise exploratória complementar em Jupyter
- `conclusoes.md` — Principais achados e recomendações estratégicas
- `README.md` — Esta documentação

---

##  Tecnologias utilizadas

- Python 3.x
- Streamlit
- Pandas
- Matplotlib & Seaborn
- Scikit-learn

---

## ▶ Como executar

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/Fatec_Mineracao_Dados.git
   cd Fatec_Mineracao_Dados

2. Instale as dependências:
pip install -r requirements.txt

3. Execute a aplicação:
streamlit run app.py


##  Funcionalidades do Dashboard

- Filtros interativos por data e país

- KPIs: receita total, nº de pedidos e ticket médio

- Gráficos:

    - Receita mensal

    - Receita por dia da semana

    - Receita por país (top 10)

    - Curva ABC de produtos

    - Clusterização de países
