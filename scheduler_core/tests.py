# -*- coding: utf-8 -*-
from django.test import TestCase
from django.db.models import Q
from scheduler_core.models import BroadcastCompany, MovieSchedule
from scheduler_core.movie_schedule_parser import MovieScheduleParser, CJScheduleParser, TCastScheduleParser
from . import tasks
from django.utils import timezone
from bs4 import BeautifulSoup


# Create your tests here.
class MovieScheduleParserTestCase(TestCase):
    """Test base class for movie schedule parser."""

    def setUp(self):
        """Config environments before testing."""
        self.parser = MovieScheduleParser()
        self.channel, _ = BroadcastCompany.objects.get_or_create(bc_name="OCN")
        self.schedule_list = []

    def test_get_original_data(self):
        """Test to get BeautifulSoup object from schedule page."""
        data = self.parser.get_original_data("http://ocn.tving.com/ocn/schedule")

        self.assertNotEqual(data, None)

    def test_parse_string_to_int(self):
        """Test to parse string to integer."""
        value = self.parser.parse_string_to_int("10", 1)
        self.assertEqual(value, 10)

        value2 = self.parser.parse_string_to_int("100")
        self.assertEqual(value2, 100)

        value3 = self.parser.parse_string_to_int("ABC")
        self.assertEqual(value3, 0)

    def test_make_schedule_object(self):
        """Test to make MovieSchedule object with broadcast_company and dictionary for schedule."""
        now_time = timezone.now()

        schedule = {
            "title": "Test Title",
            "start_time": now_time,
            "end_time": None,
            "rating": 19
        }

        schedule_obj = self.parser.make_schedule_object(self.channel, schedule)

        self.assertEqual(schedule_obj.title, schedule['title'])
        self.assertEqual(schedule_obj.start_time, now_time)
        self.assertEqual(schedule_obj.end_time, None)
        self.assertEqual(schedule_obj.ratings, schedule['rating'])

    def test_save_schedules(self):
        """Test to save schedule from schedule list to database."""
        schedule = {
            "title": "Test Title",
            "start_time": timezone.now(),
            "end_time": None,
            "rating": 19
        }

        self.schedule_list.append(schedule)

        self.parser.save_schedule(self.channel, self.schedule_list)


class CJScheduleTestCase(TestCase):
    """Test to get schedules from CJ E&M channel."""

    def setUp(self):
        """Config environments before testing."""
        self.parser = CJScheduleParser()
        self.original_data = """
        <table>
            <tbody>
                <tr>
                    <td class="programInfo">
                        <div>
                            <em class="airTime">03:10</em>
                            <div class="program" title="Test Program 1">Test Program 1</div>
                        </div>
                    </td>
                    <td class="video"></td>
                    <td class="rating">
                        <span class="age19">Over 19</span>
                    </td>
                    <td class="runningTime">68</td> 
                </tr>
            </tbody>
        </table>
        """
        self.schedule_table = BeautifulSoup(self.original_data, 'html.parser').find_all('tr')
        self.schedule_date = timezone.now()

    def test_get_cj_channel_ratings(self):
        """Test to get rating from string properly."""

        result = self.parser.get_rating("age15")
        self.assertEqual(result, 15)

    def test_parse_cj_schedule_item(self):
        """Test to parse a program from table properly."""

        result = self.parser.parse_schedule_item(self.schedule_table[0], self.schedule_date)

        self.assertEqual(result['title'], "Test Program 1", "Check title")
        self.assertEqual(result['start_time'].hour, 3, "Check start time(hour)")
        self.assertEqual(result['start_time'].minute, 10, "Check start time(minute)")
        self.assertEqual(result['rating'], 19, "Check rating")

    def test_get_cj_daily_schedule(self):
        """Test to get daily schedule from web site properly."""

        result = self.parser.parse_daily_schedule(self.schedule_table, self.schedule_date)
        self.assertEqual(len(result), 1)

    def test_get_cj_channel_schedule(self):
        """Test to get CJ E&M channel schedule"""

        date_str = timezone.datetime.strftime(self.schedule_date, "%Y%m%d")
        result = self.parser.get_channel_schedule("http://ocn.tving.com/ocn/schedule?startDate=" + date_str)
        self.assertNotEqual(len(result), 0)

    def test_save_cj_channel_schedule(self):
        """Test to get and saving CJ E&M channel schedule"""
        tasks.save_cj_channel_schedule("OCN", "http://ocn.tving.com/ocn/schedule?startDate=")


