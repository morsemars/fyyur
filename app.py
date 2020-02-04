#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# DONE - TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# DONE - TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Shows(db.Model):
  __tablename__ = 'Shows'
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
  start_time = db.Column(db.DateTime, primary_key=True)
  artist = db.relationship("Artist", backref="venues")
  venue = db.relationship("Venue", backref="artists")

  def __repr__(self):
        return f'<Shows {self.venue.name} {self.artist.name} {self.start_time}>'

class Venue(db.Model):
  __tablename__ = 'Venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable = False)
  city = db.Column(db.String(120),  nullable = False)
  state = db.Column(db.String(120),  nullable = False)
  address = db.Column(db.String(120),  nullable = False)
  phone = db.Column(db.String(120),  nullable = False)
  image_link = db.Column(db.String(500),  nullable = True)
  facebook_link = db.Column(db.String(120),  nullable = True)
  # DONE - TODO: implement any missing fields, as a database migration using Flask-Migrate
  genres = db.Column(db.ARRAY(db.String),  nullable = False)
  website = db.Column(db.String(120),  nullable = True)
  seeking_talent = db.Column(db.String, nullable = False)
  seeking_description = db.Column(db.String, nullable = True)
  shows = db.relationship("Shows", backref="Venues", cascade="all, delete-orphan")

  def __repr__(self):
        return f'<Venue {self.name}>'

class Artist(db.Model):
  __tablename__ = 'Artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String,  nullable = False)
  city = db.Column(db.String(120),  nullable = False)
  state = db.Column(db.String(120),  nullable = False)
  phone = db.Column(db.String(120),  nullable = False)
  genres = db.Column(db.ARRAY(db.String), nullable = False)
  image_link = db.Column(db.String(500),  nullable = True)
  facebook_link = db.Column(db.String(120),  nullable = True)
  # DONE - TODO: implement any missing fields, as a database migration using Flask-Migrate
  website = db.Column(db.String(120),  nullable = True)
  seeking_venue = db.Column(db.String, nullable = False)
  seeking_description = db.Column(db.String, nullable = True)
  shows = db.relationship("Shows", backref="Artists", cascade="all, delete-orphan")

  def __repr__(self):
        return f'<Artist {self.name}>'

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
# Helpers
#----------------------------------------------------------------------------#

def identify_shows(venue_artist, is_venue):
  def filter_past_shows(show):
    now = datetime.now()
    return show.start_time < now

  def filter_upcoming_shows(show):
    now = datetime.now()
    return show.start_time > now

  past_shows = list(filter(filter_past_shows, venue_artist.shows))
  upcoming_shows = list(filter(filter_upcoming_shows, venue_artist.shows))

  if(is_venue):
    return {
    "past_shows": [get_artist_show_summary(show) for show in past_shows],
    "upcoming_shows": [get_artist_show_summary(show) for show in upcoming_shows],
    "past_shows_count":len(past_shows),
    "upcoming_shows_count":len(upcoming_shows)
  }
  else:
    return {
    "past_shows": [get_venue_show_summary(show) for show in past_shows],
    "upcoming_shows": [get_venue_show_summary(show) for show in upcoming_shows],
    "past_shows_count":len(past_shows),
    "upcoming_shows_count":len(upcoming_shows)
  }

def get_venue_show_summary(show):
  return {
    "venue_id": show.venue.id,
    "venue_name": show.venue.name,
    "venue_image_link": show.venue.image_link,
    "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
  }

def get_artist_show_summary(show):
  return {
    "artist_id": show.artist.id,
    "artist_name": show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
  } 

def get_venue_summary(venue):
  return {
    "id": venue.id,
    "name": venue.name,
    "num_upcoming_shows": len(identify_shows(venue, True)["upcoming_shows"])
  }

