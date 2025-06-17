#!/usr/bin/env python3
"""
Script de teste para verificar o processamento de tags nos arquivos GTD
"""

import sys
from pathlib import Path

# Adiciona o diretório do projeto ao path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from models.gtd_processor import GTDProcessor

def test_tag_processing():
    """Testa o processamento de tags em um arquivo GTD"""
      # Arquivo de teste
    # test_file = "temp_data/002171_230828_101630.GTD" # with tags
    test_file = "temp_data/002843_250207_070200.GTD" # without tags
    
    print(f"=== Teste de Processamento de Tags ===")
    print(f"Arquivo: {test_file}")
    print()
    
    # Cria o processador
    processor = GTDProcessor()
    
    try:
        # Processa o arquivo
        processor.process_file(test_file)
        
        print("\n=== Resultado do Processamento ===")
        print(f"Total de canais processados: {len(processor.channels)}")
        print()
        
        # Lista todos os canais encontrados
        for channel_id, channel in processor.channels.items():
            print(f"Canal ID: '{channel_id}'")
            print(f"  - Unidade: {channel.unit}")
            print(f"  - Amostras: {len(channel.timestamps)}")
            print()
            
        # Verifica se algum canal tem tag no ID
        channels_with_tags = [ch_id for ch_id in processor.channels.keys() if '_' in str(ch_id)]
        
        if channels_with_tags:
            print(f"Canais com tags detectados ({len(channels_with_tags)}):")
            for ch_id in channels_with_tags:
                print(f"  - {ch_id}")
        else:
            print("Nenhum canal com tag foi detectado.")
            
    except Exception as e:
        print(f"Erro durante o processamento: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tag_processing()
