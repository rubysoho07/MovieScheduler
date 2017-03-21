#-*- coding: utf-8 -*-
"""
    Movie Schedule Parser.
    2017.02.21 Yungon Park
"""
from django.utils import timezone, dateparse
import requests
from bs4 import BeautifulSoup
from scheduler_core.models import MovieSchedule


class MovieScheduleParser(object):

    # __init__ method
    def __init__(self):
        pass

    # Get rating for CJ E&M channels.
    @staticmethod
    def get_cj_channel_ratings(rating):
        if rating == "age19":
            return 19
        elif rating == "age15":
            return 15
        elif rating == "age12":
            return 12
        elif rating == "age7":
            return 7
        else:
            return 0

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

        # If date is different from the day of argument, return None.
        date_split = date_text.split(".")
        if "".join(date_split) != url[-8:]:
            return None

        # Convert to timezone.datetime type.
        schedule_date = timezone.datetime(int(date_split[0]), int(date_split[1]), int(date_split[2]))

        # Get table.
        schedule_table = schedule.find('tbody').find_all('tr')

        # Make schedule list.
        schedule_list = []

        last_hour = 0
        for item in schedule_table:
            # Get title
            try:
                title = item.find('div', class_='program')['title']
            except KeyError:
                # Remove span tag
                title = item.find('div', class_='program').text

            title = title.strip()

            # Get start time and end time.
            start_time_text = item.find('em').text.strip()
            duration = item.find('td', class_='runningTime').text

            start_time_split = start_time_text.split(':')
            start_time = schedule_date + timezone.timedelta(hours=int(start_time_split[0]),
                                                            minutes=int(start_time_split[1]))
            # Convert naive time to timezone aware.
            start_time = timezone.make_aware(start_time, timezone.get_current_timezone())
            end_time = start_time + timezone.timedelta(minutes=int(duration))

            if start_time.hour < last_hour:
                # Check start_time to add next day's schedule.
                start_time = start_time + timezone.timedelta(days=1)
                end_time = end_time + timezone.timedelta(days=1)
                schedule_date = schedule_date + timezone.timedelta(days=1)
            elif end_time.day != schedule_date.day:
                # if end time is after the midnight, plus 1 day to schedule_date.
                schedule_date = schedule_date + timezone.timedelta(days=1)

            # Save hour field of last schedule.
            last_hour = end_time.hour

            # Get ratings.
            rating = item.find('td', class_='rating').find('span')['class']
            schedule_list.append({"title": title,
                                  "start_time": start_time,
                                  "end_time": end_time,
                                  "rating": rating[0]})

        # Return it.
        return schedule_list

    # Get Kakao TV Movie/Animation Schedule.
    @staticmethod
    def get_kakao_tv_schedule():

        # Get original data
        original_page = MovieScheduleParser.get_original_data(
            "http://kakao-tv.tistory.com/category/PLAYY%20%ED%8E%B8%EC%84%B1%ED%91%9C"
        )

        # Get two schedule tables.
        first_article = original_page.find('div', class_='article')
        schedules_table = first_article.find_all('table')

        movie_schedule = MovieScheduleParser.parse_kakao_tv_schedule(schedules_table[0])
        animation_schedule = MovieScheduleParser.parse_kakao_tv_schedule(schedules_table[1])

        return movie_schedule, animation_schedule

    # Parse Kakao TV Schedule.
    @staticmethod
    def parse_kakao_tv_schedule(table):
        # blank schedule.
        schedule_list = []

        # Ignore first row.
        first_row = table.find('tr')
        all_schedules = first_row.find_next_siblings('tr')

        for schedule in all_schedules:
            schedule_dict = dict()

            schedule_column = schedule.find_all('td')

            start_datetime = MovieScheduleParser.make_kakao_schedule_time(
                schedule_column[0].text, schedule_column[1].text)
            end_datetime = MovieScheduleParser.make_kakao_schedule_time(
                schedule_column[0].text, schedule_column[2].text)

            if start_datetime > end_datetime:
                end_datetime = end_datetime + timezone.timedelta(days=1)

            schedule_dict['start_time'] = timezone.make_aware(start_datetime, timezone.get_current_timezone())
            schedule_dict['end_time'] = timezone.make_aware(end_datetime, timezone.get_current_timezone())

            schedule_dict['title'] = schedule_column[3].text
            schedule_dict['rating'] = None

            schedule_list.append(schedule_dict)

        return schedule_list

    @staticmethod
    def make_kakao_schedule_time(date, time):
        return dateparse.parse_datetime(date + " " + time)

    @staticmethod
    def make_kakao_schedule_object(broadcast_company, schedule):
        schedule_object = MovieSchedule(broadcast_company=broadcast_company,
                                        title=schedule['title'],
                                        start_time=schedule['start_time'],
                                        end_time=schedule['end_time'],
                                        ratings=schedule['rating'])
        return schedule_object

    @staticmethod
    def save_kakao_schedule(broadcast_company, schedules):
        for schedule in schedules:
            schedule_object = MovieScheduleParser.make_kakao_schedule_object(broadcast_company, schedule)
            schedule_object.save()

if __name__ == "__main__":
    # CJ E&M Channel Test.
    print (MovieScheduleParser.get_cj_channels("http://catchon.tving.com/catchon/schedule2?startDate=20170228"))
