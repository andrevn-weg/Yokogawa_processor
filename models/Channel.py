from datetime import datetime
from typing import List, Dict, Tuple, Optional, Union
import json

class Channel:
    """
    Classe para armazenar os dados de um canal específico do arquivo GTD.
    Cada canal contém registros de timestamp, valores mínimos e máximos.
    """
    def __init__(self, channel_id: Union[int, str], unit: str):
        """
        Inicializa um objeto Channel com ID e unidade.
        
        Args:
            channel_id: O ID do canal (número inteiro ou string)
            unit: A unidade de medida do canal (ex: °C)
        """
        self.channel_id = channel_id
        self.unit = unit
        self.timestamps = []  # Lista para armazenar os timestamps
        self.samples_min = []  # Lista para armazenar os valores mínimos
        self.samples_max = []  # Lista para armazenar os valores máximos
    
    def add_sample(self, timestamp: datetime, min_value: float, max_value: float):
        """
        Adiciona uma amostra ao canal com timestamp, valor mínimo e máximo.
        
        Args:
            timestamp: Data e hora da amostra
            min_value: Valor mínimo no intervalo
            max_value: Valor máximo no intervalo
        """
        self.timestamps.append(timestamp)
        self.samples_min.append(min_value)
        self.samples_max.append(max_value)
    
    def get_data_as_dict(self) -> Dict:
        """
        Retorna os dados do canal como um dicionário para facilitar a exportação.
        
        Returns:
            Um dicionário com timestamps, min e max values
        """
        return {
            f"Timestamp": self.timestamps,
            f"Ch{self.channel_id}_Min_{self.unit}": self.samples_min,
            f"Ch{self.channel_id}_Max_{self.unit}": self.samples_max
        }
    
    def __str__(self) -> str:
        """Representação em string do objeto Channel"""
        return (f"Channel {self.channel_id} ({self.unit}): "
                f"{len(self.timestamps)} amostras")
    
    def to_json(self) -> Dict:
        """
        Converte o objeto Channel em um dicionário para serialização JSON.
        
        Returns:
            Um dicionário com os dados do canal em formato serializable
        """
        # Converte objetos datetime para strings ISO
        iso_timestamps = [ts.isoformat() for ts in self.timestamps]
        
        return {
            "channel_id": self.channel_id,
            "unit": self.unit,
            "timestamps": iso_timestamps,
            "samples_min": self.samples_min,
            "samples_max": self.samples_max
        }
    
    @staticmethod
    def from_json(json_data: Dict) -> 'Channel':
        """
        Cria um objeto Channel a partir de dados JSON.
        
        Args:
            json_data: Dicionário com dados do canal
            
        Returns:
            Uma nova instância de Channel
        """
        channel = Channel(json_data["channel_id"], json_data["unit"])
        
        # Converte strings ISO para objetos datetime
        channel.timestamps = [datetime.fromisoformat(ts) for ts in json_data["timestamps"]]
        channel.samples_min = json_data["samples_min"]
        channel.samples_max = json_data["samples_max"]
        
        return channel
    
    def save_to_json_file(self, filepath: str) -> None:
        """
        Salva os dados do canal em um arquivo JSON.
        
        Args:
            filepath: Caminho para o arquivo JSON
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_json(), f, indent=4) # Usa indentação para melhor legibilidade
            
    @staticmethod
    def load_from_json_file(filepath: str) -> 'Channel':
        """
        Carrega um canal a partir de um arquivo JSON.
        
        Args:
            filepath: Caminho para o arquivo JSON
            
        Returns:
            Uma instância de Channel
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        return Channel.from_json(json_data)
