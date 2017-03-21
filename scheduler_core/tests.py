from django.test import TestCase
from scheduler_core.models import BroadcastCompany, LatestUpdate
import tasks
from django.utils import timezone


# Create your tests here.
class MovieScheduleTestCase(TestCase):
    def setUp(self):
        bc = BroadcastCompany.objects.create(bc_name="OCN")
        LatestUpdate.objects.create(broadcast_company=bc,
                                    latest_update=timezone.datetime(2017, 3, 6, tzinfo=timezone.get_current_timezone()))

    def test_get_ocn_schedule(self):
        """ Test for getting OCN schedule """
        tasks.save_cj_channel_schedule("OCN", "http://ocn.tving.com/ocn/schedule?startDate=")

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
