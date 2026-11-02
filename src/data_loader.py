from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "VeiculosSubtraidos_2024.xlsx"


def load_and_validate_data(
    excel_path: str | Path = DEFAULT_DATA_PATH,
    sheet_name: str = "AMOSTRAGEM",
) -> pd.DataFrame:
    """Load the vehicle-theft sample and check the columns used by the pipeline."""
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    required_columns = [
        "BAIRRO",
        "DATA_OCORRENCIA_BO",
        "HORA_OCORRENCIA",
        "DESCR_TIPO_VEICULO",
        "LATITUDE",
        "LONGITUDE",
    ]

    for column in required_columns:
        if column not in df.columns:
            raise KeyError(f"Required spreadsheet column '{column}' was not found.")

    return df
