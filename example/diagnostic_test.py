#!/usr/bin/env python3
"""
Script de diagnóstico para problemas do Streamlit Cloud
"""

import sys
import os
import locale
from pathlib import Path

# Adiciona o diretório do projeto ao path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from models.gtd_processor import GTDProcessor

def diagnostic_test():
    """Executa testes de diagnóstico para identificar problemas do Streamlit Cloud"""
    
    print("=== DIAGNÓSTICO STREAMLIT CLOUD ===")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Locale: {locale.getlocale()}")
    print(f"File system encoding: {sys.getfilesystemencoding()}")
    print(f"Default encoding: {sys.getdefaultencoding()}")
    print()
    
    # Testa arquivo com tags
    test_file_with_tags = "temp_data/002171_230828_101630.GTD"
    # Testa arquivo sem tags  
    test_file_no_tags = "temp_data/002843_250207_070200.GTD"
    
    for test_file, description in [(test_file_with_tags, "COM TAGS"), (test_file_no_tags, "SEM TAGS")]:
        if not os.path.exists(test_file):
            print(f"❌ Arquivo não encontrado: {test_file}")
            continue
            
        print(f"=== TESTE: {description} ===")
        print(f"Arquivo: {test_file}")
        
        try:
            # Verifica se o arquivo pode ser lido
            with open(test_file, 'r', encoding='utf-8') as f:
                first_lines = f.readlines()[:30]
            print(f"✓ Arquivo lido com sucesso (primeiras 30 linhas)")
            
            # Procura linha Tag
            tag_line = None
            for i, line in enumerate(first_lines):
                if line.strip().startswith('Tag'):
                    tag_line = line
                    print(f"✓ Linha Tag encontrada na linha {i}: {repr(line.strip())}")
                    break
            
            if tag_line is None:
                print("⚠️ Linha Tag não encontrada nas primeiras 30 linhas")
            
            # Testa processamento
            processor = GTDProcessor()
            processor.process_file(test_file)
            
            print(f"✓ Processamento concluído")
            print(f"  - Total de canais: {len(processor.channels)}")
            
            # Verifica se existem canais com tags
            channels_with_tags = [ch_id for ch_id in processor.channels.keys() if '_' in str(ch_id)]
            channels_without_tags = [ch_id for ch_id in processor.channels.keys() if '_' not in str(ch_id)]
            
            print(f"  - Canais com tags: {len(channels_with_tags)}")
            print(f"  - Canais sem tags: {len(channels_without_tags)}")
            
            if channels_with_tags:
                print("  - Exemplos com tags:")
                for ch_id in channels_with_tags[:3]:  # Mostra até 3 exemplos
                    print(f"    * {ch_id}")
            
            if channels_without_tags:
                print("  - Exemplos sem tags:")
                for ch_id in channels_without_tags[:3]:  # Mostra até 3 exemplos
                    print(f"    * {ch_id}")
                    
        except Exception as e:
            print(f"❌ Erro durante o processamento: {e}")
            import traceback
            traceback.print_exc()
        
        print()
        print("-" * 50)
        print()

if __name__ == "__main__":
    diagnostic_test()
