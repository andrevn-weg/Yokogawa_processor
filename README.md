# Yokogawa GTD File Processor

Sistema para processamento de arquivos GTD provenientes de equipamentos Yokogawa. Aplicação desenvolvida para facilitar a conversão e análise de dados de medição.

## 🚀 Acesso Rápido

- **Aplicação Web**: https://yokogawa-gtd.streamlit.app/
- **Repositório**: https://github.com/andrevn/Yokogawa_processor.git

## Funcionalidades

- **Processamento de arquivos GTD**: Leitura e parsing de arquivos GTD do Yokogawa
- **Conversão de dados**: Exportação para formatos Excel (.xlsx) e JSON
- **Interface web**: Interface Streamlit para upload e processamento de arquivos
- **Visualização de dados**: Gráficos interativos dos dados processados
- **Múltiplos arquivos**: Processamento simultâneo de vários arquivos GTD

## Estrutura do Projeto

```
Yokogawa_processor/
├── main.py                 # Ponto de entrada do Streamlit
├── requirements.txt        # Dependências do Python
├── models/
│   ├── gtd_processor.py   # Processador principal GTD
│   └── Channel.py         # Classe para canais de dados
├── pages/
│   └── Process_gtd_Files.py # Interface principal
├── utils/
│   ├── css_loader.py      # Carregamento de estilos
│   └── ...
└── temp_data/             # Diretório para arquivos processados
```

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/andrevn/Yokogawa_processor.git
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

1. Execute a aplicação Streamlit:
   ```bash
   streamlit run main.py
   ```

2. Acesse a interface web e faça upload dos arquivos GTD

3. Os arquivos processados serão salvos no diretório `temp_data/`

## Formatos de Saída

- **Excel**: Arquivo .xlsx com abas separadas para dados, metadados e informações dos canais
- **JSON**: Arquivo estruturado com todos os dados e metadados
