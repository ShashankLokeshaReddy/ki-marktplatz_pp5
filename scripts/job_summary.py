import pandas as pd


def summarize_jobs(order_df: pd.DataFrame) -> pd.DataFrame:
    # assuming all jobs in order_df are open (not finished, not in progress, not planned)
    
    # create aggregation lists
    aggregation_map = {}
    tools_in_use = order_df['tool'].unique()
    for tool in tools_in_use:
        aggregation_map[tool] = []
        for _, job in order_df.iterrows():
            if job['tool'] == tool:
                aggregation_map[tool].append(job['job'])
                
    # create collection lists
    for key, value in aggregation_map.items():
        tool_df = order_df.loc[order_df['job'].isin(value)]
        print(tool_df)
        aggregation_map[key] = tool_df
        
    return order_df