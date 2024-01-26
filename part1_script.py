import wbgapi as wb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def create_chart(filter_options, df):
    '''
    Creates a plotly visualization (with a drop down to filter displayed data) and saves it as html.
 
    Args:
        filter_options: A Dictionary of values for the drop down menu.
        df: Pandas DataFrame.
 
    Returns:
        None
    '''
    # Create plotly figure using data and labels
    fig = px.line(df, x=df.index, y=df.columns, 
                  labels={
                     "value": "Percentage (%) of Population",
                     "variable": "Filter By:",
                 },
                  title='Percentage (%) of Population Using At Least Basic Sanitation Services'
        ).update_traces(visible="legendonly")

    # Set visibility of each category
    category_list = []
    category_visibility_list = []
    for category_name in filter_options.keys():
        visibility_list = []
        for col in df.columns:
            if col in filter_options[category_name]:
                if (col == "Country_Avg_line"):
                    visibility_list.append(True)
                elif category_name == "Countries":
                    visibility_list.append('legendonly')
                else:
                    visibility_list.append(True)
            else:
                visibility_list.append(False)

        category_list.append(category_name)
        category_visibility_list.append(visibility_list)

    # Create buttons for each category
    buttons = []
    for i, g in enumerate(category_list):
        button =  dict(label=g, method='restyle', args=['visible',category_visibility_list[i]])
        buttons.append(button)

    # Create button for union of all categories
    buttons = [{'label': 'All', 
                'method': 'restyle', 
                'args': ['visible', ['legendonly' for i in range(len(df.columns))]]}] + buttons

    # Update layout with buttons                       
    fig.update_layout(
        updatemenus=[
            dict(
            type="dropdown",
            direction="down",
            buttons = buttons)
        ],
        title_x=0.5
    )
   
    fig.show()
    fig.write_html('visual.html')


def inspect_dataframe(df):
    '''
    Get a high level overview of a given DataFrame.
 
    Args:
        df: Pandas DataFrame.
 
    Returns:
        None
    '''
    print("Top 5 rows:\n")
    print(df.head())
    print('\n********************\n')

    print("Column data-type and non-null count:\n")
    print(df.info())
    print('\n********************\n')

    print("Basic summary statistics for numerical column:\n")
    print(df.describe())
    print('\n********************\n')


def preprocess_df(df):
    '''
    Format the raw data, for example, removing NaNs, taking transpose etc.
 
    Args:
        df: Pandas DataFrame.
 
    Returns:
        df: Preprocessed df.
    '''
    before_prep_shape = df.shape

    print("\nDrop columns with all nulls.")
    df.dropna(axis=1, how='all', inplace=True)

    print("Drop rows with all nulls in year columns.")
    cols_to_check = list(df.columns)
    df.dropna(subset=cols_to_check, how='all', inplace=True)

    print("Remove 'YR' from column names.")
    df.columns = df.columns.str.replace("YR", "", regex=True)

    print("Round percentage values to 1 decimal place in year columns.")
    df = df.round(1)

    print("Take transpose of the dataframe.")
    df = df.T
    df.index.names = ['Year']
    df = df.rename_axis(columns=None)
    print('\n********************\n')

    print('Shape of dataframe before applying preprocessing:', before_prep_shape)
    print('Shape of dataframe after applying preprocessing:', df.shape)
    print("Top 5 rows now:\n")
    print(df.head())
    print('\n********************\n')

    return df


def main():
    # # get indicators with the word sanitation
    # print(wb.series.info(q='sanitation'))

    # access metadata for the sanitation indicator
    print("Metadata about the Indicator: People using at least basic sanitation services (Percentage of population)")
    print(wb.series.metadata.get('SH.STA.BASS.ZS'))

    # retreive sanitation data
    sanit_df = wb.data.DataFrame('SH.STA.BASS.ZS', labels=True)
    sanit_df.set_index("Country", inplace=True)

    inspect_dataframe(sanit_df)
    sanit_df = preprocess_df(sanit_df)

    # Extract country names from dataframe columns
    world_index = list(sanit_df.columns).index('World')
    countries = sorted(sanit_df.columns[0:world_index].tolist())
    sanit_df['Country_Avg_line'] = sanit_df[countries].mean(axis=1)
    countries = ['Country_Avg_line'] + countries

    # Income and Region categories taken from https://datahelpdesk.worldbank.org/knowledgebase/articles/906519-world-bank-country-and-lending-groups
    income_grps = ['Low income', 'Lower middle income', 'Upper middle income', 'High income']
    region_grps = ['East Asia & Pacific', 'Europe & Central Asia', 'Latin America & Caribbean', 'Middle East & North Africa', 'North America', 'South Asia', 'Sub-Saharan Africa']

    # Divide column names into categories and sort alphabetically
    sanit_df = sanit_df[countries + region_grps + income_grps]

    # Create dictionary of filter options
    filter_options = {'Countries':countries,'Income Groups':income_grps, 'Regions':region_grps}

    create_chart(filter_options, sanit_df)

main()



