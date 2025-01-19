from datetime import datetime
from enum import Enum
import pandas as pd

from googleapiclient.errors import HttpError


from auth import authenticate_google_sheets


SAMPLE_SPREADSHEET_ID = "18jFotI0lwie-8p-eU9rjtcVrtsO5GldMbVoyo-Y5EYY"


def _fetch_data_from_sheets(service_sheets, sheet_id, range_name):
    try:
        sheet = service_sheets.spreadsheets()
        result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()

        values = result.get("values", [])

        if not values:
            print("No data found.")
            return pd.DataFrame()

        headers = values[0]

        headers = [header.split("\n")[0] for header in headers]

        data = values[1:]
        return pd.DataFrame(data, columns=headers)

    except HttpError as err:
        print(f"An error occurred: {err}")
        return pd.DataFrame()


class TimePeriod(Enum):
    WEEK = "week"
    MONTH = "month"
    THREE_MONTH = "3Month"
    SIX_MONTH = "6Month"


def _filter_data(df, time_period, only_first_visa=True, only_touristic_visa=True):
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    end_date = datetime.now()

    # Time period filtering
    if time_period == TimePeriod.WEEK.value:
        start_date = end_date - pd.DateOffset(weeks=1)
    elif time_period == TimePeriod.MONTH.value:
        start_date = end_date - pd.DateOffset(months=1)
    elif time_period == TimePeriod.THREE_MONTH.value:
        start_date = end_date - pd.DateOffset(months=3)
    elif time_period == TimePeriod.SIX_MONTH.value:
        start_date = end_date - pd.DateOffset(months=6)
    else:
        raise ValueError("Invalid time period. Choose from: week, month, 3Month, 6Month.")

    df_filtered = df[(df['Timestamp'] >= start_date) & (df['Timestamp'] <= end_date)]

    if only_first_visa:
        df_filtered = df_filtered[df_filtered['Предыдущая визовая история.'].str.contains("первая", na=False)]

    if only_touristic_visa:
        df_filtered = df_filtered[df_filtered['Тип визы.'] == 'Туристическая']

    df_filtered = df_filtered[df_filtered['Ваш паспорт.'] == 'РФ']

    return df_filtered


def _calculate_top_countries(df):
    df['Multi_visa'] = df['Какое было решение по визе?'].apply(lambda x: 1 if 'Мульти' in x else 0)
    df['One_entry_visa'] = df['Какое было решение по визе?'].apply(lambda x: 1 if 'Один въезд' in x else 0)

    country_visa_counts = df.groupby('В какую страну вы подавались на шенген?').agg(
        Multi_visa_decisions=('Multi_visa', 'sum'),
        One_entry_visa_decisions=('One_entry_visa', 'sum')
    )

    country_visa_counts['rate'] = country_visa_counts['Multi_visa_decisions'] / country_visa_counts['One_entry_visa_decisions']

    # Sort by the rate in descending order and return the top 5 countries
    top_countries = country_visa_counts.sort_values('rate', ascending=False).head(5)

    return top_countries


def get_top_visa_countries(
        service_sheets,
        spreadsheet_id,
        time_period,
        only_first_visa=True,
        only_touristic_visa=True):
    SAMPLE_RANGE_NAME = "Form Responses 1!A2:K"

    df = _fetch_data_from_sheets(service_sheets, spreadsheet_id, SAMPLE_RANGE_NAME)

    filtered_df = _filter_data(df, time_period, only_first_visa, only_touristic_visa)
    top_countries = _calculate_top_countries(filtered_df)

    return top_countries


def main():
    service_sheets = authenticate_google_sheets()
    top_countries = get_top_visa_countries(
        service_sheets,
        SAMPLE_SPREADSHEET_ID,
        TimePeriod.SIX_MONTH.value, only_first_visa=True, only_touristic_visa=True)

    print(len(top_countries))
    print("Data fetched from Google Sheets:")
    print(top_countries)


if __name__ == "__main__":
    main()
