#!/usr/bin/python3

import pathlib
import mimetypes

from flask import Response, request, abort, send_file

class FileShuttle(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        pass

    def _send_file_nginx(self, file_path, mimetype=None):
        """Sends a response indicating that nginx should serve this file using
        X-Accel-Mapping.
        """
        mapping = request.headers.get('X-Accel-Mapping')
        if not mapping:
            raise KeyError("Missing X-Accel-Mapping header")
        fs_path_str, web_path_str = map(lambda p: p.strip(), mapping.split('=', 1))

        # web_path is treated as a POSIX path, but fs_path is native
        # allows for testing on Windows
        fs_path, web_path = pathlib.Path(fs_path_str), pathlib.PurePosixPath(web_path_str)

        if not all(p.is_absolute() for p in (fs_path, web_path)):
            raise KeyError("X-Accel-Mapping paths are not absolute")
        if not file_path.is_relative_to(fs_path):
            abort(404)
        result_path = pathlib.PurePosixPath(web_path / file_path.relative_to(fs_path))

        if not mimetype:
            mimetype, encoding = mimetypes.guess_type(file_path, strict = False)

        # return this file
        file_stat = file_path.stat()
        return Response(headers = {
            'Content-Length': file_stat.st_size,
            'Content-Type': mimetype,
            'X-Accel-Redirect': str(result_path),
        })

    def send_file(self, file_path, mimetype=None, as_attachment=False, download_name=None,
                  attachment_filename=None, conditional=True, etag=True, add_etags=None,
                  last_modified=None, max_age=None, cache_timeout=None):
        """Send the given file path to the client.  Note that unlike :meth:`flask.send_file`,
        this function does not take a file-like object.
        """
        file_path = pathlib.Path(file_path)
        if not file_path.is_absolute():
            # non-absolute paths should be relative to flask's root to match normal flask.send_file
            file_abs_path = pathlib.Path(self.app.root_path) / file_path
        else:
            file_abs_path = file_path

        sendfile_type = request.headers.get('X-Sendfile-Type')
        if sendfile_type == 'X-Accel-Redirect':
            return self._send_file_nginx(file_abs_path, mimetype)
        elif sendfile_type is not None:
            raise TypeError(f"Unknown X-Sendfile-Type '{sendfile_type}'")
        return send_file(
            file_path, mimetype, as_attachment, download_name, attachment_filename,
            conditional, etag, add_etags, last_modified, max_age, cache_timeout
        )
