import tempfile
import unittest
from pathlib import Path
import app,management

class ServicePrefixes(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.old=app.DATA;app.DATA=Path(self.folder.name);app.initialize('service-prefix-password-123')
    def tearDown(self):app.DATA=self.old;self.folder.cleanup()
    def test_five_services_have_independent_letters_and_keep_global_numbering(self):
        labels=[app.issue(n,'prefix-for-service-request-'+str(n))['label'] for n in range(1,6)]
        self.assertEqual(labels,['A001','B002','C003','D004','E005'])
    def test_changes_apply_only_to_new_tickets_and_retries_keep_original(self):
        old=app.issue(2,'old-prefix-ticket-request-123')
        with app.connect() as c:
            prefix=management.validate_service_prefix(c,'Z',2);c.execute('UPDATE services SET prefix=? WHERE id=2',(prefix,))
        new=app.issue(2,'new-prefix-ticket-request-123')
        self.assertEqual((old['label'],new['label']),('B001','Z002'))
        self.assertEqual(app.issue(2,old['request'])['label'],'B001')
        with app.connect() as c:
            for value in ['A','aa','1','ABCD','']:
                with self.assertRaises(ValueError):management.validate_service_prefix(c,value,2)
    def test_legacy_database_migration_does_not_rename_existing_labels(self):
        ticket=app.issue(2,'legacy-service-prefix-request')
        with app.connect() as c:
            c.execute("UPDATE tickets SET label='A001' WHERE id=?",(ticket['id'],));c.execute('ALTER TABLE services DROP COLUMN prefix')
        app.initialize()
        with app.connect() as c:self.assertEqual(c.execute('SELECT label FROM tickets WHERE id=?',(ticket['id'],)).fetchone()[0],'A001')
        self.assertEqual(app.issue(2,'post-migration-prefix-request')['label'],'B002')
