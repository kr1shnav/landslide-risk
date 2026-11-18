import pandas as pd
def accumulations(series: pd.Series) -> pd.DataFrame:
    return pd.DataFrame({'rainfall_1d':series.rolling(1).sum(),'rainfall_3d':series.rolling(3).sum(),'rainfall_7d':series.rolling(7).sum()})
