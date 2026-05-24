import unittest
from datetime import date
from business_logic import calculate_progress, calculate_remaining_budget, get_deadline_status

class TestBusinessLogic(unittest.TestCase):

    # [US1] Deadline Testi
    def test_get_deadline_status(self):
        test_today = date(2026, 5, 24)
        self.assertEqual(get_deadline_status('2026-05-20', test_today), 'Overdue')
        self.assertEqual(get_deadline_status('2026-05-26', test_today), '2 Days Remaining')

    # [US2] İlerleme (Yüzde) Testi
    def test_calculate_progress(self):
        self.assertEqual(calculate_progress(4, 1), 25) # 4 görevden 1'i bittiyse %25 olmalı
        self.assertEqual(calculate_progress(0, 0), 0)  # Sıfıra bölünme hatası engeli
        self.assertEqual(calculate_progress(5, 5), 100)

    # [US3] Bütçe Testi
    def test_calculate_remaining_budget(self):
        self.assertEqual(calculate_remaining_budget(1000.0, 250.0), 750.0)
        self.assertEqual(calculate_remaining_budget(500.0, 600.0), -100.0) # Bütçe aşımı

if __name__ == '__main__':
    unittest.main()