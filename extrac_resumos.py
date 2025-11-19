# extrac_resumos.py (CORRIGIDO V19 - FIM DO SANGRAMENTO)
# -----------------------------------------------------------
# SCRIPT 2
# -----------------------------------------------------------
import fitz  # PyMuPDF
import pandas as pd
import re
import sys

# --- O SEU CAMINHO ---
PASTA_DO_PROJETO = r"C:\Users\lcarl\Desktop\PSIAC6" # <-- Verifique se esta pasta está correta
arquivo_resumos_pdf = PASTA_DO_PROJETO + r"\2025_CT-CAD_RESUMOS.pdf"
arquivo_csv_saida_2 = PASTA_DO_PROJETO + r"\resumos_siac_ct_FINAL.csv" # <-- Nome de saída final

try:
    dados_dos_resumos = []
    
    # --- LÓGICA DE REGEX CORRIGIDA (V19) ---
    # 1. Regex para os campos ANTES do ID
    regex_modalidade = re.compile(r"MODALIDADE DE APRESENTAÇÃO\s*(.*?)$", re.IGNORECASE | re.MULTILINE)
    regex_area = re.compile(r"ÁREA PRINCIPAL\s*(.*?)$", re.MULTILINE) # 'Á' com acento

    # 2. Regex para os campos DEPOIS do ID
    STOP_PATTERN = r"(T[IÍ]TULO\s*:|AUTOR\(?(?:ES)?\)\s*:|ORIENTADOR\(?(?:ES)?\)\s*:|RESUMO\s*:|BIBLIOGRAFIA\s*:|$)"
    regex_titulo = re.compile(r"T[IÍ]TULO\s*:(.*?)(?=" + STOP_PATTERN + ")", re.DOTALL | re.IGNORECASE)
    regex_autores = re.compile(r"AUTOR\(?(?:ES)?\)\s*:(.*?)(?=" + STOP_PATTERN + ")", re.DOTALL | re.IGNORECASE)
    regex_orientadores = re.compile(r"ORIENTADOR\(?(?:ES)?\)\s*:(.*?)(?=" + STOP_PATTERN + ")", re.DOTALL | re.IGNORECASE)
    
    # 3. Regex para o Resumo e Bibliografia (V19 FIX)
    regex_resumo_explicito = re.compile(r"RESUMO\s*:(.*?)(?=" + STOP_PATTERN + ")", re.DOTALL | re.IGNORECASE)
    
    # --- ALTERAÇÃO 1 (V19) ---
    # Padrão para parar ANTES da metadata do próximo artigo
    FIM_DO_ARTIGO_PATTERN = r"(MODALIDADE DE APRESENTAÇÃO|ÁREA PRINCIPAL|$)"
    
    # --- ALTERAÇÃO 2 (V19) ---
    regex_bibliografia = re.compile(r"BIBLIOGRAFIA\s*:(.*?)(?=" + FIM_DO_ARTIGO_PATTERN + ")", re.DOTALL | re.IGNORECASE)

    # --- ALTERAÇÃO 3 (V19) ---
    regex_resumo_implicito = re.compile(r"ORIENTADOR\(?(?:ES)?\)\s*:.*?\n(.*?)(?=BIBLIOGRAFIA\s*:|" + FIM_DO_ARTIGO_PATTERN + ")", re.DOTALL | re.IGNORECASE)


    print(f"\nSCRIPT 2 (V19): Abrindo '{arquivo_resumos_pdf}'...")
    doc = fitz.open(arquivo_resumos_pdf)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    
    artigos_fatiados = re.split(r"ARTIGO:\s*(\d+)", full_text, flags=re.IGNORECASE)
    for i in range(1, len(artigos_fatiados), 2):
        id_artigo = artigos_fatiados[i].strip()
        texto_artigo_anterior = artigos_fatiados[i-1] 
        texto_artigo_atual = artigos_fatiados[i+1]      
        info_artigo = {"id": id_artigo} 

        # --- LÓGICA DE BUSCA V19 ---
        # 1. Procurar MODALIDADE e ÁREA no bloco ANTERIOR
        match_mod = regex_modalidade.search(texto_artigo_anterior)
        match_are = regex_area.search(texto_artigo_anterior)
        
        # 2. Procurar o RESTO no bloco ATUAL
        match_tit = regex_titulo.search(texto_artigo_atual)
        match_aut = regex_autores.search(texto_artigo_atual)
        match_ori = regex_orientadores.search(texto_artigo_atual)
        match_bib = regex_bibliografia.search(texto_artigo_atual) # Usa a V19
        
        # 3. Lógica CORRIGIDA para o Resumo
        match_res = regex_resumo_explicito.search(texto_artigo_atual)
        if not match_res:
            match_res = regex_resumo_implicito.search(texto_artigo_atual) # Usa a V19
        
        # Limpar e salvar (só salva se encontrar)
        if match_mod: info_artigo["modalidade"] = " ".join(match_mod.group(1).split()).strip(" :")
        if match_are: info_artigo["area_principal"] = " ".join(match_are.group(1).split()).strip(" :")
        if match_tit: info_artigo["titulo"] = " ".join(match_tit.group(1).split()).strip()
        if match_aut: info_artigo["autores"] = " ".join(match_aut.group(1).split()).strip()
        if match_ori: info_artigo["orientadores"] = " ".join(match_ori.group(1).split()).strip()
        if match_res: info_artigo["resumo"] = " ".join(match_res.group(1).split()).strip()
        if match_bib: info_artigo["bibliografia"] = " ".join(match_bib.group(1).split()).strip()

        dados_dos_resumos.append(info_artigo)
    
    if dados_dos_resumos:
        df_resumos = pd.DataFrame(dados_dos_resumos)
        print(f"SCRIPT 2 (V19): SUCESSO. {len(df_resumos)} resumos extraídos.")
        
        colunas_ordenadas = ['id', 'titulo', 'autores', 'orientadores', 'modalidade', 'area_principal', 'resumo', 'bibliografia']
        colunas_finais = [col for col in colunas_ordenadas if col in df_resumos.columns]
        colunas_extras = [col for col in df_resumos.columns if col not in colunas_finais]
        df_resumos = df_resumos[colunas_finais + colunas_extras]
        
        df_resumos.to_csv(arquivo_csv_saida_2, index=False, encoding='utf-8-sig', sep='\t')
        print(f"SCRIPT 2 (V19): Ficheiro salvo em '{arquivo_csv_saida_2}'")
    else:
        print("SCRIPT 2 (V19): Nenhum resumo foi extraído.")
        
except FileNotFoundError:
    print(f"\nERRO: O ficheiro não foi encontrado em '{arquivo_resumos_pdf}'.")
except Exception as e:
    print(f"SCRIPT 2 (V19): Ocorreu um erro inesperado: {e}")