import pandas as pd


def create_aggregation_map(order_df: pd.DataFrame, column):
    """Given a dataframe and a specific column, this function finds unique values for this column.
    Consequently, this return a mapping from unique values to dataframes with jobs using this value.

    Args:
        order_df (pd.DataFrame): _description_
        column (_type_): _description_

    Returns:
        _type_: _description_
    """
    # create aggregation lists
    aggregation_map = {}
    unique_objects = order_df[column].unique()
    for object in unique_objects:
        aggregation_map[object] = []
        for _, job in order_df.iterrows():
            if job[column] == object:
                aggregation_map[object].append(job["job"])

    # create collection lists
    for key, value in aggregation_map.items():
        tool_df = order_df.loc[order_df["job"].isin(value)]
        aggregation_map[key] = tool_df

    return aggregation_map


def summarize_jobs(order_df: pd.DataFrame) -> pd.DataFrame:
    """For a faster schedule optimization, this functions summarizes several jobs to a single job
    with respect to different criteria.

    Args:
        order_df (pd.DataFrame): A dataframe containing the job database

    Returns:
        pd.DataFrame: A modified datafraem, which includes collective orders for boosted optimization.
    """
    # assuming all jobs in order_df are open (not finished, not in progress, not planned)
    tool_aggregation_map = create_aggregation_map(order_df, "tool")
    item_aggregation_map = create_aggregation_map(order_df, "item")

    # Printing all tools and items with the amount from the order_df to the console
    print("::Tools::")
    for tool in tool_aggregation_map.keys():
        if pd.isna(tool) or len(tool) == 0:
            print("A tool is missing in the database.")
        else:
            print(tool + ": " + str(len(tool_aggregation_map[tool].index)))
    print("\n::Items::")
    for item in item_aggregation_map.keys():
        print(item + ": " + str(len(item_aggregation_map[item].index)))

    # TODO implement summary function

    return order_df
