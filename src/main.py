#!/.venv/bin/python.exe

import requests
import json
import datetime
from rich.console import Console
from rich.text import Text
from rich.spinner import Spinner

VERSION = "v1.0"
CONFIG_FILE = "config.json"
API_KEY_FILE = "api_key.txt"
ZIPS = ['32712', '90210']


def main() -> None:
    try:
        console = Console()
        alarms = load_config(CONFIG_FILE).get('alarms')
        api_key = load_api_key(API_KEY_FILE)
        console.print('Shipping Weather', style="bold yellow", end=' - ')
        console.print(VERSION, style='dim')
        display_prompt(alarms, console)

        while True:
            input_str = input('> ')
            if input_str == 'q':
                break
            elif input_str =='c':
                alarms = get_alarm_temp_input()
                new_alarm_dict = {'alarms': alarms}
                update_config(new_alarm_dict, CONFIG_FILE)
                display_prompt(alarms, console)
                continue
            elif input_str == '':
                zipcodes = ZIPS
            elif ',' in input_str:
                zipcodes = [zipcode.strip() for zipcode in input_str.split(',')]
            elif ' ' in input_str:
                zipcodes = input_str.split(' ')
            else:
                zipcodes = [input_str]

            print_data(api_key, zipcodes, alarms, console)
    except Exception as e:
        console.print(f'An error occurred: {e}', style='bold red')
def display_prompt(alarms, console) -> None:
    low = alarms['low']
    high = alarms['high']
    console.print(f'Alarm Temps: [blue]{low}[/blue] and [red]{high}[/red]')
    console.print('\nEnter one or more Zip Codes\n\nOR\n\n[green]C[/green]  to [underline]C[/underline]hange alarm temps\n[green]Q[/green]  to [underline]Q[/underline]uit\n')

def load_api_key(key_file) -> str:
    try:
        with open(key_file, "r") as file:
            api_key = file.read().strip()
            return api_key
    except FileNotFoundError:
        raise ValueError("API key file not found")
    
def load_config(config_file) -> dict:
    try:
        with open(config_file, "r") as file:
            config_data = json.load(file)
            return config_data
    except FileNotFoundError:
        print(f"The file {file} does not exist.")
        return {}

def update_config(updates, config_file) -> None:

    try:
        config = load_config(config_file)
        config.update(updates)

        with open(config_file, "w") as file:
            json.dump(config, file, indent=4)

    except FileNotFoundError:
        print(f"The file {file} does not exist.")
    except json.JSONDecodeError:
        print(f'Error loading {file}.')
    except IOError:
        print(f"Failed to write to file {file}: {e}")

def get_alarm_temp_input() -> str:
    new_alarm_temps = {}
    try:
        new_alarm_temps['low'] = int(input('\nLow temp alarm: '))
        new_alarm_temps['high'] = int(input('High temp alarm: '))
    except ValueError:
        print('Invalid input. Please enter an integer.')

    return new_alarm_temps

def fetch_forecast(api_key, zipcodes) -> list:
    base_url = "https://api.openweathermap.org/data/2.5/forecast"

    results = []

    for zipcode in zipcodes:
        parameters = {'zip': f'{zipcode},us', 'appid': api_key, 'units': 'imperial'}

        with Console().status('[bold green]Fetching weather data...', spinner='dots'):
            response = requests.get(base_url, params=parameters)

        if response.status_code == 200:
            city = response.json()['city']['name']
            forecasts = response.json()['list']  # Corrected: Get 'list' from the API response
            result_city_entry = {
                'Zip Code': zipcode,
                'City': city,
                'High': '',
                'Low': '',
                'Forecast': []
                }

            summarize_city_forecasts(forecasts, result_city_entry)
             
            results.append(result_city_entry)
        else: 
            # results.append(None)
            Console().print(f'\n[red]> [/red]{zipcode} is not a valid Zip Code.')

    return results

def summarize_city_forecasts(forecasts, result_city_entry):
    city_temps = {}  # overall min and max for a city
    daily_temps = {}  # daily minimum and maximum temperatures

    for three_hour_segment in forecasts:
        date = three_hour_segment['dt_txt'].split()[0]  # Extract only the date part
        temp = three_hour_segment['main']['temp']

        # Update daily temperatures
        if date not in daily_temps:
            daily_temps[date] = {'High': temp, 'Low': temp}
        else:
            daily_temps[date]['High'] = max(daily_temps[date]['High'], temp)
            daily_temps[date]['Low'] = min(daily_temps[date]['Low'], temp)
        
        if len(city_temps) == 0: # Establish the first min/max entries
            city_temps['High'] = temp
            city_temps['Low'] = temp
        else: # Compare and update Min and Max
            city_temps['High'] = max(city_temps['High'], temp) 
            city_temps['Low'] = min(city_temps['Low'], temp)
    
    # Append aggregated daily temperatures to result_city_entry
    for date, temps in daily_temps.items():
        result_city_entry['Forecast'].append({'Date': date, 'High': temps['High'], 'Low': temps['Low']})
    
    result_city_entry['High'], result_city_entry['Low'] = city_temps['High'], city_temps['Low']

def print_data(api_key, zipcodes, alarms, console) -> None:

    def format_temp(temp) -> Text:
        temp = round(temp)
        t = temp
        temp = f'{temp}°'

        if t >= alarms['high']:
            temp = Text(temp, style="red")
        elif t <= alarms['low']:
            temp = Text(temp, style="blue")
        return temp

    def print_header_line(header) -> None:
        
        print(' ' * first_column_indent, end='')
        for item in header:
            header_item_spacing = ' ' * (column_spacing + (9-len(item))) 
            print(item, end=header_item_spacing)
        print()

    column_spacing = 7
    first_column_indent = 20
    days_of_week = []
    formatted_dates = []

    results = fetch_forecast(api_key, zipcodes)

    for date in results[0]['Forecast']:
        day_of_week, formatted_date = format_dt(date['Date'])
        days_of_week.append(day_of_week)
        formatted_dates.append(formatted_date)

    # Print Headers
    print()
    for header in [days_of_week, formatted_dates]:
        print_header_line(header)
    print()

    # Print City Entries   
    for city in results:
        print(city['City'])
        console.print(city['Zip Code'], end='') 
        print(' '*15, end='')

        for day in city['Forecast']:
            low = format_temp(day['Low'])
            high = format_temp(day['High'])
            
            temp_range = Text()
            temp_range.append(low)
            temp_range.append(' - ')
            temp_range.append(high)

            temp_string_spacing = ' ' * (column_spacing + (9-len(temp_range.plain)))
            console.print(temp_range + temp_string_spacing, end='')
        print('\n')
    print()

def format_dt(date) -> list:
    dt = datetime.datetime.strptime(date, '%Y-%m-%d')
    day_of_week = dt.strftime("%A")
    day = dt.strftime("%d")
    month = dt.strftime("%B")
    formatted_date = f"{month} {add_ordinal_suffix(day)}"
    return day_of_week, formatted_date

def add_ordinal_suffix(day) -> str:
    day = int(day)
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = 'th'
    else:
        suffix = ['st', 'nd', 'rd'][day % 10 - 1]
    return str(day) + suffix

if __name__ == "__main__":
    main()