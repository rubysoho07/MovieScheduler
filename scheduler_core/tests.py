# -*- coding: utf-8 -*-
from django.test import TestCase
from scheduler_core.models import BroadcastCompany
from scheduler_core.movie_schedule_parser import MovieScheduleParser
import tasks
from django.utils import timezone
from bs4 import BeautifulSoup


# Create your tests here.
class CJScheduleTestCase(TestCase):
    def setUp(self):
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
        result = MovieScheduleParser.get_cj_channel_ratings("age15")
        self.assertEqual(result, 15)

    def test_parse_cj_schedule_item(self):
        result = MovieScheduleParser.parse_cj_schedule_item(self.schedule_table[0], self.schedule_date)

        self.assertEqual(result['title'], "Test Program 1", "Check title")
        self.assertEqual(result['start_time'].hour, 3, "Check start time(hour)")
        self.assertEqual(result['start_time'].minute, 10, "Check start time(minute)")
        self.assertEqual(result['rating'], 19, "Check rating")

    def test_get_cj_daily_schedule(self):
        result = MovieScheduleParser.get_cj_daily_schedule(self.schedule_date, self.schedule_table)
        self.assertEqual(len(result), 1)

    def test_get_cj_schedule(self):
        """ Test for getting CJ E&M channel schedule """
        date_str = timezone.datetime.strftime(self.schedule_date, "%Y%m%d")
        result = MovieScheduleParser.get_cj_channels("http://ocn.tving.com/ocn/schedule?startDate=" + date_str)
        self.assertNotEqual(len(result), 0)

    def test_save_cj_channel_schedule(self):
        """ Test for getting and saving CJ E&M channel schedule """
        tasks.save_cj_channel_schedule("OCN", "http://ocn.tving.com/ocn/schedule?startDate=")


class KakaoTVScheduleTestCase(TestCase):
    def setUp(self):
        pass

    def test_get_kakao_tv_schedule(self):
        """
        Test for getting KaKao TV (Animation, Movie) schedule.
        """
        tasks.save_kakao_tv_schedule()


class TCastScheduleTestCase(TestCase):
    def setUp(self):
        self.channel, _ = BroadcastCompany.objects.get_or_create(bc_name="Screen")

    def test_get_tcast_single_schedule(self):
        """ Test for making single schedule """
        original_data = """
        <strong>21:35</strong>
        <a href="#a" class="layerpopup1" onclick="aa">Test Schedule</a>
        <img src="../images/common/icon_15age.gif" alt="Test Rating">
        """.encode('utf-8')
        original_data_parsed = BeautifulSoup(original_data, 'html.parser')
        date = timezone.now()

        result = MovieScheduleParser.parse_tcast_schedule_item(original_data_parsed, date)
        self.assertEqual(result['start_time'].hour, 21)
        self.assertEqual(result['start_time'].minute, 35)

    def test_get_tcast_schedule(self):
        """ Test for getting t.cast channel schedule. """

        end_date = MovieScheduleParser.get_tcast_channel_schedules(
            self.channel,
            "http://www.imtcast.com/cinef/program/schedule.jsp",
            timezone.datetime(2017, 3, 24, tzinfo=timezone.get_current_timezone()))

        self.assertEqual(end_date.day, 1)
        self.assertEqual(end_date.month, 4)

    def test_get_tcast_next_schedule(self):
        """ Test for getting t.cast channel schedule on next week. """
        MovieScheduleParser.get_tcast_channel_schedules(self.channel,
                                                        "http://www.imtcast.com/screen/program/schedule.jsp",
                                                        timezone.datetime(2017, 3, 28,
                                                                          tzinfo=timezone.get_current_timezone()))
