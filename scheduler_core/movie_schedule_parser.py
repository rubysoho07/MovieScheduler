# -*- coding: utf-8 -*-
"""
    Movie Schedule Parser.
    2017.02.21 Yungon Park
"""
from django.utils import timezone, dateparse

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from scheduler_core.models import MovieSchedule


class MovieScheduleParser(object):
    """Parse movie schedule from schedule table of Korean movie channels."""

    @staticmethod
    def get_original_data(url):
        """Get source from web and returns BeautifulSoup object."""

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'
        }
        data = requests.get(url, headers=headers)

        return BeautifulSoup(data.text, "html.parser")

    @staticmethod
    def parse_string_to_int(duration, default):
        """Try to parse string to int, or return default value."""

        try:
            return int(duration)
        except ValueError:
            return default

    @staticmethod
    def make_schedule_object(broadcast_company, schedule):
        """Make MovieSchedule object with broadcast_company and dictionary for schedule."""

        schedule_object = MovieSchedule(broadcast_company=broadcast_company,
                                        title=schedule['title'],
                                        start_time=schedule['start_time'],
                                        end_time=schedule['end_time'],
                                        ratings=schedule['rating'])
        return schedule_object

    def save_schedule(self, broadcast_company, schedules):
        """Save schedule from schedule list to database."""

        for schedule in schedules:
            schedule_object = self.make_schedule_object(broadcast_company, schedule)
            schedule_object.save()

    def get_rating(self, rating):
        pass

    def parse_schedule_item(self, item, date):
        pass

    def parse_daily_schedule(self, table, date):
        pass

    def get_channel_schedule(self, url):
        pass


class CJScheduleParser(MovieScheduleParser):
    """Parser for movie schedule from CJ E&M channels."""

    def get_rating(self, rating):
        """Return rating information from string."""

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

    def parse_schedule_item(self, item, date):
        """Return CJ E&M channel schedule from table row."""

        schedule = dict()

        # Get title
        try:
            title = item.find('div', class_='program')['title']
        except KeyError:
            # Remove span tag
            title = item.find('div', class_='program').text

        schedule['title'] = title.strip()

        # Get ratings
        rating = item.find('td', class_='rating').find('span')['class'][0]
        schedule['rating'] = self.get_rating(rating)

        # Get start_time and end_time
        duration = item.find('td', class_='runningTime').text
        start_time = timezone.datetime.combine(date, dateparse.parse_time(item.find('em').text.strip()))
        schedule['start_time'] = timezone.make_aware(start_time, timezone.get_current_timezone())
        schedule['end_time'] = \
            start_time + timezone.timedelta(minutes=MovieScheduleParser.parse_string_to_int(duration, 0))

        return schedule

    def parse_daily_schedule(self, table, date):
        """Get daily schedule for CJ E&M channels."""

        schedule_list = []

        last_hour = 0  # Hour of last schedule
        for item in table:
            schedule = self.parse_schedule_item(item, date)

            if schedule['start_time'].hour < last_hour and last_hour >= 22:
                # Move to next day's schedule.
                schedule['start_time'] = schedule['start_time'] + timezone.timedelta(days=1)
                schedule['end_time'] = schedule['end_time'] + timezone.timedelta(days=1)

                # Move to next day.
                date = date + timezone.timedelta(days=1)
            elif schedule['end_time'].day != date.day:
                # Set next day because next schedule is for next day.
                date = date + timezone.timedelta(days=1)

            # Save hour field of last schedule.
            last_hour = schedule['end_time'].hour

            schedule_list.append(schedule)

        return schedule_list

    def get_channel_schedule(self, url):
        """Get movie schedule from CJ E&M channels."""

        schedule = self.get_original_data(url).find('div', class_='scheduler')

        date_text = schedule.find('em').text[:-4].strip()
        date_split = date_text.split(".")

        # If date is different from the day of argument, return None.
        if "".join(date_split) != url[-8:]:
            return None

        schedule_date = timezone.datetime(int(date_split[0]), int(date_split[1]), int(date_split[2]))
        schedule_table = schedule.find('tbody').find_all('tr')

        if len(schedule_table) == 0:
            # If no schedule exists
            return None

        return self.parse_daily_schedule(schedule_table, schedule_date)


