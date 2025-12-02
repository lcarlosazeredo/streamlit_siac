# Análise de Dados SIAC 2025

## Sobre o Projeto

Este projeto é uma aplicação de Engenharia de Dados e Visualização (Dashboard) desenvolvida para extrair, processar e analisar os trabalhos acadêmicos apresentados na **SIAC 2025 (Semana de Integração Acadêmica da UFRJ)**.

Este sistema implementa um **Pipeline de ETL (Extract, Transform, Load)** automatizado que consolida dados de múltiplos centros (CAXIAS, CCJE, CCMN, CCS, CFCH, CLA, CT, FCC, MACAE) em uma base unificada.

O sistema processa dados brutos extraídos dos PDFs de **Programação** e **Cadernos de Resumos** (Disponível em: https://sistemas2.macae.ufrj.br/siac/paginainicial/index) e oferece uma interface interativa para exploração estatística e textual.

## ✨ Funcionalidades

* **📊 Dashboard Interativo (Streamlit):**
    * **KPIs Dinâmicos:** Contagem em tempo real de trabalhos, origens, áreas, modalidades e locais.
    * **Análise Temporal:** Mapa de Calor (Heatmap) interativo mostrando a densidade de apresentações por Dia da Semana vs. Horário.
    * **Processamento de Linguagem Natural (NLP):** Geração de **Nuvem de Palavras** (WordCloud) baseada nos resumos filtrados, com remoção de stopwords em português.
    * **Rankings:** Top 10 temas mais frequentes e Top 10 orientadores com mais trabalhos.

* **⚙️ Pipeline de Dados Automatizado:**
    * Extração inteligente de PDFs usando "Máquina de Estados" para associar horários e locais a múltiplos trabalhos.
    * Uso de Regex (Expressões Regulares) para mineração de textos complexos (Resumos, Bibliografias).
    * Unificação automática de bases de dados de diferentes centros.

* **🔎 Filtros Avançados:**
    * Filtragem multidimensional: Origem (Centro), Tema, Modalidade, Área Principal e Local.
    * Busca textual global por Título, Autor ou Orientador.

## 🛠 Tecnologias Utilizadas

* **Linguagem:** Python 3.1
* **Orquestração ETL:** Script Python autônomo (`pipeline_geral.py`)
* **Frontend/Dashboard:** Streamlit
* **Manipulação de Dados:** Pandas
* **Extração de Dados (PDF):** PyMuPDF (fitz), Regex
* **Visualização:** * Matplotlib (Gráficos de barras e Nuvem de Palavras)
    * Plotly Express (Mapa de Calor Interativo)
    * WordCloud & NLTK (Processamento de texto)

## 📂 Estrutura do Projeto

A estrutura de arquivos é organizada para separar a extração (ETL) da visualização:

```text
├── pdfs/                       # [OBRIGATÓRIO] Pasta com os PDFs de entrada e CSVs intermediários
│   ├── 2025_CT-PROG_SESSOES.pdf
│   ├── 2025_CT-CAD_RESUMOS.pdf
│   └── ...
├── pipeline_geral.py           # Script Mestre: Executa a extração de TODOS os centros
├── extrac_sessoes.py           # Módulo: Extrai grade de horários 
├── extrac_resumos.py           # Módulo: Extrai textos dos resumos
├── merge.py                    # Módulo: Unifica e limpa os dados
├── visu.py                     # Aplicação do Dashboard (Streamlit)
├── BASE_SIAC_UFRJ_COMPLETA.csv # Base Final (Gerada automaticamente)
├── requirements.txt            # Dependências
└── README.md                   # Documentação
