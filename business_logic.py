from datetime import datetime

# [US1] Teslim tarihi hesaplama mantığı
def get_deadline_status(deadline_str, today_date):
    deadline_date = datetime.strptime(deadline_str, '%Y-%m-%d').date()
    delta = (deadline_date - today_date).days
    if delta < 0:
        return 'Overdue'
    return f"{delta} Days Remaining"

# [US2] Görev ilerleme (yüzde) hesaplama mantığı
def calculate_progress(total_tasks, completed_tasks):
    if total_tasks == 0:
        return 0
    return int((completed_tasks / total_tasks) * 100)

# [US3] Kalan bütçe hesaplama mantığı
def calculate_remaining_budget(budget, total_expenses):
    return budget - total_expenses