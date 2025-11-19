#import google.generativeai as genai
#import os

# --- IMPORTANTE ---
# Cole sua API key aqui dentro das aspas "SUA_CHAVE"

API_KEY = "SUA_CHAVE" 

try:
    genai.configure(api_key=API_KEY)
    
    print("\n--- Modelos disponíveis para sua chave (que suportam 'generateContent'): ---")
    
    # Lista apenas os modelos que funcionam para o nosso caso
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
            
    print("--- Fim da lista ---\n")

except Exception as e:
    print(f"\n--- Ocorreu um erro ao buscar os modelos ---")
    print(f"Erro: {e}")
    print("\nVerifique se sua API_KEY está correta.")