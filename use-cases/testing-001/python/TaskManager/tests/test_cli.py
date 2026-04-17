import unittest
from datetime import datetime, date
from unittest.mock import patch, MagicMock
import sys

from cli import parse_date, format_task, main
from models import TaskStatus, TaskPriority

class TestParseDate(unittest.TestCase):

    def test_valid_date(self):
        result = parse_date("2026-04-17")
        self.assertEqual(result, date(2026, 4, 17))

    def test_none_or_empty(self):
        self.assertIsNone(parse_date(None))
        self.assertIsNone(parse_date(""))

    def test_invalid_date(self):
        with self.assertRaises(ValueError):
            parse_date("17-04-2026")

class DummyTask:
    def __init__(self):
        self.id = "1234567890abcdef"
        self.title = "Test Task"
        self.description = "Test Description"
        self.status = TaskStatus.TODO
        self.priority = TaskPriority.HIGH
        self.due_date = date(2026, 4, 20)
        self.tags = ["work", "urgent"]
        self.created_at = datetime(2026, 4, 17, 10, 30)


class TestFormatTask(unittest.TestCase):

    def test_format_output(self):
        task = DummyTask()
        output = format_task(task)

        self.assertIn("[ ]", output)  # status
        self.assertIn("!!!", output)  # priority
        self.assertIn("Test Task", output)
        self.assertIn("Test Description", output)
        self.assertIn("Due: 2026-04-20", output)
        self.assertIn("Tags: work, urgent", output)
        self.assertIn("Created: 2026-04-17 10:30", output)

class TestMainCLI(unittest.TestCase):

    @patch("cli.TaskManager")
    def test_create_command(self, mock_task_manager):
        mock_instance = MagicMock()
        mock_instance.create_task.return_value = "abc123"
        mock_task_manager.return_value = mock_instance

        test_args = [
            "prog",
            "create",
            "Test Task",
            "-d", "Desc",
            "-p", "3",
            "-u", "2026-04-20",
            "-t", "work,urgent"
        ]

        with patch.object(sys, "argv", test_args):
            main()

        mock_instance.create_task.assert_called_once()
    
    @patch("cli.TaskManager")
    def test_list_command(self, mock_task_manager):
        mock_instance = MagicMock()
        mock_instance.list_tasks.return_value = []
        mock_task_manager.return_value = mock_instance

        test_args = ["prog", "list"]

        with patch.object(sys, "argv", test_args):
            main()

        mock_instance.list_tasks.assert_called_once()


    @patch("cli.TaskManager")
    def test_invalid_date_error(self, mock_task_manager):
        test_args = [
            "prog",
            "create",
            "Task",
            "-u", "invalid-date"
        ]

        with patch.object(sys, "argv", test_args):
            # Should not crash
            main()

