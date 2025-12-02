# python -m streamlit run visu.py
# app.pY

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords

# --- CONFIGURAÇÃO INICIAL (NLTK) ---
# Baixar stopwords na primeira execução se não existirem
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Configuração da página
st.set_page_config(page_title="Análise SIAC (UFRJ)", layout="wide")

st.markdown("""
<style> 
    /* Aumenta o tamanho da fonte das abas */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 24px;
    }     
</style>
""", unsafe_allow_html=True)

# --- ARQUIVO MESTRE ---
ARQUIVO_MESTRE = "BASE_SIAC_UFRJ_COMPLETA.csv"

# --- FUNÇÃO PARA GERAR A NUVEM DE PALAVRAS ---
@st.cache_data
def gerar_nuvem_de_palavras(df_alvo):
    if df_alvo.empty:
        return None
    
    # 1. Juntar todos os resumos num textão só
    # Filtramos apenas onde o resumo é string válida
    # Certifique-se de que a coluna 'resumo' existe no CSV
    if 'resumo' not in df_alvo.columns:
        return None

    textos = [str(t) for t in df_alvo['resumo'] if t != "Não Definido" and isinstance(t, str)]
    texto_completo = " ".join(textos)
    
    if not texto_completo.strip():
        return None

    # 2. Configurar Stopwords (Palavras para ignorar)
    stops = set(stopwords.words('portuguese'))
    # Adicionamos palavras comuns em artigos que não agregam valor semântico visual
    stops.update([
        "resumo", "trabalho", "artigo", "projeto", "objetivo", "resultados", 
        "conclusão", "estudo", "presente", "apresenta", "análise", "dados",
        "ser", "foi", "são", "através", "sobre", "entre", "pela", "pelo",
        "metodologia", "desenvolvimento", "pesquisa", "universidade", "ufrj",
        "para", "com", "dos", "das", "uma", "um", "percnt", "além", "disso", "partir",
        "desse", "estudante", "janeiro", "cada", "dessa", "realizado", "rio", "uso",
          "meio", "estudantes", "sendo", "et", "al"

    ])

    # 3. Gerar a Nuvem
    wordcloud = WordCloud(
        stopwords=stops,
        background_color="white",
        width=800,
        height=400,
        max_words=100, # Top 100 palavras
        colormap="viridis" 
    ).generate(texto_completo)
    
    return wordcloud

# --- CARREGAR OS NOSSOS DADOS ---
@st.cache_data
def carregar_dados(nome_arquivo):
    try:
        df = pd.read_csv(nome_arquivo, sep='\t')
        
        # Limpeza para os filtros e para a exibição
        cols_limpeza = ['tema', 'modalidade', 'area_principal', 'resumo', 'bibliografia', 'local', 'origem']
        for col in cols_limpeza:
            if col in df.columns:
                df[col] = df[col].fillna("Não Definido")
        return df
    
    except FileNotFoundError:
        st.error(f"ERRO: Ficheiro '{nome_arquivo}' não encontrado.")
        st.error("Rode o 'pipeline_geral.py' primeiro para gerar a base completa.")
        return pd.DataFrame()

# 1. Carregamos os dados PRIMEIRO
df = carregar_dados(ARQUIVO_MESTRE)

# --- TÍTULO DO APP ---
st.title("Análise de Trabalhos - SIAC 2025 (UFRJ Completa)")

