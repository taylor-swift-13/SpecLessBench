"""Regression tests for overlap-safe construction accounting."""
import datetime as dt,unittest
from summarize_total_cost import KEYS,provider_union,union_seconds

def t(seconds):return dt.datetime(2026,1,1,tzinfo=dt.timezone.utc)+dt.timedelta(seconds=seconds)
def usage(n):return {k:n for k in KEYS}
class AccountingTest(unittest.TestCase):
    def test_nested_and_overlapping_wall_time(self):
        self.assertEqual(union_seconds([(t(0),t(10)),(t(2),t(3)),(t(8),t(12)),(t(20),t(25))]),(17.0,2))
    def test_overlapping_provider_windows_are_counted_once(self):
        totals,merged,overlaps=provider_union({'one':[(t(0),t(10),usage(0),usage(100)),
            (t(5),t(15),usage(50),usage(160)),(t(20),t(30),usage(200),usage(230))],
            'two':[(t(0),t(3),usage(10),usage(20))]})
        self.assertEqual((totals['total_tokens'],merged,overlaps),(200,3,1))
    def test_counter_reset_is_rejected(self):
        with self.assertRaises(AssertionError):provider_union({'one':[(t(0),t(10),usage(0),usage(100)),
            (t(5),t(15),usage(50),usage(90))]})
if __name__=='__main__':unittest.main()
