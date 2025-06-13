import os
import re
import pandas as pd
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Union
from .Channel import Channel  # Importa a classe Channel do módulo Channel




class GTDProcessor:
    """
    Classe para processar arquivos GTD e convertê-los em formato Excel.
    Pode processar múltiplos arquivos GTD e combiná-los em uma única saída.
    """
    def __init__(self):
        """Inicializa o processador GTD"""
        self.channels = {}  # Dicionário para armazenar objetos Channel por ID
        self.metadata = {}  # Dicionário para armazenar metadados
    
    def _parse_header(self, lines: List[str]) -> int:
        """
        Processa o cabeçalho do arquivo GTD e armazena metadados relevantes.
        
        Args:
            lines: Lista de linhas do arquivo GTD
            
        Returns:
            Índice da linha onde começa os dados de amostragem
        """
        sampling_data_line_index = 0
        header_section = True
        
        for i, line in enumerate(lines):
            if line.strip() == "Sampling Data":
                sampling_data_line_index = i
                break
            
            # Processa metadados do cabeçalho
            if header_section and line.strip():
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    self.metadata[key] = value
        
        return sampling_data_line_index
    
    def _parse_channels(self, lines: List[str], sampling_data_line_index: int) -> None:
        """
        Processa as definições de canais do arquivo GTD e cria objetos Channel.
        
        Args:
            lines: Lista com todas as linhas do arquivo
            sampling_data_line_index: Índice da linha "Sampling Data"
        """
        # Identifica as linhas de definição de canal com base em palavras-chave
        ch_line_idx = None
        unit_line_idx = None
        kind_line_idx = None
        
        # Procura as linhas de definição olhando algumas linhas antes de "Sampling Data"
        for i in range(sampling_data_line_index - 10, sampling_data_line_index):
            if i < 0 or i >= len(lines):
                continue
                
            line = lines[i].strip()
            parts = line.split('\t')
            
            if parts and parts[0].strip() == "Ch":
                ch_line_idx = i
            elif parts and parts[0].strip() == "Unit":
                unit_line_idx = i
            elif parts and parts[0].strip() == "Kind":
                kind_line_idx = i
        
        # Verifica se temos todas as informações necessárias
        if None in (ch_line_idx, unit_line_idx, kind_line_idx):
            print("Aviso: Não foi possível identificar todas as linhas de definição de canais.")
            print(f"Ch: {ch_line_idx}, Unit: {unit_line_idx}, Kind: {kind_line_idx}")
            return
        
        # Obtém as linhas específicas
        ch_parts = lines[ch_line_idx].strip().split('\t')
        unit_parts = lines[unit_line_idx].strip().split('\t')
        kind_parts = lines[kind_line_idx].strip().split('\t')
        
        # Mapeia canais para suas posições
        # Dicionário: {posição -> (channel_id, kind, unit)}
        channel_map = {}
        
        # A primeira coluna é geralmente um rótulo, então começamos do índice 1
        for i in range(1, len(ch_parts)):
            # Ignora colunas vazias
            if i >= len(ch_parts) or not ch_parts[i].strip():
                continue
            
            try:
                # Obtém o ID do canal a partir da linha "Ch"
                channel_id_str = ch_parts[i].strip()
                
                # Converte para inteiro, se possível
                if channel_id_str.isdigit():
                    channel_id = int(channel_id_str)
                else:
                    # Se não for um dígito, usa a string como identificador
                    channel_id = channel_id_str
                
                # Obtém a unidade e o tipo (Min/Max)
                unit = unit_parts[i].strip() if i < len(unit_parts) else ""
                kind = kind_parts[i].strip() if i < len(kind_parts) else ""
                
                # Cria o canal se ainda não existir
                if channel_id not in self.channels:
                    self.channels[channel_id] = Channel(channel_id, unit)
                
                # Armazena o mapeamento da coluna
                channel_map[i] = (channel_id, kind, unit)
                
            except (ValueError, IndexError) as e:
                print(f"Aviso: Erro ao processar canal na coluna {i}: {e}")
        
        self.channel_map = channel_map
        print(f"Processados {len(set([ch_id for ch_id, _, _ in channel_map.values()]))} canais únicos.")
    
    def _parse_data(self, data_lines: List[str]) -> None:
        """
        Processa as linhas de dados e adiciona as amostras aos canais correspondentes.
        
        Args:
            data_lines: Lista de linhas contendo os dados de amostragem
        """
        # Cria um dicionário para armazenar valores Min/Max temporários
        # Formato: {(timestamp, channel_id) -> {"min": valor, "max": valor}}
        temp_values = {}
        
        for line in data_lines:
            parts = line.strip().split('\t')
            
            # A primeira coluna é o timestamp
            if len(parts) < 2:
                continue
            
            try:
                # Converte a string de timestamp para datetime
                timestamp_str = parts[0].strip()
                timestamp = datetime.strptime(timestamp_str, "%Y/%m/%d %H:%M:%S")
                
                # Itera através das colunas de dados
                for i in range(1, len(parts)):
                    if i not in self.channel_map:
                        continue
                    
                    channel_id, kind, _ = self.channel_map[i]
                    
                    # Pula se não houver valor
                    if not parts[i].strip():
                        continue
                    
                    # Converte para float
                    try:
                        value = float(parts[i].strip())
                    except ValueError:
                        continue
                    
                    key = (timestamp, channel_id)
                    
                    # Inicializa o dicionário para este par timestamp/canal se necessário
                    if key not in temp_values:
                        temp_values[key] = {"min": None, "max": None}
                    
                    # Armazena o valor de acordo com o tipo (Min/Max)
                    if kind.lower() == "min":
                        temp_values[key]["min"] = value
                    elif kind.lower() == "max":
                        temp_values[key]["max"] = value
                
            except ValueError as e:
                print(f"Erro ao processar linha: {line.strip()} - {e}")
        
        # Adiciona pares completos de Min/Max aos canais
        samples_added = 0
        for (timestamp, channel_id), values in temp_values.items():
            min_value = values.get("min")
            max_value = values.get("max")
            
            if channel_id in self.channels and min_value is not None and max_value is not None:
                self.channels[channel_id].add_sample(timestamp, min_value, max_value)
                samples_added += 1
        
        print(f"Adicionadas {samples_added} amostras aos canais.")
    
    def process_file(self, filepath: str) -> None:
        """
        Processa um único arquivo GTD.
        
        Args:
            filepath: Caminho para o arquivo GTD
        """
        print(f"Processando arquivo: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Encontra a linha de início dos dados de amostragem
        sampling_data_line_index = self._parse_header(lines)
        
        # Verifica se encontramos a seção "Sampling Data"
        if sampling_data_line_index == 0:
            raise ValueError("Formato de arquivo GTD inválido. 'Sampling Data' não encontrado.")
        
        # Processa as definições de canais
        self._parse_channels(lines, sampling_data_line_index)
        
        # Verifica se temos canais definidos
        if not hasattr(self, 'channel_map') or not self.channel_map:
            raise ValueError("Não foi possível processar as definições de canais.")
        
        # Processa os dados de amostragem
        data_lines = lines[sampling_data_line_index + 1:]
        self._parse_data(data_lines)
    
    def process_multiple_files(self, filepaths: List[str]) -> None:
        """
        Processa múltiplos arquivos GTD.
        
        Args:
            filepaths: Lista de caminhos para arquivos GTD
        """
        for filepath in filepaths:
            self.process_file(filepath)
    
    def export_to_excel(self, output_filepath: str) -> None:
        """
        Exporta os dados processados para um arquivo Excel.
        
        Args:
            output_filepath: Caminho para o arquivo Excel de saída
        """
        # Se não tiver extensão .xlsx, adiciona
        if not output_filepath.lower().endswith('.xlsx'):
            output_filepath += '.xlsx'
        
        # Cria um DataFrame vazio
        df = pd.DataFrame()
        
        # Função auxiliar para ordenação dos canais
        def channel_sort_key(item):
            # O item é um tuple (channel_id, channel_object)
            channel_id = item[0]
            # Se for string, tentamos converter para inteiro para comparação
            if isinstance(channel_id, str) and channel_id.isdigit():
                return (0, int(channel_id))  # Tupla com prioridade 0 para números
            if isinstance(channel_id, int):
                return (0, channel_id)  # Tupla com prioridade 0 para números
            # Para strings não-numéricas, retorna com prioridade 1
            return (1, str(channel_id))  # Garante comparação apenas entre strings
        
        # Primeiro, identifique o canal com mais amostras para inicializar o DataFrame
        max_samples = 0
        init_channel_id = None
        init_channel = None
        
        for channel_id, channel in self.channels.items():
            if len(channel.timestamps) > max_samples:
                max_samples = len(channel.timestamps)
                init_channel_id = channel_id
                init_channel = channel
        
        if init_channel is None:
            print("Aviso: Nenhum canal com dados foi encontrado.")
            return
            
        # Inicializa o DataFrame com o canal que tem mais amostras
        channel_data = init_channel.get_data_as_dict()
        df['Timestamp'] = channel_data['Timestamp']
        
        min_col = f"Ch{init_channel_id}_Min_{init_channel.unit}"
        max_col = f"Ch{init_channel_id}_Max_{init_channel.unit}"
        df[min_col] = channel_data[min_col]
        df[max_col] = channel_data[max_col]
        
        # Adiciona os demais canais ao DataFrame
        for channel_id, channel in sorted(self.channels.items(), key=channel_sort_key):
            # Pula o canal inicializador
            if channel_id == init_channel_id:
                continue
                
            # Verifica se o canal tem dados
            if len(channel.timestamps) == 0:
                print(f"Aviso: Canal {channel_id} não possui amostras, ignorando.")
                continue
                
            # Obtém dicionário de dados do canal
            channel_data = channel.get_data_as_dict()
            
            # Adiciona colunas de min e max, verificando comprimento
            min_col = f"Ch{channel_id}_Min_{channel.unit}"
            max_col = f"Ch{channel_id}_Max_{channel.unit}"
            
            # Se o tamanho dos dados do canal for diferente do DataFrame, avisa mas não adiciona
            if len(channel_data[min_col]) != len(df):
                print(f"Aviso: Canal {channel_id} tem um número diferente de amostras ({len(channel_data[min_col])}) em relação ao DataFrame ({len(df)}). Este canal será ignorado.")
                continue
                
            df[min_col] = channel_data[min_col]
            df[max_col] = channel_data[max_col]
        
        # Cria a planilha Excel e salva
        with pd.ExcelWriter(output_filepath, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Dados GTD')
            
            # Adiciona uma aba de metadados
            metadata_df = pd.DataFrame(list(self.metadata.items()), columns=['Chave', 'Valor'])
            metadata_df.to_excel(writer, index=False, sheet_name='Metadados')
            
            # Adiciona uma aba de informações dos canais
            channel_info = []
            for channel_id, channel in sorted(self.channels.items(), key=channel_sort_key):
                channel_info.append({
                    'Canal ID': channel.channel_id,
                    'Unidade': channel.unit,
                    'Amostras': len(channel.timestamps)
                })
            
            if channel_info:
                channel_df = pd.DataFrame(channel_info)
                channel_df.to_excel(writer, index=False, sheet_name='Informações dos Canais')
        
        print(f"Arquivo Excel gerado com sucesso: {output_filepath}")

    def export_to_json(self, output_filepath: str) -> None:
        """
        Exporta os dados processados para um arquivo JSON.
        
        Args:
            output_filepath: Caminho para o arquivo JSON de saída
        """
        # Se não tiver extensão .json, adiciona
        if not output_filepath.lower().endswith('.json'):
            output_filepath += '.json'
        
        # Cria um dicionário com metadados e canais
        data_to_export = {
            "metadata": self.metadata,
            "channels": {}
        }
        
        # Adiciona cada canal ao dicionário
        for channel_id, channel in self.channels.items():
            # Converte o canal para dicionário JSON usando o método to_json
            data_to_export["channels"][str(channel_id)] = channel.to_json()
        
        # Salva o dicionário como JSON
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(data_to_export, f, indent=4)
        
        print(f"Arquivo JSON gerado com sucesso: {output_filepath}")
    
    @staticmethod
    def import_from_json(json_filepath: str) -> 'GTDProcessor':
        """
        Cria um novo processador GTD a partir de um arquivo JSON exportado anteriormente.
        
        Args:
            json_filepath: Caminho para o arquivo JSON
            
        Returns:
            Um novo objeto GTDProcessor com os dados carregados
        """
        # Cria um novo processador
        processor = GTDProcessor()
        
        # Carrega o arquivo JSON
        with open(json_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Carrega os metadados
        processor.metadata = data.get("metadata", {})
        
        # Carrega os canais
        channels_data = data.get("channels", {})
        for channel_id, channel_data in channels_data.items():
            # Converte os dados JSON em um objeto Channel
            processor.channels[channel_id] = Channel.from_json(channel_data)
        
        return processor

def process_gtd_directory(directory: str, output_filepath: str) -> None:
    """
    Processa todos os arquivos GTD em um diretório.
    
    Args:
        directory: Caminho para o diretório contendo arquivos GTD
        output_filepath: Caminho para o arquivo de saída (base para Excel e JSON)
    """
    processor = GTDProcessor()
    
    # Encontra todos os arquivos .GTD no diretório
    gtd_files = []
    for file in os.listdir(directory):
        if file.lower().endswith('.gtd'):
            gtd_files.append(os.path.join(directory, file))
    
    # Ordena os arquivos pelo nome para processá-los em ordem
    gtd_files.sort()
    
    # Processa os arquivos
    if gtd_files:
        processor.process_multiple_files(gtd_files)
        
        # Define caminhos para os arquivos de saída
        excel_filepath = output_filepath
        if not excel_filepath.lower().endswith('.xlsx'):
            excel_filepath += '.xlsx'
            
        json_filepath = os.path.splitext(output_filepath)[0] + '.json'
        
        # Exporta para Excel e JSON
        processor.export_to_excel(excel_filepath)
        processor.export_to_json(json_filepath)
        
        print(f"Processados {len(gtd_files)} arquivos GTD.")
    else:
        print(f"Nenhum arquivo GTD encontrado no diretório: {directory}")


if __name__ == "__main__":
    # Exemplo de uso para processar um único arquivo
    # processor = GTDProcessor()
    # processor.process_file("caminho/para/arquivo.GTD")
    # processor.export_to_excel("saida.xlsx")
    
    # Diretório base do projeto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Diretório de entrada com os arquivos GTD
    input_dir = os.path.join(base_dir, "Info_the_project_GHFM", "Ensaios", "GHFM_250206_070758")
    
    # Diretório para salvar os arquivos processados
    output_dir = os.path.join(base_dir, "temp_data")
    
    # Cria o diretório de saída se não existir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Define o caminho completo para o arquivo Excel de saída
    output_file = os.path.join(output_dir, "GTD_Processed_Data.xlsx")
    
    # Processa os arquivos GTD do diretório de entrada
    process_gtd_directory(input_dir, output_file)