import os

from django.conf import settings
from django.contrib.staticfiles.storage import ManifestFilesMixin, ManifestStaticFilesStorage


class DeleteOriginalsMixin(ManifestFilesMixin):
    def post_process(self, *args, **kwargs):
        if not kwargs.get('dry_run'):
            files = super().post_process(*args, **kwargs)
            for name, hashed_name, processed in files:
                print(name, hashed_name, processed)
                # Delete copied over original file to prevent unhashed files from being served
                os.remove(settings.STATIC_ROOT + '/' + name)
                yield name, hashed_name, processed


class CustomStorage(DeleteOriginalsMixin, ManifestStaticFilesStorage):
    patterns = ()
