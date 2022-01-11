# Flask-FileShuttle

Replacement / wrapper around Flask's `send_file` functionality with nginx support.

Implements `X-Accel-Redirect` based on [Rack::Sendfile][].

[Rack::Sendfile]: https://www.rubydoc.info/gems/rack/Rack/Sendfile

## Usage

On the application side:
```python
from flask_fileshuttle import FileShuttle

app = Flask(__name__)
shuttle = FileShuttle(app)
```
Use `shuttle.send_file` in place of `flask.send_file`.

In nginx, configure the following server blocks:
```
location @your_application {
	proxy_set_header   X-Sendfile-Type      X-Accel-Redirect;
	proxy_set_header   X-Accel-Mapping      /your_physical_path/=/your_web_path/;
}

location /your_web_path {
	internal;
	alias /your_physical_path;
}
```

## Dependencies

Currently requires Python 3.9 or newer due to the use of `PurePath.is_relative_to`.
