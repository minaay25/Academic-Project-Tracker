import unittest
from datetime import date
from business_logic import (
    calculate_progress,
    calculate_remaining_budget,
    get_deadline_status,
    can_delete_task,
    get_task_completion_summary,
    sort_projects_by_deadline,
    get_overdue_projects
)

class TestBusinessLogic(unittest.TestCase):

    # [US1] Deadline Testi
    def test_get_deadline_status(self):
        test_today = date(2026, 5, 24)
        self.assertEqual(get_deadline_status('2026-05-20', test_today), 'Overdue')
        self.assertEqual(get_deadline_status('2026-05-26', test_today), '2 Days Remaining')

    # [US2] İlerleme (Yüzde) Testi
    def test_calculate_progress(self):
        self.assertEqual(calculate_progress(4, 1), 25)
        self.assertEqual(calculate_progress(0, 0), 0)
        self.assertEqual(calculate_progress(5, 5), 100)

    # [US3] Bütçe Testi
    def test_calculate_remaining_budget(self):
        self.assertEqual(calculate_remaining_budget(1000.0, 250.0), 750.0)
        self.assertEqual(calculate_remaining_budget(500.0, 600.0), -100.0)

    # [US4] Görev Silme Yetki Testi
    def test_can_delete_task_authorized(self):
        self.assertTrue(can_delete_task(task_owner_user_id=3, current_user_id=3))

    def test_can_delete_task_unauthorized(self):
        self.assertFalse(can_delete_task(task_owner_user_id=3, current_user_id=7))

    def test_get_task_completion_summary_mixed(self):
        tasks = [
            {'is_completed': 1},
            {'is_completed': 0},
            {'is_completed': 1},
            {'is_completed': 0},
        ]
        result = get_task_completion_summary(tasks)
        self.assertEqual(result['total'], 4)
        self.assertEqual(result['completed'], 2)
        self.assertEqual(result['pending'], 2)

    def test_get_task_completion_summary_empty(self):
        result = get_task_completion_summary([])
        self.assertEqual(result['total'], 0)
        self.assertEqual(result['completed'], 0)
        self.assertEqual(result['pending'], 0)

    def test_get_task_completion_summary_all_done(self):
        tasks = [{'is_completed': 1}, {'is_completed': 1}]
        result = get_task_completion_summary(tasks)
        self.assertEqual(result['completed'], 2)
        self.assertEqual(result['pending'], 0)

    # [US5] Deadline Sıralama Testi
    def test_sort_projects_by_deadline_ascending(self):
        projects = [
            {'title': 'C', 'deadline': '2026-12-01'},
            {'title': 'A', 'deadline': '2026-06-01'},
            {'title': 'B', 'deadline': '2026-09-15'},
        ]
        sorted_projects = sort_projects_by_deadline(projects)
        self.assertEqual(sorted_projects[0]['title'], 'A')
        self.assertEqual(sorted_projects[1]['title'], 'B')
        self.assertEqual(sorted_projects[2]['title'], 'C')

    def test_sort_projects_by_deadline_single(self):
        projects = [{'title': 'Solo', 'deadline': '2026-07-01'}]
        self.assertEqual(sort_projects_by_deadline(projects), projects)

    def test_sort_projects_by_deadline_empty(self):
        self.assertEqual(sort_projects_by_deadline([]), [])

    def test_get_overdue_projects(self):
        projects = [
            {'title': 'Old', 'deadline': '2026-01-01'},
            {'title': 'Future', 'deadline': '2026-12-01'},
            {'title': 'AlsoOld', 'deadline': '2026-03-10'},
        ]
        overdue = get_overdue_projects(projects, '2026-05-30')
        self.assertEqual(len(overdue), 2)
        titles = [p['title'] for p in overdue]
        self.assertIn('Old', titles)
        self.assertIn('AlsoOld', titles)

    def test_get_overdue_projects_none(self):
        projects = [{'title': 'Future', 'deadline': '2026-12-01'}]
        self.assertEqual(get_overdue_projects(projects, '2026-05-30'), [])

if __name__ == '__main__':
    unittest.main()