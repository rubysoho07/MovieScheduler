# -*- coding: utf-8 -*-
from django.test import TestCase
from django.db.models import Q
from scheduler_core.models import BroadcastCompany, MovieSchedule
from scheduler_core.movie_schedule_parser import CJScheduleParser, TCastScheduleParser
from . import tasks
from django.utils import timezone
from bs4 import BeautifulSoup


# Create your tests here.
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

    def test_get_cj_schedule(self):
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
        self.parser_next_week = TCastScheduleParser(self.channel, timezone.datetime(2017, 4, 26))

    def test_get_tcast_single_schedule(self):
        """Test to make single schedule"""

        original_data = """
        <strong>21:35</strong>
        <a href="#a" class="layerpopup1" onclick="aa">Test Schedule</a>
        <img src="../images/common/icon_15age.gif" alt="Test Rating">
        """.encode('utf-8')
        original_data_parsed = BeautifulSoup(original_data, 'html.parser')
        date = timezone.now()

        result = self.parser.parse_schedule_item(original_data_parsed, date)
        self.assertEqual(result['start_time'].hour, 21)
        self.assertEqual(result['start_time'].minute, 35)

    def test_get_tcast_schedule(self):
        """Test to get t.cast channel schedule."""

        end_date = self.parser.get_channel_schedule("http://www.imtcast.com/screen/program/schedule.jsp")

        self.assertEqual(end_date.day, 28)
        self.assertEqual(end_date.month, 4)

    def test_get_tcast_next_schedule(self):
        """Test to get t.cast channel schedule on next week."""
        end_date = self.parser_next_week.get_channel_schedule("http://www.imtcast.com/screen/program/schedule.jsp")

        self.assertEqual(end_date.day, 28)
        self.assertEqual(end_date.month, 4)


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
