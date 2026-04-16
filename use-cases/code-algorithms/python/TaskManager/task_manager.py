import argparse
from datetime import datetime, timedelta

from models import TaskPriority, Task, TaskStatus
from storage import TaskStorage


class TaskManager:
    def __init__(self, storage_path="tasks.json"):
        self.storage = TaskStorage(storage_path)

    def create_task(self, title, description="", priority_value=2,
                    due_date_str=None, tags=None):

        if tags is None:
            tags = []

        try:
            priority = TaskPriority(priority_value)
        except ValueError:
            return None

        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            except ValueError:
                return None

        task = Task(title, description, priority, due_date, tags)
        return self.storage.add_task(task)

    def list_tasks(self, status_filter=None, priority_filter=None, show_overdue=False):
        if status_filter:
            try:
                status = TaskStatus(status_filter)
            except ValueError:
                raise ValueError("Invalid status")
            return self.storage.get_tasks_by_status(status)

        if priority_filter:
            try:
                priority = TaskPriority(priority_filter)
            except ValueError:
                raise ValueError("Invalid priority")
            return self.storage.get_tasks_by_priority(priority)

    def update_task_status(self, task_id, new_status_value):
        try:
            new_status = TaskStatus(new_status_value)
        except ValueError:
            return False

        if new_status == TaskStatus.DONE:
            task = self.storage.get_task(task_id)
            if not task:
                return False
            task.mark_as_done()
            self.storage.save()
            return True

        return self.storage.update_task(task_id, status=new_status)

    def update_task_priority(self, task_id, new_priority_value):
        new_priority = TaskPriority(new_priority_value)
        return self.storage.update_task(task_id, priority=new_priority)

    def delete_task(self, task_id):
        return self.storage.delete_task(task_id)

    def get_task_details(self, task_id):
        return self.storage.get_task(task_id)

    def add_tag_to_task(self, task_id, tag):
        task = self.storage.get_task(task_id)
        if not task:
            return False

        if tag not in task.tags:
            task.tags.append(tag)
            self.storage.save()

        return True

    def remove_tag_from_task(self, task_id, tag):
        task = self.storage.get_task(task_id)
        if not task:
            return False

        if tag not in task.tags:
            return False

        task.tags.remove(tag)
        self.storage.save()
        return True

    def get_statistics(self):
        tasks = self.storage.get_all_tasks()
        total = len(tasks)

        # Count by status
        status_counts = {status.value: 0 for status in TaskStatus}
        for task in tasks:
            status_counts[task.status.value] += 1

        # Count by priority
        priority_counts = {priority.name: 0 for priority in TaskPriority}
        for task in tasks:
            priority_counts[task.priority.name] += 1

        # Count overdue
        overdue_count = len([
            task for task in tasks
            if task.is_overdue() and task.status != TaskStatus.DONE])

        # Count completed in last 7 days
        completed_recently = len([
            task for task in tasks
            if task.status == TaskStatus.DONE
            and task.completed_at
            and task.completed_at >= seven_days_ago
        ])


        return {
            "total": total,
            "by_status": status_counts,
            "by_priority": priority_counts,
            "overdue": overdue_count,
            "completed_last_week": completed_recently
        }

