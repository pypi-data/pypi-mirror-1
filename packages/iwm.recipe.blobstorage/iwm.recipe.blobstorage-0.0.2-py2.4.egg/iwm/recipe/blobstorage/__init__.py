import logging, os

import pkg_resources

import zc.buildout
import zc.recipe.egg

logger = logging.getLogger('iwm.recipe.blobstorage')


class Recipe:

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options
        path = options.get('path')
        if path is None:
            path = os.path.join(buildout['buildout']['parts-directory'],
                                self.name, 'Data.fs')
            blob_dir = os.path.join(buildout['buildout']['parts-directory'],
                                self.name, 'blobs')
            self.make_part = True
        else:
            path = os.path.join(buildout['buildout']['directory'], path)
            blob_dir = options.get('blob-dir', None)
            if blob_dir is None:
                logging.getLogger('iwm.recipe.blobstorage').error(
                    "If path option is given, blob-dir must also be defined")
                blob_dir = os.path.join(buildout['buildout']['parts-directory'],
                                self.name, 'blobs')
                logging.getLogger('iwm.recipe.blobstorage').error(
                    "Using default %s", blob_dir)
            for part in (path, blob_dir):
                if not os.path.exists(part):
                    logging.getLogger('iwm.recipe.blobstorage').error(
                        "%s does not exist", parts)
            self.make_part = False

        storage_options = {}
        for option in options.get('storage-options', '').split('\n'):
            option = option.strip()
            if not option:
                continue
            option = option.split(' ', 1)
            if (len(option) == 1) or not option[1].strip():
                logger.error('%s: storage-option, %s, has no value',
                             self.name, option[0]
                             )
                raise zc.buildout.UserError("Invalid storage-option", option[0])
            storage_options[option[0]] = option[1]

        storage_options = '\n  '.join([
            ' '.join(option)
            for option in storage_options.iteritems()
            ])

        options['path'] = path
        options['blob-dir'] = blob_dir
        options['zconfig'] = template % dict(
                                            blobdir = blob_dir,
                                            path = path,
                                            options = storage_options)

    def install(self):
        if self.make_part:
            for part in (os.path.dirname(self.options['path']),
                         self.options['blob-dir']):
                if not os.path.exists(part):
                    os.mkdir(part)
        return ()

    def update(self):
        pass

template = """\
<zodb>
  <blobstorage>
    blob-dir %(blobdir)s
    <filestorage>
      path %(path)s
    </filestorage>
  </blobstorage>

  %(options)s

</zodb>
"""
