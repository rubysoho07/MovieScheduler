"""
    Movie Schedule Parser.
    2017.02.21 Yungon Park
"""
import datetime
import requests
from bs4 import BeautifulSoup


class MovieScheduleParser(object):

    # __init__ method
    def __init__(self):
        pass

    # Get original data from web.
    @staticmethod
    def get_original_data(url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'
        }
        data = requests.get(url, headers=headers)

        # Need to encoding UTF-8. (For unicode text)
        return BeautifulSoup(data.text, "html.parser")

    # Get movie schedule from CJ E&M channels.
    @staticmethod
    def get_cj_channels(url):
        # Get original data
        schedule = MovieScheduleParser.get_original_data(url).find('div', class_='scheduler')

        # Get date.
        date_text = schedule.find('em').text[:-4].strip()

        # If date is different from argument day, return None.
        date_split = date_text.split(".")
        if "".join(date_split) != url[-8:]:
            return None

        # Convert to datetime.datetime type.
        schedule_date = datetime.datetime(int(date_split[0]), int(date_split[1]), int(date_split[2]))

        # Get table.
        schedule_table = schedule.find('tbody').find_all('tr')

        # Make schedule list.
        schedule_list = []

        for item in schedule_table:
            # Get title
            title = item.find('div', class_='program')['title']

            # Get start time and end time.
            start_time_text = item.find('em').text.strip()
            duration = item.find('td', class_='runningTime').text

            start_time_split = start_time_text.split(':')
            start_time = schedule_date + datetime.timedelta(hours=int(start_time_split[0]),
                                                            minutes=int(start_time_split[1]))
            end_time = start_time + datetime.timedelta(minutes=int(duration))

            # if end time is after the midnight, plus 1 day to schedule_date.
            if end_time.day != schedule_date.day:
                schedule_date = schedule_date + datetime.timedelta(days=1)

            # Get ratings.
            rating = item.find('td', class_='rating').find('span')['class']
            schedule_list.append({"title": title, "start_time": start_time, "end_time": end_time, "rating": rating[0]})

        # Return it.
        return schedule_list

if __name__ == "__main__":
    # CJ E&M Channel Test.
    print (MovieScheduleParser.get_cj_channels("http://ocn.tving.com/ocn/schedule?startDate=20170224"))
