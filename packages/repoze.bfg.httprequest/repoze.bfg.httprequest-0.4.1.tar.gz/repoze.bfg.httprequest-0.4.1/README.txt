Overview
========

The motivation for this package is to encourage the use of request
type adaptation instead of depending on packages with request type
definitions.

Instead of subclassing the request interface, we encourage an
adaptation pattern:

  >>> from repoze.bfg.interfaces import IRequest
  >>> IGZipRequest = IRequest({'http_accept_encoding': 'gzip'})

An event handler listens for the ``INewRequest`` event and
automatically marks the request with interfaces as needed to adapt the
request to the request types that it may apply for.

To complete the example above, a request would come in with an HTTP
environment like the following:

  {'http_accept_encoding': 'compress, gzip'}

Since we've previouly adapted the request to an accept-encoding of
'gzip', the adaptation machinery will mark the interface such that
this environment will match the ``IGZipRequest`` interface.

This would be an alternative to subclassing, where we would manually
have to set up an event listener that interprets the request
environment and marks the request with the interface.

  >>> class IGZipRequest(IRequest):
  ...     """Marker interface for requests for gzipped response."""

Credits
-------

Stefan Eletzhofer <stefan.eletzhofer@inquant.de> and Malthe Borch
<mborch@gmail.com>.