if not df.empty:
    # Ordenando o DataFrame pelo 'id'
    if 'id' in df.columns:
        df['id'] = pd.to_numeric(df['id'], errors='coerce')
        df = df.sort_values(by='id').reset_index(drop=True)
   
    st.write(f"Base de dados unificada com {len(df)} trabalhos analisados.")
    
    # --- FILTROS ---
    st.sidebar.header("Filtros") 
    
    # Filtro: Origem (Centro)
    if 'origem' in df.columns:
        origens_unicas = ['Todas'] + sorted(df['origem'].unique())
        origem_selecionada = st.sidebar.selectbox("Filtrar por Origem (Centro):", origens_unicas)
    else:
        origem_selecionada = 'Todas'

    temas_unicos = ['Todos'] + sorted(df['tema'].unique())
    tema_selecionado = st.sidebar.selectbox("Filtrar por Tema da Sessão:", temas_unicos)

    modalidades_unicas = ['Todas'] + sorted(df['modalidade'].unique())
    modalidade_selecionada = st.sidebar.selectbox("Filtrar por Modalidade:", modalidades_unicas)
    
    areas_unicas = ['Todas'] + sorted(df['area_principal'].unique())
    area_selecionada = st.sidebar.selectbox("Filtrar por Área Principal:", areas_unicas)

    locais_unicos = ['Todos'] + sorted(df['local'].unique())
    local_selecionado = st.sidebar.selectbox("Filtrar por Local:", locais_unicos)

    termo_busca = st.sidebar.text_input("Buscar por Título ou Autor:")
    termo_busca_orientador = st.sidebar.text_input("Buscar por Orientador:")

    # --- LÓGICA DE FILTRAGEM ---
    df_filtrado = df.copy() 
    
    if origem_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['origem'] == origem_selecionada]

    if tema_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['tema'] == tema_selecionado]
    
    if modalidade_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['modalidade'] == modalidade_selecionada]
        
    if area_selecionada != 'Todas': 
        df_filtrado = df_filtrado[df_filtrado['area_principal'] == area_selecionada]
    
    if local_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['local'] == local_selecionado]
    
    if termo_busca:
        df_filtrado = df_filtrado[
            df_filtrado['titulo'].str.contains(termo_busca, case=False, na=False) |
            df_filtrado['autores'].str.contains(termo_busca, case=False, na=False)
        ]

    if termo_busca_orientador:
        df_filtrado = df_filtrado[
            df_filtrado['orientadores'].str.contains(termo_busca_orientador, case=False, na=False)
        ]

    # --- EXIBIR OS RESULTADOS ---
    st.header(f"Resultados: {len(df_filtrado)} trabalhos encontrados")
    
    # --- MÉTRICAS (KPIs) ---
    if not df_filtrado.empty:
        col1, col2, col3, col4 = st.columns(4)
        if 'origem' in df_filtrado.columns:
            col1.metric("Origens", df_filtrado['origem'].nunique())
        else:
            col1.metric("Temas", df_filtrado['tema'].nunique())
            
        col2.metric("Áreas", df_filtrado['area_principal'].nunique())
        col3.metric("Modalidades", df_filtrado['modalidade'].nunique())
        col4.metric("Locais", df_filtrado['local'].nunique())
    
    st.write("---") 
    
    # --- ABAS (TABS) ---
    tab1, tab2 = st.tabs(["📊 Visão Geral (Gráficos)", "📑 Tabela e Resumos"])

    with tab1:
        # --- GRÁFICOS ---
        if not df_filtrado.empty:
            st.subheader("Gráficos Rápidos")
            
            # --- INSERÇÃO: WORD CLOUD ---
            st.write("☁️ **Nuvem de Palavras (Baseado nos Resumos Filtrados)**")
            
            with st.spinner("Gerando nuvem de palavras..."):
                wc = gerar_nuvem_de_palavras(df_filtrado)
            
            if wc:
                fig_wc, ax_wc = plt.subplots(figsize=(10, 5))
                ax_wc.imshow(wc, interpolation='bilinear')
                ax_wc.axis("off")
                st.pyplot(fig_wc)
            else:
                st.warning("Não há texto suficiente nos resumos filtrados para gerar a nuvem.")
            
            st.write("---")
            # ---------------------------

            # Gráfico de Origem
            if origem_selecionada == 'Todas' and 'origem' in df_filtrado.columns:
                st.write("Trabalhos por Origem (Centro)")
                st.bar_chart(df_filtrado['origem'].value_counts())
                st.write("---")

            col1, col2 = st.columns(2)
            with col1:
                st.write("Trabalhos por Tema (Top 10)")
                contagem_temas = df_filtrado['tema'].value_counts().head(10)
                st.bar_chart(contagem_temas)

            with col2:
                st.write("Trabalhos por Modalidade")
                contagem_modalidade = df_filtrado['modalidade'].value_counts()
                st.bar_chart(contagem_modalidade)

            st.write("---")    
            st.subheader("Top 10 Orientadores (por nº de trabalhos)")
            
            # Limpeza: Alguns orientadores podem ser "Não Definido"
            orientadores_limpos = df_filtrado[df_filtrado['orientadores'] != "Não Definido"]
            
            if not orientadores_limpos.empty:
                # O "Arquivista" (Pandas) fazendo a contagem
                contagem_orientadores = orientadores_limpos['orientadores'].value_counts().head(10)
                st.bar_chart(contagem_orientadores)
            else:
                st.write("Nenhum orientador definido nos dados filtrados.")

            st.write("---")
            st.subheader("Mapa de Calor: Concentração de Sessões")

            # --- MAPA DE CALOR (HEATMAP) ---
            if 'data' in df_filtrado.columns and 'horario' in df_filtrado.columns:
                df_heat = df_filtrado.copy()
                
                try:
                    # Limpeza de Dia e Hora
                    df_heat['dia_semana'] = df_heat['data'].apply(lambda x: x.split('/')[-1].strip() if isinstance(x, str) and '/' in x else x)
                    df_heat['hora_inicio'] = df_heat['horario'].apply(lambda x: x.split('às')[0].strip() if isinstance(x, str) and 'às' in x else x)
                    
                    # Agrupar
                    heatmap_data = df_heat.groupby(['dia_semana', 'hora_inicio']).size().reset_index(name='quantidade')
                    
                    # Ordenar
                    ordem_dias = ['SEG', 'TER', 'QUA', 'QUI', 'SEX']
                    heatmap_data['dia_semana'] = pd.Categorical(heatmap_data['dia_semana'], categories=ordem_dias, ordered=True)
                    heatmap_data = heatmap_data.sort_values(['dia_semana', 'hora_inicio'])

                    # Plotly
                    import plotly.express as px

                    fig = px.density_heatmap(
                        heatmap_data, 
                        x="dia_semana", 
                        y="hora_inicio", 
                        z="quantidade", 
                        title="Densidade de Trabalhos por Dia e Horário",
                        labels={"dia_semana": "Dia da Semana", "hora_inicio": "Horário de Início", "quantidade": "Nº de Trabalhos"},
                        color_continuous_scale="Viridis",
                        text_auto=True 
                    )
                    
                    fig.update_layout(
                        xaxis_title=None, 
                        yaxis_title="Horário de Início",
                        coloraxis_showscale=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                except Exception as e:
                    st.warning(f"Não foi possível gerar o mapa de calor. Erro: {e}")
            else:
                st.info("Colunas de 'data' ou 'horario' não encontradas para gerar o mapa de calor.")

        else:
            st.write("Nenhum dado selecionado para exibir gráficos.")

    with tab2:
        # --- TABELA DE DADOS ---
        st.subheader("Dados Filtrados")
        colunas_para_exibir = [
            'id', 'origem', 'titulo', 'autores', 'orientadores', 'modalidade', 
            'tema', 'area_principal', 'data', 'horario', 'local'
        ]
        colunas_finais = [col for col in colunas_para_exibir if col in df_filtrado.columns]
        st.dataframe(df_filtrado[colunas_finais])
        
        # --- DETALHE DO RESUMO ---
        if not df_filtrado.empty:
            st.write("---")
            st.header("Ver detalhes do Resumo")
            
            df_filtrado['id_e_titulo'] = df_filtrado['id'].astype(str) + " - " + df_filtrado['titulo']
            lista_opcoes = df_filtrado['id_e_titulo'].unique()
            opcao_selecionada = st.selectbox("Selecione um trabalho para ler o resumo:", lista_opcoes)
            
            if len(lista_opcoes) > 0:
                trabalho_detalhe = df_filtrado[df_filtrado['id_e_titulo'] == opcao_selecionada].iloc[0]
                
                st.subheader(trabalho_detalhe['titulo'])
                
                if 'origem' in trabalho_detalhe:
                    st.caption(f"📍 Origem: {trabalho_detalhe['origem']}")
                
                st.write(f"**Autores:** {trabalho_detalhe['autores']}")
                st.write(f"**Orientadores:** {trabalho_detalhe['orientadores']}")
                
                st.write(f"**Resumo:**")
                st.info(trabalho_detalhe['resumo'])
                
                if 'bibliografia' in trabalho_detalhe and trabalho_detalhe['bibliografia'] != "Não Definido":
                    st.write("**Bibliografia:**")
                    st.caption(trabalho_detalhe['bibliografia'])

else:
    st.warning("A base de dados não foi carregada. Verifique os erros acima.")
