# Flask-FileShuttle

Replacement / wrapper around Flask's `send_file` functionality with nginx support.

Implements `X-Accel-Redirect` based on [Rack::Sendfile][].

[Rack::Sendfile]: https://www.rubydoc.info/gems/rack/Rack/Sendfile

## Dependencies

Currently requires Python 3.9 or newer due to the use of `PurePath.is_relative_to`.