class TCastScheduleParser(MovieScheduleParser):
    """Parser for movie schedule from t.cast channels."""

    def __init__(self, channel, start_date=None):
        """Constructor for the parser of t.cast channel. It needs channel, start_hour, start_date."""
        self.channel = channel
        self.start_hour = self.get_tcast_start_hour(channel)
        if start_date is None:
            self.start_date = timezone.datetime.today()
        else:
            self.start_date = start_date

    @staticmethod
    def get_tcast_start_hour(channel):
        """Get start hour of schedule table from t.cast channel."""

        if channel.bc_name == "Cinef":
            return 6
        else:
            return 5

    @staticmethod
    def check_tcast_date_range(date, date_range):
        """Extract date range from table and check if date is in that range."""

        found = False
        for i in date_range[1:]:
            if str(i.find_all(text=True)[-1]) == timezone.datetime.strftime(date, "%Y.%m.%d"):
                found = True
                break

        return found

    def get_tcast_next_week_page(self, start_date, date_range, wait, driver):
        """Get next week schedule page from t.cast channels."""

        while self.check_tcast_date_range(start_date, date_range) is not True:
            driver.find_element_by_xpath("//span[@class='next']/a").click()
            _ = wait.until(expected_conditions.element_to_be_clickable((By.XPATH, "//span[@class='next']/a")))
            date_range = BeautifulSoup(driver.page_source, 'html.parser').find_all('th')

        return driver

    def get_rating(self, rating):
        """Return rating information from file name of rating information."""

        rating_file_name = rating.split("/")[-1]

        if rating_file_name == "icon_7age.gif":
            return 7
        elif rating_file_name == "icon_12age.gif":
            return 12
        elif rating_file_name == "icon_15age.gif":
            return 15
        elif rating_file_name == "icon_19age.gif":
            return 19
        else:
            return 0

    def parse_schedule_item(self, item, date):
        """
        Make single schedule for t.cast channel. Return single schedule dictionary.

        :param item: <div class="con active">
        :param date: <strong>05:30</strong>
        :return schedule of movie
        """

        schedule = dict()

        start_time = dateparse.parse_time(item.find('strong').text.strip())
        start_datetime = date.replace(hour=start_time.hour, minute=start_time.minute)
        schedule['start_time'] = start_datetime
        schedule['end_time'] = None

        schedule['title'] = item.find('a').text.strip()

        rating = item.find('img')
        if rating is None:
            schedule['rating'] = 0
        else:
            schedule['rating'] = self.get_rating(rating['src'])

        return schedule

    def parse_daily_schedule(self, table, date):
        """Get daily schedule for t.cast channel."""

        date_format = timezone.datetime.strftime(date, "%Y%m%d")
        next_date = date + timezone.timedelta(days=1)
        daily_schedule = []

        # Get schedule
        for hour in range(24):
            date_hour_string = date_format + '{:02d}'.format(hour)
            cell = table.find('td', id=date_hour_string)

            if cell is None:
                return None

            schedules = cell.find_all('div', class_='con active')
            for schedule in schedules:
                if hour in range(self.start_hour):
                    # Next day's schedule.
                    daily_schedule.append(self.parse_schedule_item(schedule, next_date))
                else:
                    daily_schedule.append(self.parse_schedule_item(schedule, date))

        # Add to list
        return daily_schedule

    def get_channel_schedule(self, url):
        """Get t.cast channel schedule until no schedule exists. And return last update date. """

        driver = webdriver.PhantomJS()
        driver.get(url)

        # Get current week of start_date
        date_range = BeautifulSoup(driver.page_source, 'html.parser').find_all('th')
        wait = WebDriverWait(driver, 8)

        driver = self.get_tcast_next_week_page(self.start_date, date_range, wait, driver)

        # Get one day's schedule iteratively.
        end_date = self.start_date
        schedule_table = BeautifulSoup(driver.page_source, 'html.parser').find('tbody')
        schedules = self.parse_daily_schedule(schedule_table, self.start_date)
        while len(schedules) != 0:
            if schedules is not None:
                self.save_schedule(self.channel, schedules)

            end_date = end_date + timezone.timedelta(days=1)
            schedules = self.parse_daily_schedule(schedule_table, end_date)

            if schedules is None:
                driver = self.get_tcast_next_week_page(end_date, date_range, wait, driver)
                schedule_table = BeautifulSoup(driver.page_source, 'html.parser').find('tbody')
                schedules = self.parse_daily_schedule(schedule_table, end_date)

        driver.close()

        return end_date
