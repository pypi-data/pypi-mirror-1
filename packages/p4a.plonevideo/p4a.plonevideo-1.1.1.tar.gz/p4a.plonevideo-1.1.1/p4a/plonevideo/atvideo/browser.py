import transaction
from zope import component
from p4a.video.migration import IMigrator
from p4a.plonevideo.atvideo.interfaces import IATVideo

class ATVideoMigrationView(object):
    """A view for migrating ATVideo content to Plone4ArtistsVideo.
    """
    
    @property
    def should_migrate(self):
        return bool(self.request.form.get('migrate', False))

    @property
    def dry_run(self):
        return bool(self.request.form.get('dry_run', True))

    def migrate(self):
        """Invoke the migration mechanism and return a status message.
        """
        migrator = component.getUtility(IMigrator)

        transaction.begin()
        count = migrator.migrate(self.context, IATVideo)
        
        msg_suffix = ''
        if self.dry_run:
            transaction.abort()
            msg_suffix = ', which were rolled back due to running ' \
                         'in "dry run" mode'
        else:
            transaction.commit()

        if count > 0:
            msg = 'Successfully migrated %i object(s)' % count
            msg += msg_suffix
        else:
            msg = 'No objects were migrated'
        
        return msg

    def __call__(self):
        kwargs = {}
        
        if self.should_migrate:
            self.request.form['portal_status_message'] = self.migrate()

        return self.index(**kwargs)
