# PodMin, the People's Podcast Platform

This is PodMin, a Django project for managing podcasts. It grew organically
in the pungent soil of necessity, and has some oddities and warts as a result.

PodMin was originally designed to process audio files uploaded by an automated
system at a local radio station and turn them into a podcast. It was a rough
and more or less ready set of scripts for generating RSS feeds, which eventually
grew a UI and became more and more useful for general podcast maintenance.

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
* Many more

## Feature priorities:

* Test suite
* Documentation and in-app user help
* UI improvements throughout
* API for pulling show notes and other data out
