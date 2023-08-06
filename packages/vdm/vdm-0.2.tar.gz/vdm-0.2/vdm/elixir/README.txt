
## Issues -- 2007-12-23

(in rough order of priority)

### 1. Support for versioned many to many

### 2. Model traversal (for 'old' objects) works correctly

  * this is very closely related to versioned many to many
  * minor subissue: ensure one gets continuity object not a 'version'
    when you do changes
    * in terms of use case below what happens if we do:
      some_other_object.movie = m1r1
    * not a problem if you can only do changes using HEAD

### Support delete and undeleting (State)

Current versioning model despite being versioned does not allow deleting
and undeleting of objects.

### 4. Conflicts, merging and locking

Once we have versioning we have conflicts, merging and locking ...

### 5. Revisions should be 'hidden' -- i.e. created automatically

Decision: wontfix

Why:

  * problem with this is where do you set up the revision itself (e.g.
    log_message, author)
  * thus think it is inevitable that you create some kind of Revision
    object, however no need to have to call commit on revision (just use
    session.flush stuff)
  * simplest approach is simply to require the user to create a revision
    and attach it to session before calling flush (if absolutely require
    could provide a backup where this revision is auto created if
    nonexistent)
    * alternative is to override flush on extension to take an argument
      (or have a SessionExtension and override before_flush in some way)
      -- but don't like this much
    * TODO: without explicit call to commit how do we set timestamp on
      revision -- could just let it be as it was when revision was
      created or just override before_update on Revision

## Analysis and Use Cases

Here's the basis use case setup we will refer to below:

    class Movie(Entity):
        id = Field(Integer, primary_key=True)
        title = Field(String(60), primary_key=True)
        description = Field(String(512))
        ignoreme = Field(Integer, default=0)
        director = ManyToOne('Director', inverse='movies')
        actors = ManyToMany('Genre', inverse='movies',
          tablename='movie_2_genre')
        using_options(tablename='movies')
        acts_as_versioned(ignore=['ignoreme'])

    class Director(Entity):
        name = Field(String(60))
        movies = OneToMany('Movie', inverse='director')
        using_options(tablename='directors')

    class Genre(Entity):
        name = Field(String(60))
        movies = ManyToMany('Movie', inverse='genres',
          tablename='movie_2_genre')
        using_options(tablename='actors')


### Versioned Many to Many

This is fairly trivial conceptually: just turn the intermediate object
in a many to many into a versioned object in its own right but also
adding a state attribute.

I.e. we implement ManyToMany explicitly using:

    class Movie2Genre
        movie = ManyToOne('Movie')
        actor = ManyToOne('Actor')
        state = Field(Integer)
        acts_as_versioned()

and the association_proxy provided by sqlalchemy.

However to get this to work 'nicely' with elixir involves:

  * setting up a new m2m property which is aware of state
  * proper model traversal (o/w we still have the problem that we only
    ever get the HEAD value for movie.genres even when using an old
    version of movie).


### Model Traversal

    # revision 1
    m1 = Movie(id=1)
    d1 = Director(id=1, name='Blogs')
    m1.director = d1
    flush()
    ts1 = datetime.now()

    # revision 2
    m1 = Movie.get(1)
    d1 = Director.get(2)
    d1.name = 'Jones'
    g1 = Genre(...)
    d2 = Director(...)
    m1.genres.append(g1)
    m1.director = d2
    flush()
    ts2 = datetime.now()
    # basic domain model traversal (requires remembering revision/timestamp)
    # in elixir
    # assert m1r1.director.name == 'Jones'
    assert m1r1.director.name == 'Blogs'


    m1 = Movie.get(1)
    m1r1 = m1.get_as_of(ts1) 
    assert len(m1r1.genres) == 0
    # in elixir this results in an error as m1r1 does not have attribute genres
    # (or any m2m versioning support)
    # with broken traversal but m2m attribute we get
    # assert len(m1r1.genres) == 1
    # note that traversal would include proper m2m versioning

#### The Issue

How do we pass around information about what the current reference
timestamp/revision this is because doing many to many involves
*traversing* the domain model i.e. we have moved from the Movie object
to the implicit Movie2Genre object and then on to the Genre object. 

The key question in resolving this is deciding what we get back when we
do:

    m1r1 = m1.get_as_of(ts1)

Solution 1

At present the elixir approach is that this returns a MovieVersion
object appropriate at ts1. The problem with this is that:

1. This does not behave like the continuity object (i.e. Movie) in
important respects most notably in terms of 'special' properties such as
m2m lists (and any other properties you've specially added).

2. Even if it did it would be unclear what the m2m links would work with
(i.e.  point to)? Should they point to GenreVersion or to Genre (more
explicitly should we have MovieVersion2GenreVersion objects or
MovieVersion2Genre objects or ...)

To put this formally what happens when one does:

    # does this return d1r1 or just d1 in elixir this returns d1
    thedirector = m1r1.director
    # again do we get g1 or g1r1 and what list do we get (as it was at
    # r1 or now)
    thegenres = m1r1.genres
    # and this really gets difficult if genres were to have some foreign
    # key or even another m2m
    mylist = m1r1.genres.some_other_m2m

Solution 2

m1r1 is m1 (i.e. the continuity object) but with some information
telling it to return information on attribute calls as if it was at ts1.
[This was approach taken with sqlobject code].

However this is problematic because it means overriding all property
read accesses to ensure (if necessary) the call is passed down to the
relevant history object.

To be continued ...
