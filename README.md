# streamlit_siac


## Sobre o Projeto

Este projeto é uma aplicação web interativa desenvolvida para analisar, visualizar e explorar os trabalhos acadêmicos apresentados na **SIAC 2025 (Semana de Integração Acadêmica da UFRJ)**.

O sistema processa dados brutos extraídos dos cadernos de resumos em PDF (Disponível em: **https://sistemas2.macae.ufrj.br/siac/paginainicial/index**) e oferece uma interface amigável para filtragem, análise estatística e uma funcionalidade de **Chat com seus Dados (RAG)**, onde uma Inteligência Artificial responde perguntas sobre os trabalhos baseada no conteúdo dos resumos.


## ✨ Funcionalidades

* **📊 Dashboard Interativo:**
    * Visualização de KPIs (Total de trabalhos, áreas, modalidades, locais).
    * Gráficos de distribuição por Tema e Modalidade.
    * Ranking dos Orientadores com mais trabalhos.
* **🔎 Filtros Avançados:**
    * Filtragem dinâmica por Tema, Modalidade, Área Principal e Local.
    * Busca textual por Título ou Autor.
* **🤖 Assistente de IA (RAG):**
    * Integração com **Google Gemini 1.5 Pro**.
    * Busca semântica (Vetorial) usando **FAISS**.
    * Permite perguntas em linguagem natural (ex: *"Quais trabalhos falam sobre sustentabilidade?"* ou *"Liste os orientadores de engenharia elétrica"*).
* **📄 Leitor de Resumos:**
    * Visualização detalhada de autores, orientadores, resumo e bibliografia de cada trabalho.


## Tecnologias Utilizadas

* **Linguagem:** Python 3.11
* **Frontend/Dashboard:** Streamlit
* **Manipulação de Dados:** Pandas
* **Extração de Dados (PDF):** PyMuPDF (fitz), Regex (Expressões Regulares)
* **Inteligência Artificial & LLM:**
    * LangChain (Orquestração)
    * Google Generative AI (Gemini & Embeddings)
    * FAISS (Banco de Dados Vetorial)


## 📂 Estrutura do Projeto

```text
├── .streamlit/
│   └── secrets.toml          # Chaves de API (NÃO INCLUÍDO NO REPOSITÓRIO)
├── BASE_MESTRE_SIAC_CT_FINAL.csv # Base de dados processada (Fonte do Dashboard)
├── extrac_resumos.py         # Script de extração dos resumos do PDF
├── extrac_sessoes.py         # Script de extração da programação
├── merge.py                  # Script de unificação das bases
├── visu.py            # Aplicação Principal (Streamlit + IA)
├── requirements.txt          # Lista de dependências do projeto
├── runtime.txt               # Configuração da versão Python para Deploy
└── README.md                 # Documentação do projeto
