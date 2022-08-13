#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from audioop import add
from distutils import archive_util
from distutils.log import error
from email.policy import default
from fcntl import F_SEAL_SEAL
import json
from operator import ge
from os import stat
from sre_parse import State
from termios import VMIN
from unicodedata import name
from urllib import response
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
from models.models import db, Venue, Artist, Show
import config
import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db.init_app(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  all_venues = Venue.query.all()
  all_cities_states = set()

  # Mapping through venues
  for venue in all_venues:
    all_cities_states.add((venue.city,venue.state))

# Appending all cities and states
  all_cities = []
  for city,state in all_cities_states:
    all_cities.append({
      "city": city,
      "state": state,
      "venues": []
    })

  for venue in all_venues:
    for city in all_cities:
      if venue.city == city.get('city') and venue.state == city.get('state'):
        upcoming_shows = len(Show.query.join(Venue).filter(Show.start_time > datetime.datetime.utcnow()).all())

        city['venues'].append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": upcoming_shows
        })


  return render_template('pages/venues.html', areas=all_cities)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_query = request.form.get('search_term')
  search_result = Venue.query.filter(Venue.name.ilike('%' + search_query + '%')).all()
  search_array = []

  for items in search_result:
    num_upcoming_shows = Show.query.filter(Show.venue_id == items.id).count()
    search_array.append({
      "id":items.id,
      "name":items.name,
      "num_upcoming_shows":num_upcoming_shows
    })

    response = {
      "count": len(search_array),
      "data": search_array
    }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter(Venue.id ==venue_id).first()
  all_past_shows = Show.query.join(Venue, Show.venue_id == venue_id).filter(Show.start_time <= datetime.datetime.utcnow()).all()
  all_upcoming_shows = Show.query.join(Venue, Show.venue_id == venue_id).filter(Show.start_time > datetime.datetime.utcnow()).all()


  past_shows = [] 
  for show in all_past_shows:
    past_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
    })

  upcoming_shows = []
  for show in all_upcoming_shows:
    upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
    })

  data = {
    "id": venue.id,
      "name": venue.name,
      "city": venue.city,
      "state": venue.state,
      "address": venue.address,
      "phone": venue.phone,
      "image_link": venue.image_link,
      "facebook_link": venue.facebook_link,
      "genres": venue.genres,
      "website_link": venue.website_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows)
    }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead 
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
  # return json.dumps(request.form.name)

  try:
    new_venue = Venue(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
      image_link = form.image_link.data,
      website_link = form.website_link.data,
      seeking_talent = form.seeking_talent.data,
      seeking_description = form.seeking_description.data
    )
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
  # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  try:
    venue = Venue.query.get(venue_id)
    for show in venue.shows:
      db.session.delete(show)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    flash("Cannot Delete Venue")
  finally:
    db.session.close()
  return redirect(url_for('index'))

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  all_artists = []

  for artist in Artist.query.all():
    all_artists.append({
      "id": artist.id,
      "name": artist.name
    })

  return render_template('pages/artists.html', artists=all_artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_query = request.form.get('search_term')
  search_result = Artist.query.filter(Artist.name.ilike('%' + '%')).all()
  search_array = []
  for data in search_result:
    search_array.append({
      "id": data.id,
      "name": data.name
    })

  response = {
    "count": len(search_array),
    "data": search_array
  }


  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artist = Artist.query.filter(Artist.id == artist_id).first()
  all_past_shows = Show.query.join(Artist, Show.artist_id == artist.id).filter(Show.start_time <= datetime.datetime.utcnow()).all()
  all_upcoming_shows = Show.query.join(Artist, Show.artist_id == artist.id).filter(Show.start_time > datetime.datetime.utcnow()).all()


  past_shows = [] 
  for show in all_past_shows:
    past_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time
    })

  upcoming_shows = []
  for show in all_upcoming_shows:
    upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time
    })

  data = {
    "id": artist.id,
      "name": artist.name,
      "city": artist.city,
      "state": artist.state,
      "address": artist.address,
      "phone": artist.phone,
      "image_link": artist.image_link,
      "facebook_link": artist.facebook_link,
      "genres": artist.genres,
      "website_link": artist.website_link,
      "seeking_talent": artist.seeking_talent,
      "seeking_description": artist.seeking_description,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows)
    }


  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter(Artist.id == artist_id).first()

  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.website_link.data = artist.website_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.description 

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist_form = ArtistForm(request.form)
  artist = Artist.query.filter(Artist.id == artist_id).first()

  if(artist_form.validate()):
    artist.name = artist_form.name.data
    artist.city = artist_form.city.data
    artist.state = artist_form.state.data
    artist.phone = artist_form.phone.data
    artist.genres = artist_form.genres.data
    artist.facebook_link = artist_form.facebook_link.data
    artist.website_link = artist_form.website_link.data
    artist.seeking_venue = artist_form.seeking_venue.data
    artist.seeking_description = artist_form.seeking_description.data

    try:
      db.session.commit()
      flash(f' {artist.name} updated successfully')
    except:
      db.session.rollback()
      flash('An Error Occurred')
    finally:
      db.session.close()
    return redirect(url_for('show_artist', artist_id=artist.id))
  else:
    flash('Invalid data provided')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter(Venue.id == venue_id).first()
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.image_link.data = venue.image_link
  form.facebook_link.data = venue.facebook_link
  form.genres.data = venue.genres
  form.website_link.data = venue.website_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.filter(Venue.id == venue_id).first()
  venue_form = VenueForm(request.form)

  if(venue_form.validate()):
    venue.name = venue_form.name.data
    venue.city = venue_form.city.data
    venue.state = venue_form.state.data
    venue.address = venue_form.address.data
    venue.phone = venue_form.phone.data
    venue.image_link = venue_form.image_link.data
    venue.facebook_link = venue_form.facebook_link.data
    venue.genres = venue_form.genres.data
    venue.website_link = venue_form.website_link.data
    venue.seeking_talent = venue_form.seeking_talent.data
    venue.seeking_description = venue_form.seeking_description.dat

    try:
      db.session.commit()
      flash(f' {venue.name} updated successfully ')
    except:
      db.session.rollback()
      flash('An Error Occurred')
    finally:
      db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    flash("Invalid fields entered")
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    genres = request.form.get('genres')
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')
    website_link = request.form.get('website_link')
    seeking_venue = request.form.get('seeking_venue')
    seeking_description = request.form.get('seeking_description')
    
  # TODO: modify data to be the data object returned from db insertion

    artist_form = ArtistForm(request.form)

    if(artist_form.validate()):
      try:
        new_artist = Artist(
          name = name,
          city = city,
          state = state,
          address = address,
          phone = phone,
          genres = genres,
          facebook_link = facebook_link,
          image_link = image_link,
          website_link = website_link,
          seeking_venue = seeking_venue,
          seeking_description = seeking_description
        )
        db.session.add(new_artist)
        db.session.commit()
        flash('Artist ' + new_artist.name + ' was successfully listed!')
      except:
        db.session.rollback()
        flash('An error occurred. Artist ' + new_artist.name + ' could not be listed.')
      finally:
        db.session.close()
      return render_template('pages/home.html')
    else:
      flash('Invalid fields entered')
      return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  
  all_shows = []

  for show in Show.query.filter(Show.artist_id != None).filter(Show.venue_id != None).all():

    all_shows.append({
    "venue_id": show.venue_id,
    "venue_name": show.venue.name,
    "artist_id": show.artist_id,
    "artist_name": show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": show.start_time
  })

  return render_template('pages/shows.html', shows=all_shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  artist_id = request.form.get('artist_id')
  venue_id = request.form.get('venue_id')
  start_time = request.form.get('start_time')
  new_show = Show(
    artist_id = artist_id,
    venue_id = venue_id,
    start_time = start_time
  )

  show_form = ShowForm(request.form)

  if(show_form.validate):
    try:
      db.session.add(new_show)
      db.session.commit()
      flash('Show was successfully listed!')
    except:
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')
    finally:
      db.session.close()
    return render_template('pages/home.html')
  else:
    flash('Invalid fields entered')
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
