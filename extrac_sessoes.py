# extrac_sessoes.py (VERSÃO FUNÇÃO)
# -----------------------------------------------------------
# SCRIPT 1
# -----------------------------------------------------------
import fitz  # PyMuPDF
import pandas as pd
import re
import os

PASTA_DO_PROJETO = os.getcwd()# Pega a pasta atual

def processar_sessoes(sigla):
    print(f"\n--- [SESSÕES] Iniciando extração (V13) para: {sigla} ---")
    
    # 1. Configurar nomes de arquivos dinâmicos
    nome_pdf = f"2025_{sigla.upper()}-PROG_SESSOES.pdf"
    nome_csv_saida = f"programacao_siac_{sigla.lower()}_FINAL.csv"
    
    # Caminhos: Input e Output na pasta 'pdfs'
    arquivo_programacao = os.path.join(PASTA_DO_PROJETO, "pdfs", nome_pdf)
    arquivo_csv_saida_1 = os.path.join(PASTA_DO_PROJETO, "pdfs", nome_csv_saida)

    try:
        dados_extraidos_1 = []
        sessao_atual = {"tema": "Não definido", "local_raw": "Não definido", "data": "Não definido", "horario": "Não definido"}

        # --- REGEX ---
        regex_tema_normal = re.compile(r"^\w+\.\s(.*?)\s\|") 
        regex_tema_extra = re.compile(r"^(.*?)\(atividade extra\)\.?") 
        
        regex_data = re.compile(r"(\d{2} Sep \/ \w{3})")
        regex_horario_completo = re.compile(r"(\d{1,2}:\d{2}\s*às\s*.*)", re.IGNORECASE)
        regex_horario_inicio = re.compile(r"(\d{1,2}:\d{2}\s*às)$", re.IGNORECASE)
        
        primeira_parte_horario = None 

        # Abrir PDF
        doc = fitz.open(arquivo_programacao)
        
        for num_pagina, page in enumerate(doc):
            page_text = page.get_text("text")
            linhas = page_text.split('\n')
            
            for linha in linhas:
                linha = linha.strip()
                
                # --- LÓGICA DO "STATE MACHINE" (Horário Partido) ---
                if primeira_parte_horario:
                    sessao_atual["horario"] = primeira_parte_horario + " " + linha
                    primeira_parte_horario = None 
                    continue
                # --- FIM DA LÓGICA DE ESTADO ---

                # 1. Procurar por TEMA
                match_normal = regex_tema_normal.search(linha)
                match_extra = regex_tema_extra.search(linha)
                if match_normal:
                    sessao_atual = {"tema": match_normal.group(1).strip(), "local_raw": "Não definido", "data": "Não definido", "horario": "Não definido"}
                    continue 
                elif match_extra:
                    sessao_atual = {"tema": match_extra.group(1).strip(), "local_raw": "Não definido", "data": "Não definido", "horario": "Não definido"}
                    continue 

                # 2. Procurar por LOCAL
                if linha.startswith("Local:"):
                    local_limpo = linha.replace("Local:", "").strip()
                    if local_limpo:
                        sessao_atual["local_raw"] = local_limpo
                    else:
                        sessao_atual["local_raw"] = None
                    continue

                # 3. Procurar por DATA
                match_data = regex_data.search(linha)
                if match_data:
                    sessao_atual["data"] = match_data.group(1).strip()
                    continue 

                # 4. Procurar por HORÁRIO
                match_completo = regex_horario_completo.search(linha)
                match_inicio = regex_horario_inicio.search(linha)
                
                if match_completo:
                    sessao_atual["horario"] = match_completo.group(1).strip()
                    continue
                elif match_inicio:
                    primeira_parte_horario = match_inicio.group(1).strip()
                    continue

                # 5. Procurar por TRABALHO
                if linha.startswith("TRABALHO:"):
                    trabalho_info = {"id": None, "titulo": None}
                    
                    id_match = re.search(r"TRABALHO:\s*(\d+)", linha)
                    titulo_match = re.search(r"TITULO:\s*(.*?)(?=AUTORES E ORIENTADORES:|$)", linha)
                    
                    if id_match: trabalho_info["id"] = id_match.group(1)
                    if titulo_match: trabalho_info["titulo"] = titulo_match.group(1).strip()
                    
                    trabalho_info.update(sessao_atual) 
                    dados_extraidos_1.append(trabalho_info)
        doc.close()
        
        if dados_extraidos_1:
            df1 = pd.DataFrame(dados_extraidos_1)
            
            # Renomear 'local_raw' para 'local'
            df1 = df1.rename(columns={"local_raw": "local"})
            
            colunas_ordenadas = ['id', 'tema', 'titulo', 'data', 'horario', 'local']
            colunas_finais = [col for col in colunas_ordenadas if col in df1.columns]
            df1 = df1[colunas_finais]
            
            df1.to_csv(arquivo_csv_saida_1, index=False, encoding='utf-8-sig')
            print(f"   [OK] Sessões extraídas: {len(df1)} registros. Salvo em: {nome_csv_saida}")
            return True
        else:
            print(f"   [AVISO] Nenhuma sessão encontrada para {sigla}.")
            return False
            
    except FileNotFoundError:
        print(f"   [ERRO] Arquivo PDF não encontrado em 'pdfs/': {nome_pdf}")
        return False
    except Exception as e:
        print(f"   [ERRO] Falha em sessoes ({sigla}): {e}")
        return False

# Bloco para teste
if __name__ == "__main__":
    processar_sessoes("CT")