def get_artist_summary(artist):
  return {
    "id": artist.id,
    "name": artist.name,
    "num_upcoming_shows": len(identify_shows(artist, False)["upcoming_shows"])
  }




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
  # DONE - TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  city_states = Venue.query.distinct('city','state')

  data = []
  for city_state in city_states:
    venues = Venue.query.filter_by(city=city_state.city,state=city_state.state).all()
    data.append({
    'city': city_state.city,
    'state': city_state.state,
    'venues': [get_venue_summary(venue) for venue in venues]
  })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE - TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form["search_term"]
  result = Venue.query.filter(Venue.name.ilike('%'+ search_term +'%')).all()

  response={
    "count": len(result),
    "data": [get_venue_summary(venue) for venue in result]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE- TODO: replace with real venue data from the venues table, using venue_id
  
  venue = Venue.query.filter_by(id=venue_id).first()
  shows = identify_shows(venue, True)
  venue.upcoming_shows = shows["upcoming_shows"]
  venue.past_shows = shows["past_shows"]
  venue.upcoming_shows_count = shows["upcoming_shows_count"]
  venue.past_shows_count = shows["past_shows_count"]
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # DONE - TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  form = VenueForm()
  if(form.validate()):
    # on successful db insert, flash success
    try:
      newVenue = Venue(
          name = form.name.data,
          city = form.city.data,
          state = form.state.data,
          address = form.address.data,
          phone = form.phone.data,
          image_link = form.image_link.data,
          facebook_link = form.facebook_link.data,
          genres = form.genres.data,
          website = form.website.data,
          seeking_talent = form.seeking_talent.data,
          seeking_description = form.seeking_description.data
        )
      db.session.add(newVenue)
      db.session.commit()
      flash('Venue ' + newVenue.name + ' was successfully listed!')
      # DONE - TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except:
      print(sys.exc_info())
      db.session.rollback()
      
      flash('An error occurred. Venue ' + newVenue.name + ' could not be listed.')
    finally:
      db.session.close()
      return render_template('pages/home.html')
  else:
    return render_template('forms/new_venue.html', form=form)
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TO TEST - TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  venue = Venue.query.filter_by(id=venue_id).first()
  
  try:
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully deleted!')
  except:
    print(sys.exc_info())
    db.session.rollback()
    flash('An error occurred. Venue ' + venue.name + ' could not be deleted.')
  finally:
    db.session.close()
    #return render_template('pages/home.html')
    #return redirect(url_for('index'))
    return jsonify({'success' : True})

  # DONE TODO BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # DONE TODO: replace with real data returned from querying the database
  artists =  Artist.query.all()
  data = [get_artist_summary(artist) for artist in artists]

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form["search_term"]
  artists = Artist.query.filter(Artist.name.ilike('%'+ search_term +'%')).all()

  response = {
    "count": len(artists),
    "data": [get_artist_summary(artist) for artist in artists]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # DONE TODO: replace with real venue data from the venues table, using venue_id

  artist = Artist.query.filter_by(id=artist_id).first()
  shows = identify_shows(artist, False)
  artist.upcoming_shows = shows["upcoming_shows"]
  artist.past_shows = shows["past_shows"]
  artist.upcoming_shows_count = shows["upcoming_shows_count"]
  artist.past_shows_count = shows["past_shows_count"]
  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # DONE TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
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
  # DONE TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  form = ArtistForm()

  if(form.validate()):
    try:
      newArtist = Artist(
          name = form.name.data,
          city = form.city.data,
          state = form.state.data,
          phone = form.phone.data,
          image_link = form.image_link.data,
          facebook_link = form.facebook_link.data,
          genres = form.genres.data,
          website = form.website.data,
          seeking_venue = form.seeking_venue.data,
          seeking_description = form.seeking_description.data
        )
      db.session.add(newArtist)
      db.session.commit()
      flash('Artist ' + newArtist.name + ' was successfully listed!')
    except:
      print(sys.exc_info())
      db.session.rollback()
      flash('An error occurred. Artist ' + newArtist.name + ' could not be listed.')
    finally:
      db.session.close()
      return render_template('pages/home.html')

  else:
    return render_template('forms/new_artist.html', form=form)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE TODO: replace with real venues data.
  shows = Shows.query.all()
  data = []
  for show in shows:
    data.append({
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # DONE TODO: insert form data as a new Show record in the db, instead

  form = ShowForm()

  if(form.validate()):
    try:
      newShow = Shows(
          artist_id = form.artist_id.data,
          venue_id = form.venue_id.data,
          start_time = form.start_time.data
        )
      db.session.add(newShow)
      db.session.commit()
      # on successful db insert, flash success
      flash('Show was successfully listed!')
      # DONE TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Show could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      return render_template('pages/home.html')
    except:
      print(sys.exc_info())
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')
    finally:
      db.session.close()
      return render_template('pages/home.html')
  else:
    return render_template('forms/new_show.html', form=form)

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
