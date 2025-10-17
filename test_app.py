import unittest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app import create_organizer, read_organizer, update_organizer, delete_organizer, OrganizerCreate

class TestOrganizerCRUD(unittest.TestCase):

    @patch('app.get_connection')
    def test_create_organizer(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]

        org_in = OrganizerCreate(name="Test Org", contact_info="contact@example.com")
        result = create_organizer(org_in)

        self.assertEqual(result.id, 1)
        self.assertEqual(result.name, "Test Org")
        self.assertEqual(result.contact_info, "contact@example.com")

        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO organizers (name, contact_info) OUTPUT INSERTED.id VALUES (?, ?)",
            "Test Org", "contact@example.com"
        )
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('app.get_connection')
    def test_read_organizer_found(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, "Test Org", "contact@example.com")

        result = read_organizer(1)

        self.assertEqual(result.id, 1)
        self.assertEqual(result.name, "Test Org")
        self.assertEqual(result.contact_info, "contact@example.com")

    @patch('app.get_connection')
    def test_read_organizer_not_found(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        with self.assertRaises(HTTPException) as context:
            read_organizer(999)
        self.assertEqual(context.exception.status_code, 404)

    @patch('app.get_connection')
    def test_update_organizer(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1

        org_in = OrganizerCreate(name="Updated Org", contact_info="update@example.com")
        result = update_organizer(1, org_in)

        self.assertEqual(result.id, 1)
        self.assertEqual(result.name, "Updated Org")
        self.assertEqual(result.contact_info, "update@example.com")

        mock_cursor.execute.assert_called_once_with(
            "UPDATE organizers SET name=?, contact_info=? WHERE id=?",
            "Updated Org", "update@example.com", 1
        )
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('app.get_connection')
    def test_update_organizer_not_found(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 0

        org_in = OrganizerCreate(name="Updated Org", contact_info="update@example.com")

        with self.assertRaises(HTTPException) as context:
            update_organizer(999, org_in)
        self.assertEqual(context.exception.status_code, 404)

    @patch('app.get_connection')
    def test_delete_organizer(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1

        result = delete_organizer(1)
        self.assertEqual(result, {"detail": "Organizer deleted"})

        mock_cursor.execute.assert_called_once_with("DELETE FROM organizers WHERE id=?", 1)
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('app.get_connection')
    def test_delete_organizer_not_found(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 0

        with self.assertRaises(HTTPException) as context:
            delete_organizer(999)
        self.assertEqual(context.exception.status_code, 404)


if __name__ == '__main__':
    unittest.main()