class TCastScheduleTestCase(TestCase):
    """Test to get schedules from t.cast channels."""

    def setUp(self):
        """Configuration before testing"""
        self.channel, _ = BroadcastCompany.objects.get_or_create(bc_name="Screen")
        self.parser = TCastScheduleParser(self.channel)
        self.original_data = """
            <strong>21:35</strong>
            <a href="#a" class="layerpopup1" onclick="aa">Test Schedule</a>
            <img src="../images/common/icon_15age.gif" alt="Test Rating">
        """.encode('utf-8')

    def test_get_tcast_start_hour(self):
        """Test to get start hour of t.cast channel."""
        start_hour = self.parser.get_tcast_start_hour(self.channel)
        self.assertEqual(start_hour, 5)

        cinef_channel, _ = BroadcastCompany.objects.get_or_create(bc_name="Cinef")
        start_hour = self.parser.get_tcast_start_hour(cinef_channel)
        self.assertEqual(start_hour, 6)

        test_channel, _ = BroadcastCompany.objects.get_or_create(bc_name="Test")
        start_hour = self.parser.get_tcast_start_hour(test_channel)
        self.assertEqual(start_hour, 5)

    def test_get_tcast_single_schedule(self):
        """Test to make single schedule"""

        original_data_parsed = BeautifulSoup(self.original_data, 'html.parser')
        date = timezone.now()

        result = self.parser.parse_schedule_item(original_data_parsed, date)
        self.assertEqual(result['title'], "Test Schedule")
        self.assertEqual(result['start_time'].hour, 21)
        self.assertEqual(result['start_time'].minute, 35)

    def test_get_tcast_channel_ratings(self):
        """Test to get rating information from schedule of t.cast channels."""
        rating = self.parser.get_rating("../images/common/icon_15age.gif")
        self.assertEqual(rating, 15)

    def test_get_tcast_schedule(self):
        """Test to get t.cast channel schedule."""
        today = timezone.datetime.today()
        end_date = self.parser.get_channel_schedule("http://www.imtcast.com/screen/program/schedule.jsp")

        print("Today: " + str(today))
        print("Next schedule date: " + str(end_date))
        self.assertNotEqual(today, end_date)
        self.assertEqual(today < end_date, True)


class DeleteLastWeekScheduleTest(TestCase):
    """Test to delete schedules of last week."""

    def setUp(self):
        """Make schedules from 3 days ago to 2 days after today."""
        self.channel, _ = BroadcastCompany.objects.get_or_create(bc_name="Screen")

        day_list = list(range(-2, 3))

        for day in day_list:
            start_date = timezone.datetime.today() + timezone.timedelta(days=day)
            new_schedule = MovieSchedule(title="Test", broadcast_company=self.channel, start_time=start_date)
            new_schedule.save()

    def test_deleting_schedule(self):
        """Test whether schedule deleting method is working."""
        self.assertEqual(MovieSchedule.objects.all().count(), 5)

        today_date = timezone.datetime.today() - timezone.timedelta(days=1)
        MovieSchedule.objects.filter(start_time__lt=today_date).delete()

        self.assertEqual(MovieSchedule.objects.all().count(), 3)


class ModifyTodayScheduleTest(TestCase):
    """Test to modify today's schedule. (For CJ E&M channels)"""

    def setUp(self):
        """Make old schedules example."""
        self.channel, _ = BroadcastCompany.objects.get_or_create(bc_name="Screen")
        start_time = timezone.datetime(2017, 6, 30, 1, 30, 0)

        for i in range(5):
            new_schedule = MovieSchedule(title="test", broadcast_company=self.channel, start_time=start_time)
            new_schedule.save()
            start_time = start_time + timezone.timedelta(hours=1)

    def test_modify_schedule(self):
        """Change schedule time."""
        schedules = MovieSchedule.objects.all()

        self.assertEqual(schedules[0].start_time.hour, 1)
        self.assertEqual(schedules[0].start_time.minute, 30)

        self.assertEqual(schedules[len(schedules)-1].start_time.hour, 5)
        self.assertEqual(schedules[len(schedules)-1].start_time.minute, 30)

        new_start_time = timezone.datetime(2017, 6, 30, 2, 00, 0) - timezone.timedelta(minutes=30)
        new_end_time = timezone.datetime(2017, 6, 30, 6, 00, 0) + timezone.timedelta(minutes=30)

        old_schedules = MovieSchedule.objects.filter(Q(start_time__range=(new_start_time, new_end_time)) &
                                                     Q(broadcast_company=self.channel))
        old_schedules.delete()

        new_start_time = new_start_time + timezone.timedelta(minutes=30)

        for i in range(5):
            new_schedule = MovieSchedule(title="test", broadcast_company=self.channel, start_time=new_start_time)
            new_schedule.save()
            new_start_time = new_start_time + timezone.timedelta(hours=1)

        new_schedules = MovieSchedule.objects.all()

        self.assertEqual(new_schedules[0].start_time.hour, 2)
        self.assertEqual(new_schedules[0].start_time.minute, 0)

        self.assertEqual(new_schedules[len(new_schedules)-1].start_time.hour, 6)
        self.assertEqual(new_schedules[len(new_schedules)-1].start_time.minute, 0)
