from datetime import datetime
import pandas as pd

from googleapiclient.errors import HttpError

from auth import SAMPLE_SPREADSHEET_ID, authenticate_google_sheets


def fetch_data_from_sheets(sheet_id, range_name):
    try:
        service = authenticate_google_sheets()
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
        values = result.get("values", [])
        
        if not values:
            print("No data found.")
            return pd.DataFrame()
        
        headers = values[0]
        data = values[1:]
        return pd.DataFrame(data, columns=headers)
    
    except HttpError as err:
        print(f"An error occurred: {err}")
        return pd.DataFrame()


def filter_data(df, time_period, only_first_visa=True, only_touristic_visa=True):
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    # Time period filtering
    if time_period == "week":
        end_date = datetime.now()
        start_date = end_date - pd.DateOffset(weeks=1)
    elif time_period == "month":
        end_date = datetime.now()
        start_date = end_date - pd.DateOffset(months=1)
    elif time_period == "3Month":
        end_date = datetime.now()
        start_date = end_date - pd.DateOffset(months=3)
    elif time_period == "6Month":
        end_date = datetime.now()
        start_date = end_date - pd.DateOffset(months=6)
    else:
        raise ValueError("Invalid time period. Choose from: week, month, 3Month, 6Month.")
    
    df_filtered = df[(df['Timestamp'] >= start_date) & (df['Timestamp'] <= end_date)]

    if only_first_visa:
        df_filtered = df_filtered[df_filtered['Предыдущая визовая история'].str.contains("первая", na=False)]

    if only_touristic_visa:
        df_filtered = df_filtered[df_filtered['Тип визы'] == 'Туристическая']
    
    return df_filtered


def calculate_top_countries(df):
    df['Multi_visa'] = df['Какое было решение по визе?'].apply(lambda x: 1 if 'Мульти' in x else 0)
    df['One_entry_visa'] = df['Какое было решение по визе?'].apply(lambda x: 1 if 'Один въезд' in x else 0)

    country_visa_counts = df.groupby('В какую страну вы подавались на шенген?').agg(
        Multi_visa_decisions=('Multi_visa', 'sum'),
        One_entry_visa_decisions=('One_entry_visa', 'sum')
    )

    country_visa_counts['rate'] = country_visa_counts['Multi_visa_decisions'] / country_visa_counts['One_entry_visa_decisions']
    
    # Sort by the rate in descending order and return the top 3 countries
    top_countries = country_visa_counts.sort_values('rate', ascending=False).head(3)
    
    return top_countries


def get_top_visa_countries(time_period, only_first_visa=True, only_touristic_visa=True):
    SAMPLE_RANGE_NAME = "Form Responses 1!A2:K"
    
    df = fetch_data_from_sheets(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME)

    filtered_df = filter_data(df, time_period, only_first_visa, only_touristic_visa)
    top_countries = calculate_top_countries(filtered_df)
    
    return top_countries


def main():
    top_countries = get_top_visa_countries("week", only_first_visa=True, only_touristic_visa=True)
    
    print("Data fetched from Google Sheets:")
    print(top_countries)

if __name__ == "__main__":
    main()
