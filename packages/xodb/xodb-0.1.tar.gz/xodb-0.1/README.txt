
xodb is yet another object database for Python for use with the Xapian
Search Engine Library (http://xapian.org).

xodb transforms a python object in your application into a Xapian
'Document' object using a transformation description object called a
'Schema'.  A schema can be defines as a separate class::

  import xodb

  class Person(object):

      def __init__(self, name, biography):
          self.name = name
          self.biography = biography

  class PersonSchema(xodb.Schema):

      name = xodb.String
      biography = xodb.Text(prefix="bio")

  if __name__ == '__main__':
      d = Person("dan", "Likes to eat pickles")
      a = Person("alice", "Collects funny pickle hats")

      # create a database and tell it how to index people
      db = xodb.temp()
      db.map(Person, PersonSchema)
      
      # add some objects
      db.add(d, a)

      # now you can search
      print db.query("name:dan").next().name
      print db.query("bio:collect").next().name
      print [p.name for p in db.query("bio:pickle")]


