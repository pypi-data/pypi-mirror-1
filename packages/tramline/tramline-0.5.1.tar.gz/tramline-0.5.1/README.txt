Tramline
========

Introduction
------------

Tramline is a upload and download accelerator that plugs into Apache,
using mod_python. Its aim is to make downloading and uploading large
media to an application server easy and fast, without overloading the
application server with large amounts of binary data.

Tramline integrates into Apache using mod_python. The application
server is assumed to sit behind Apache, for instance hooked up using
mod_proxy or mod_rewrite.

Tramline takes over uploading and downloading files, handling these
within Apache. Only a small configuration change in Apache should be
necessary to enable tramline.

The application server remains in complete control over security, page
and form rendering, and everything else. Minimal changes are necessary
to any application to enable it to work with tramline; in fact it's
just setting two response headers in a few places in the code.

How it works
------------

Given a 'tramline_data' directory that's accessible to Apache (and the
appserver if it needs to), there are two subdirectories, 'upload' and
'repository'. 'upload' will only contain temporary files currently
being uploaded, while 'repository' contains the files successfully
uploaded.

Tramline makes sure uploaded files (in a form POST) don't appear at
the appserver but go directly into the filesystem. The only thing the
appserver sees is a unique identifier of the uploaded file, so that
the appserver can access it when needed. The binary data is gone at
the time the POST reaches the appserver. You can check whether
tramline is in use by checking the 'tramline' header in the request,
though frequently there's no need to do so.

The appserver can control whether it accepts the uploaded file(s) in
the output response header; if a 'tramline_ok' header is present, the
uploaded files will be moved into the repository, 'committing' the
upload. If it's absent, the uploaded files will be removed, 'aborting'
the upload.

Tramline also can handle downloads. The appserver can signal in the
response headers that tramline should push a file out of the
filesystem to the end user, by adding a 'tramline_file' response
header. The data of the file body as received during upload,
containing the unique identifier of the file, should be sent back as
the response body.  Again the appserver does not see the binary data
but only sends out an identifier to make the file be served by Apache.

Tramline makes it relatively easy to make an application that handled
large file uploads correctly without tramline installed as well. After
all, the application handles a tramline id just like it would handle
an uploaded file; the data is stored and served again. Of course
mixing tramline uploaded files and appserver uploaded files in the
same setup of your application would get complicated, but this feature
does make it nice to be able to test your application without tramline
available.

So:

* to handle upload:

  - file contents will contain the unique file id.

  - send out 'tramline_ok' header if file is accepted. Failure 
    to send out this header will cause the file to be rejected.

* to detect whether tramline took care of an upload:

  - look for a 'tramline' header in the request.

* to handle download:

  - send out 'tramline_file' header in response if the file can
    be downloaded.

  - send out response body with unique file id.
