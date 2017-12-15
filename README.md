# PodMin, the People's Podcast Platform

This is PodMin, a Django project for managing podcasts. It grew organically,
in the pungent soil of necessity, and has some oddities and warts as a result.

PodMin was originally designed to process audio files uploaded by an automated
system at a local radio station and turn them into a podcast. It was a rough
and more or less ready set of scripts for generating RSS feeds, which eventually
grew a UI and became more and more useful for general podcast maintenance. It
is currently in use at http://podmin.hypothetical.net

## Main features:

* General iTunes-compatible podcast feeds including CDATA fields
* Comprehensive episode management, including at-will publish/depublish, buffer
  (upload now, publish later) and mothball functions.
* Epsiode art and show notes
* Tag audio files with notes, art, credits, etc
* Optionally auto-name audio files
* Listen to episodes with Javascript audio player
* Generates static RSS files for efficient serving and bullet-proof availability
* Upload files to a directory and PodMin can automatically process them into a
  podcast (some assembly required)
* Mothball archives can be exported/imported

## Main deficits:

* No test suite :-(
* Sparse documentation and end-user help
* No internationalization
* Rich and diverse bug ecosystem

## Feature priorities:

* Test suite
* Documentation and in-app user help
* UI improvements throughout
* API for pulling show notes and other data out

## Installation

Sorry, this is not documented at this time, but PodMin is a Django project and
should be deployable via any of the usual Django deployment methods.

## Development

You can spin up a development environment with docker-compose (make sure you
  have docker and docker-compose installed). in the top level directory do:

`docker-compose up`

And you should find the dev instance running on `http://localhost:8001`

Please feel free to file bugs or feature requests here, or submit pull requests
if you feel like fixing or adding something.
