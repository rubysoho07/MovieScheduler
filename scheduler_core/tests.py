# coding=utf-8
#-*- coding: utf-8 -*-
from django.test import TestCase
from scheduler_core.models import BroadcastCompany, LatestUpdate
from scheduler_core.movie_schedule_parser import MovieScheduleParser
import tasks
from django.utils import timezone
from bs4 import BeautifulSoup


# Create your tests here.
class CJScheduleTestCase(TestCase):
    def setUp(self):
        bc = BroadcastCompany.objects.create(bc_name="OCN")
        LatestUpdate.objects.create(broadcast_company=bc,
                                    latest_update=timezone.datetime(2017, 3, 27,
                                                                    tzinfo=timezone.get_current_timezone()))

    def test_get_ocn_schedule(self):
        """ Test for getting OCN schedule """
        test_list = tasks.save_cj_channel_schedule("OCN", "http://ocn.tving.com/ocn/schedule?startDate=")
        self.assertEqual(test_list, None)

    def test_get_catchon2_schedule(self):
        """ Test for getting Catch On 2 schedule """
        tasks.save_cj_channel_schedule("CatchOn2", "http://catchon.tving.com/catchon/schedule2?startDate=")


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
