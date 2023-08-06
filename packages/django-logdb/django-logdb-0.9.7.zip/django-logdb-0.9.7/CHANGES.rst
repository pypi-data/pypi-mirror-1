CHANGES
=======

0.9.7
-----
- Aggregation of logs is now done in a transaction.
- Changed templates to allow for easier customization.
- Fixed an error in tests.py that occured with Python 2.5.
- Added 2 new settings: INTERVAL and HISTORY_DAYS with the defaults as before.
- Moved JS code from extrastyle to extrahead block in templates.

0.9.6
-----

- Updated README to include examples to serve the media.
- Fixed a problem with saving objects or instances as log record arguments
  (picklefield).
- Fixed a problem with unicode characters in the arguments.
- Replaced library picklefield with JSONField and TupleField.

0.9.5
-----
- Removed Django as a requirement (although it's still required) to prevent
  conflicts with djangorecipe.

0.9.4
-----
- Fixed manifest to include changes.

0.9.3
-----
- Added template for LogEntry view.
- Renamed templates to Django's default. You can still override them.

0.9.2
-----
- Initial release on PyPI.