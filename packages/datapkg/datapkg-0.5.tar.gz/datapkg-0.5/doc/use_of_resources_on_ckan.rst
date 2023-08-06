This is an RFC related to use of package resources on ckan.net

Big distinction between non-packaged and packaged data.

At present almost data is non-packaged.

  * For normal files use simple mime-type.
    * what about about apis? Put this as api/...
  * For distribution put: dist/{value for that file as normal}
    * api dists ...


Installation Process
====================

  1. List package resources.
  2. If there is a dist use it (so just unpack)
  3. If there isn't pick one package resource
    * First install the metadata
    * If downloadable (not an api) then download (and unpack to same directory)

Distinguish between a distribution object and the Package

