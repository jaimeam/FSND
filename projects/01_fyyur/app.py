#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
  Flask,
  render_template,
  request,
  Response,
  flash,
  redirect,
  url_for,
  jsonify
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
import datetime
from sqlalchemy.sql import func

#Import models and SQLAlchemy connection
from models import (
  Venue,
  Artist,
  Show,
  app,
  db
)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  data = []
  locations = db.session.query(Venue.city,Venue.state).distinct().all()
  for location in locations:
    location_entry = {}
    location_entry['city'] = location[0]
    location_entry['state'] = location[1]
    location_entry['venues'] = []
    location_venues = Venue.query.filter(Venue.city==location[0],Venue.state==location[1]).all()
    for venue in location_venues:
      new_venue = {}
      new_venue['id'] = venue.id
      new_venue['name'] = venue.name
      new_venue['num_upcoming_shows'] = Show.query.filter(Show.venue_id==venue.id,Show.start_time<datetime.datetime.today()).count()
      location_entry['venues'].append(new_venue)
    data.append(location_entry)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term=request.form.get('search_term')
  venue_matches_query = Venue.query.filter(func.lower(Venue.name).contains(search_term.lower())).all()
  
  response = {}
  response['count'] = len(venue_matches_query)
  response['data'] = []

  for venue_query in venue_matches_query:
    venue_dict = {}
    venue_dict['id'] = venue_query.id
    venue_dict['name'] = venue_query.name
    venue_dict['num_upcoming_shows'] = len(Show.query.filter(Show.venue_id==venue_dict['id'], Show.start_time>=datetime.datetime.today()).all())
    response['data'].append(venue_dict)

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id

  data = {}
  venue_query = Venue.query.get(venue_id)
  data['id']=venue_query.id
  data['name']=venue_query.name
  data['genres']=venue_query.genres[1:-1].split(',')
  data['address']=venue_query.address
  data['city']=venue_query.city
  data['state']=venue_query.state
  data['phone']=venue_query.phone
  data['website']=venue_query.website
  data['facebook_link']=venue_query.facebook_link
  data['seeking_talent']=venue_query.seeking_talent
  data['seeking_description']=venue_query.seeking_description
  data['image_link']=venue_query.image_link
  data['past_shows']=[]
  past_shows_query = Show.query.filter(Show.venue_id==venue_id, Show.start_time<datetime.datetime.today()).all()
  for past_show_query in past_shows_query:
    past_show = {}
    past_show['artist_id'] = past_show_query.artist_id
    past_show['artist_name'] = Artist.query.get(past_show['artist_id']).name
    past_show['artist_image_link'] = Artist.query.get(past_show['artist_id']).image_link
    past_show['start_time'] = str(past_show_query.start_time)
    data['past_shows'].append(past_show)
  data['upcoming_shows']=[]
  upcoming_shows_query = Show.query.filter(Show.venue_id==venue_id, Show.start_time>=datetime.datetime.today()).all()
  for upcoming_show_query in upcoming_shows_query:
    upcoming_show = {}
    upcoming_show['artist_id'] = upcoming_show_query.artist_id
    upcoming_show['artist_name'] = Artist.query.get(upcoming_show['artist_id']).name
    upcoming_show['artist_image_link'] = Artist.query.get(upcoming_show['artist_id']).image_link
    upcoming_show['start_time'] = str(upcoming_show_query.start_time)
    data['upcoming_shows'].append(upcoming_show)
  data['past_shows_count']=len(data['past_shows'])
  data['upcoming_shows_count']=len(data['upcoming_shows'])
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  form = VenueForm()
  try:
    new_venue = Venue(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      image_link = form.image_link.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
      website = form.website.data,
      seeking_talent = form.seeking_talent.data,
      seeking_description = form.seeking_description.data
    )
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        flash('The venue has been removed!')
    except:
        error = True
        print('rollback delete')
        db.session.rollback()
        flash('It was not possible to delete this Venue')
    finally:
        db.session.close()
    return jsonify({ 'success': True })

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  data = []
  artists_query = Artist.query.all()
  for artist in artists_query:
    artist_dict={}
    artist_dict['id']=artist.id
    artist_dict['name']=artist.name
    data.append(artist)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    error = False
    try:
        Artist.query.filter_by(id=artist_id).delete()
        db.session.commit()
        flash('The artist has been removed!')
    except:
        error = True
        print('rollback delete')
        db.session.rollback()
        flash('It was not possible to delete this Venue')
    finally:
        db.session.close()
    return jsonify({ 'success': True })

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term=request.form.get('search_term')
  artist_matches_query = Artist.query.filter(func.lower(Artist.name).contains(search_term.lower())).all()
  
  response = {}
  response['count'] = len(artist_matches_query)
  response['data'] = []

  for artist_query in artist_matches_query:
    artist_dict = {}
    artist_dict['id'] = artist_query.id
    artist_dict['name'] = artist_query.name
    artist_dict['num_upcoming_shows'] = len(Show.query.filter(Show.artist_id==artist_dict['id'], Show.start_time>=datetime.datetime.today()).all())
    response['data'].append(artist_dict)
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  data = {}
  artist_query = Artist.query.get(artist_id)
  data['id']=artist_query.id
  data['name']=artist_query.name
  data['genres']=artist_query.genres[1:-1].split(',')
  data['city']=artist_query.city
  data['state']=artist_query.state
  data['phone']=artist_query.phone
  data['website']=artist_query.website
  data['facebook_link']=artist_query.facebook_link
  data['seeking_venue']=artist_query.seeking_venue
  data['seeking_description']=artist_query.seeking_description
  data['image_link']=artist_query.image_link
  data['past_shows']=[]
  past_shows_query = Show.query.filter(Show.artist_id==artist_id, Show.start_time<datetime.datetime.today()).all()
  for past_show_query in past_shows_query:
    past_show = {}
    past_show['venue_id'] = past_show_query.venue_id
    past_show['venue_name'] = Venue.query.get(past_show['venue_id']).name
    past_show['venue_image_link'] = Venue.query.get(past_show['venue_id']).image_link
    past_show['start_time'] = str(past_show_query.start_time)
    data['past_shows'].append(past_show)
  data['upcoming_shows']=[]
  upcoming_shows_query = Show.query.filter(Show.artist_id==artist_id, Show.start_time>=datetime.datetime.today()).all()
  for upcoming_show_query in upcoming_shows_query:
    upcoming_show = {}
    upcoming_show['venue_id'] = upcoming_show_query.venue_id
    upcoming_show['venue_name'] = Venue.query.get(upcoming_show['venue_id']).name
    upcoming_show['venue_image_link'] = Venue.query.get(upcoming_show['venue_id']).image_link
    upcoming_show['start_time'] = str(upcoming_show_query.start_time)
    data['upcoming_shows'].append(upcoming_show)
  data['past_shows_count']=len(data['past_shows'])
  data['upcoming_shows_count']=len(data['upcoming_shows'])



  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={}
  artist_query = Artist.query.get(artist_id)
  artist['id'] = artist_query.id
  artist['name'] = artist_query.name
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  form = ArtistForm()
  try:
    new_artist = {
      'name' : form.name.data,
      'city' : form.city.data,
      'state' : form.state.data,
      'phone' : form.phone.data,
      'image_link' : form.image_link.data,
      'genres' : form.genres.data,
      'facebook_link' : form.facebook_link.data,
      'website' : form.website.data,
      'seeking_venue' : form.seeking_venue.data,
      'seeking_description' : form.seeking_description.data
    }
    db.session.query(Artist).filter(Artist.id == artist_id).update(new_artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={}
  venue_query = Venue.query.get(venue_id)
  venue['id'] = venue_query.id
  venue['name'] = venue_query.name
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  form = VenueForm()
  try:
    new_venue = {
      'name' : form.name.data,
      'city' : form.city.data,
      'state' : form.state.data,
      'address': form.address.data,
      'phone' : form.phone.data,
      'image_link' : form.image_link.data,
      'genres' : form.genres.data,
      'facebook_link' : form.facebook_link.data,
      'website' : form.website.data,
      'seeking_talent' : form.seeking_talent.data,
      'seeking_description' : form.seeking_description.data
    }
    db.session.query(Venue).filter(Venue.id == venue_id).update(new_venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  form = ArtistForm()
  try:
    new_artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      image_link = form.image_link.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
      website = form.website.data,
      seeking_venue = form.seeking_venue.data,
      seeking_description = form.seeking_description.data
    )
    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows

  data = []
  shows_query = Show.query.all()
  for show_query in shows_query:
    show = {}
    show['venue_id'] = show_query.venue_id
    show['venue_name'] = Venue.query.get(show['venue_id']).name
    show['artist_id'] = show_query.artist_id
    show['artist_name'] = Artist.query.get(show['artist_id']).name
    show['artist_image_link'] = Artist.query.get(show['artist_id']).image_link
    show['start_time'] = str(show_query.start_time)
    data.append(show)
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  form = ShowForm()
  try:
    new_show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data,
    )
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()
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