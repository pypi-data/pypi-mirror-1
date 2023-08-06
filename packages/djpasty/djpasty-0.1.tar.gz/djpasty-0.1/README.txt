Description
===========

Djpasty makes it easy to run Django with the Paste_ web-server. It
does this by providing a management command which (just like
`runserver`) starts the web-server.

The server directly serves the media folder. This makes it an ideal
solution for small sites or applications for which easy of deployment
is more important than raw performance.

When serving the static files it looks at the `MEDIA_ROOT` and
`MEDIA_URL` settings. Make sure that the `MEDIA_URL` looks like
`/media/` and not like `http://nohost/media/`. Admin media will be
taken care of automatically.
