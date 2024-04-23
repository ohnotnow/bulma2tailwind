import requests
import os
import datetime
import random
from gepetto import metoffer, gpt

def get_relative_date(keyword):
    today = datetime.date.today()
    if "today" in keyword.lower():
        return [today]
    elif "tomorrow" in keyword.lower():
        return [today + datetime.timedelta(days=1)]
    elif "this week" in keyword.lower():
        return [today + datetime.timedelta(days=i) for i in range(7)]  # next 7 days
    else:
        return [today]  # default to today if unsure

def get_forecast_for_dates(forecast, target_dates):
    """
    Extracts forecast data for the specified dates from the API response.
    Returns a list of (date, period) tuples for all matching dates.
    """
    matched_periods = []
    for period in forecast['SiteRep']['DV']['Location']['Period']:
        period_date = datetime.datetime.strptime(period['value'], "%Y-%m-%dZ").date()
        if isinstance(target_dates, list):
            if period_date in target_dates:
                matched_periods.append((period_date, period))
        elif period_date == target_dates:
            matched_periods.append((period_date, period))
            break  # Break if only looking for one date and it's found
    return matched_periods

def get_forecast(location_name = None, dates = []):
    if not location_name:
        return "Wut?  I need a location name.  Asshat."
    if not dates:
        dates = [datetime.date.today()]
    API_KEY = os.getenv('MET_OFFICE_API_KEY')
    # 1. Download the Sitelist
    sitelist_url = f'http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/sitelist?key={API_KEY}'
    response = requests.get(sitelist_url)
    sitelist = response.json()

    # 2. Find the ID for the location
    location_id = None
    for location in sitelist['Locations']['Location']:
        if location['name'].lower() == location_name.lower():
            location_id = location['id']
            break

    if location_id is None:
        return f"Wut iz {location_name}? I dunno where that is.  Try again with a real place name, dummy."

    # 3. Request the forecast
    M = metoffer.MetOffer(API_KEY)
    forecast = M.loc_forecast(location_id, metoffer.DAILY)
    plain_forcasts = get_forecast_for_dates(forecast, dates)
    forecasts = []
    for date, period in plain_forcasts:
        details = period['Rep'][0]  # Assuming you want the first representation of the day
        weather_code = metoffer.WEATHER_CODES[int(details['W'])]
        human_readable_date = date.strftime("%A %d %B %Y")
        forecast_str = f"Forecast for {location_name.capitalize()} on {human_readable_date}: {metoffer.WEATHER_CODES[int(details['W'])]}, chance of rain {details['PPd']}%, temperature {details['Dm']}C (feels like {details['FDm']}C). Humidity {details['Hn']}%, wind {details['S']} knots - gusting upto {details['Gn']}.\n"
        forecasts.append(forecast_str)

    readable_forecast = "\n".join(forecasts)
    return readable_forecast

async def get_weather_location_from_prompt(prompt, chatbot):
    messages = [
        {"role": "system", "content": "You are a helpful assistant who is an expert at picking out UK town and city names from user prompts"},
        {"role": "user", "content": prompt}
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_location_for_forecast",
                "description": "figure out what town or city the user wants the weather for",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "A csv list of one or more UK city or town, eg London,Edinburgh,Manchester",
                        },
                    },
                    "required": ["location"],
                },
            }
        }
    ]
    # Note: we always use the openai model for this as it's the only one that always has function calling enabled
    chatbot = gpt.GPTModel()
    response = await chatbot.function_call(messages, tools)
    return response.parameters.get("location").split(","), response.tokens

async def get_friendly_forecast(question, chatbot):
    forecast = ""
    locations, total_tokens = await get_weather_location_from_prompt(question.strip(), chatbot)
    dates = get_relative_date(question)
    if locations is None:
        response = await chatbot.chat([{"role": "user", "content": question}])
        forecast = response.message
        total_tokens += response.tokens
    else:
        for location in locations:
            temp_forecast = get_forecast(location.strip(), dates)
            forecast += temp_forecast + "\n"
        date_and_time = datetime.datetime.now().strftime("%A %d %B %Y at %H:%M")
        default_system_prompt = f"You are a helpful assistant called '{chatbot.name}' who specialises in providing chatty and friendly weather forecasts for UK towns and cities.  ALWAYS use degrees Celcius and not Fahrenheit for temperatures. You MUST ONLY reply with the friendly forecast."
        personality = ""
        if random.random() < 0.1:
            personality = "A secret agent"
        elif random.random() < 0.1:
            personality = "A secret alcoholic"
        elif random.random() < 0.1:
            personality = "Only telling the forecast because the station has kidnapped your family"
        elif random.random() < 0.1:
            personality = "A man who loves the Cornish countryside and being with his love, Fanny"
        elif random.random() < 0.1:
            personality = "A an anxious depressive who is always on the edge of a breakdown"
        if personality:
            personality = f" You should take on subtle hints of this personality for writing your forecast *but don't be too obvious* : {personality}."
        question = f"It is currently {date_and_time}. The user asked me ''{question.strip()}''. I have the following plain weather forecasts for you based on their question.  Could you make the a bit more natural - like a weather presenter would give at the end of a drive-time news segment on the radio or TV?  ONLY reply with the rewritten forecast.  NEVER add any extra context - the user only wants to see the friendly, drive-time style forecast.  If the wind speed is given in knots, convert it to MPH. Feel free to use weather-specific emoji.  {personality}  FORECAST : ''{forecast}''"
        response  = await chatbot.chat([{"role": "user", "content": question}, {"role": "system", "content": f"You are a helpful assistant called '{chatbot.name}' who specialises in providing chatty and friendly weather forecasts for UK towns and cities.  ALWAYS use degrees Celcius and not Fahrenheit for temperatures. You MUST ONLY reply with the friendly forecast."}])
        forecast = response.message + "\n" + response.usage
    return forecast
