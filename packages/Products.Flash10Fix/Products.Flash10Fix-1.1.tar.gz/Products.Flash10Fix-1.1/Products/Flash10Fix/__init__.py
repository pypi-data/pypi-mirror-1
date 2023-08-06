# augment list of inline mimetypes to fix problems with
# Flash 10's security checks (see http://dev.plone.org/plone/ticket/8624)

new_type = 'application/x-shockwave-flash'

from Products.ATContentTypes.content.file import ATFile
classes = [ATFile]

for klass in classes:
    if new_type not in klass.inlineMimetypes:
        klass.inlineMimetypes = tuple(list(klass.inlineMimetypes) + [new_type])

import logging
logging.getLogger('Flash10Fix').info('Patched the following classes: %s' % ', '.join([c.__name__ for c in classes]))
