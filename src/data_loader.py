import pandas as pd

def load_and_validate_data(excel_path: str = "data/raw/VeiculosSubtraidos_2024.xlsx", sheet_name: str = "AMOSTRAGEM") -> pd.DataFrame:
    """Carrega e valida o conjunto de dados de amostragem de roubos de veículos."""
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    
    campos_essenciais = ['BAIRRO', 'DATA_OCORRENCIA_BO', 'HORA_OCORRENCIA', 
                         'DESCR_TIPO_VEICULO', 'LATITUDE', 'LONGITUDE']
    
    for campo in campos_essenciais:
        if campo not in df.columns:
            raise KeyError(f"A coluna essencial '{campo}' não foi encontrada na planilha.")
            
    return df
