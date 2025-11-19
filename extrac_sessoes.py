# extrac_sessoes.py (V13 - O "State Machine" Corrigido)
# -----------------------------------------------------------
# SCRIPT 1
# -----------------------------------------------------------
import fitz  # PyMuPDF
import pandas as pd
import re
import sys

# --- O SEU CAMINHO ---
PASTA_DO_PROJETO = r"C:\Users\lcarl\Desktop\PSIAC6" # <-- Verifique se esta pasta está correta
arquivo_programacao = PASTA_DO_PROJETO + r"\2025_CT-PROG_SESSOES.pdf"
arquivo_csv_saida_1 = PASTA_DO_PROJETO + r"\programacao_siac_ct_FINAL.csv" # Nome de saída final

try:
    dados_extraidos_1 = []
    sessao_atual = {"tema": "Não definido", "local_raw": "Não definido", "data": "Não definido", "horario": "Não definido"}

    # --- CORREÇÃO 1 (655 Linhas) ---
    regex_tema_normal = re.compile(r"^\w+\.\s(.*?)\s\|") # P/ "Oral. BIOTECNOLOGIA |"
    regex_tema_extra = re.compile(r"^(.*?)\(atividade extra\)\.?") # P/ "Visita Guiada (atividade extra)"
    
    # --- CORREÇÃO 2 (Horário Partido) ---
    regex_data = re.compile(r"(\d{2} Sep \/ \w{3})")
    # Regex para um horário "completo" numa só linha
    regex_horario_completo = re.compile(r"(\d{1,2}:\d{2}\s*às\s*.*)", re.IGNORECASE)
    # Regex para um horário "partido" (que termina em 'às')
    regex_horario_inicio = re.compile(r"(\d{1,2}:\d{2}\s*às)$", re.IGNORECASE)
    
    # A nossa variável de "estado" para o horário
    primeira_parte_horario = None 

    doc = fitz.open(arquivo_programacao)
    print(f"\nSCRIPT 1 (V13): Abrindo '{arquivo_programacao}'...")
    for num_pagina, page in enumerate(doc):
        page_text = page.get_text("text")
        linhas = page_text.split('\n')
        
        for linha in linhas:
            linha = linha.strip()
            
            # --- LÓGICA DO "STATE MACHINE" (Horário Partido) ---
            # Se estávamos à espera do fim do horário, esta é a linha
            if primeira_parte_horario:
                sessao_atual["horario"] = primeira_parte_horario + " " + linha
                primeira_parte_horario = None # Resetar o estado
                continue
            # --- FIM DA LÓGICA DE ESTADO ---

            # 1. Procurar por TEMA (Normal ou Extra)
            match_normal = regex_tema_normal.search(linha)
            match_extra = regex_tema_extra.search(linha)
            if match_normal:
                sessao_atual = {"tema": match_normal.group(1).strip(), "local_raw": "Não definido", "data": "Não definido", "horario": "Não definido"}
                continue 
            elif match_extra:
                sessao_atual = {"tema": match_extra.group(1).strip(), "local_raw": "Não definido", "data": "Não definido", "horario": "Não definido"}
                continue 

            # 2. Procurar por LOCAL (Como pediu: a string inteira)
            if linha.startswith("Local:"):
                local_limpo = linha.replace("Local:", "").strip()
                if local_limpo:
                    sessao_atual["local_raw"] = local_limpo
                else:
                    sessao_atual["local_raw"] = None # Guardar como None
                continue

            # 3. Procurar por DATA
            match_data = regex_data.search(linha)
            if match_data:
                sessao_atual["data"] = match_data.group(1).strip()
                continue 

            # 4. Procurar por HORÁRIO (Completo ou Partido)
            match_completo = regex_horario_completo.search(linha)
            match_inicio = regex_horario_inicio.search(linha)
            
            if match_completo:
                # Encontrámos um horário completo (ex: 13:00 às 14:00)
                sessao_atual["horario"] = match_completo.group(1).strip()
                continue
            elif match_inicio:
                # Encontrámos um horário partido (ex: 14:30 às)
                primeira_parte_horario = match_inicio.group(1).strip() # Guardar o estado
                continue
            # --- FIM DA CORREÇÃO ---

            # 5. Procurar por TRABALHO
            if linha.startswith("TRABALHO:"):
                # Foco só em ID e Título (Como pediu)
                trabalho_info = {"id": None, "titulo": None}
                
                id_match = re.search(r"TRABALHO:\s*(\d+)", linha)
                titulo_match = re.search(r"TITULO:\s*(.*?)(?=AUTORES E ORIENTADORES:|$)", linha)
                
                if id_match: trabalho_info["id"] = id_match.group(1)
                if titulo_match: trabalho_info["titulo"] = titulo_match.group(1).strip()
                
                trabalho_info.update(sessao_atual) # Aplicar a sessão
                dados_extraidos_1.append(trabalho_info)
    doc.close()
    
    if dados_extraidos_1:
        df1 = pd.DataFrame(dados_extraidos_1)
        print(f"SCRIPT 1 (V13): SUCESSO. {len(df1)} trabalhos extraídos.") # <-- Deve dar 655
        
        # Renomear 'local_raw' para 'local' (Como pediu)
        df1 = df1.rename(columns={"local_raw": "local"})
        
        # --- COLUNAS ATUALIZADAS (Como pediu) ---
        colunas_ordenadas = ['id', 'tema', 'titulo', 'data', 'horario', 'local']
        
        colunas_finais = [col for col in colunas_ordenadas if col in df1.columns]
        df1 = df1[colunas_finais]
        
        df1.to_csv(arquivo_csv_saida_1, index=False, encoding='utf-8-sig')
        print(f"SCRIPT 1 (V13): Ficheiro salvo em '{arquivo_csv_saida_1}'")
        print("\nAmostra (V13):")
        print(df1.head()) 
    else:
        print("SCRIPT 1 (V13): Nenhum dado extraído.")
        
except FileNotFoundError:
    print(f"\nERRO: O ficheiro não foi encontrado em '{arquivo_programacao}'.")
except Exception as e:
    print(f"SCRIPT 1 (V13): Ocorreu um erro inesperado: {e}")