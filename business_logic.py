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

# [US4] Görev tamamlanma durumu yönetimi
def can_delete_task(task_owner_user_id, current_user_id):
    return task_owner_user_id == current_user_id

def get_task_completion_summary(tasks):
    total = len(tasks)
    completed = sum(1 for t in tasks if t.get('is_completed'))
    pending = total - completed
    return {'total': total, 'completed': completed, 'pending': pending}

# [US5] Projeleri deadline'a göre sıralama mantığı
def sort_projects_by_deadline(projects):
    return sorted(projects, key=lambda p: p['deadline'])

def get_overdue_projects(projects, today_str):
    return [p for p in projects if p['deadline'] < today_str]