from flask import Flask, render_template, request,redirect, url_for
#required for implementing login and logout.
from flask import session, request, abort
import sqlite3, os
from datetime import date


app = Flask(__name__)
app = Flask(__name__, template_folder= "templates")
app = Flask(__name__, static_folder= "static")

UPLOAD_FOLDER = '/static/images'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# required for login and logout
app.config.update(
    SECRET_KEY='MySecretKey',
    ADMINUSERNAME='admin',
    ADMINPASSWORD='default'
    )

##################################
#  implementation for login / logout / home page
def get_pk(name):
   try:
      print ("making a connection")
      connection = sqlite3.connect('artgallery.db')

      print ("Getting a Cursor")
      cursor = connection.cursor()
      
      print ("Executing the DML")
      cursor.execute("select id from artist where name=(?)", (name,))

      print ("Get the Rows from cursor")
      pk = cursor.fetchall() 
      print(pk[0][0])
      pk=pk[0][0]

      print ("Closing the datbase")
      connection.close()

      return pk
   except Exception as error:
      return_message = str(error)
      return(return_message)


def login_helper(name, password):
   try:
      print ("making a connection")
      connection = sqlite3.connect('artgallery.db')

      print ("Getting a Cursor")
      cursor = connection.cursor()
      
      print ("Executing the DML")
      cursor.execute("select password from artist where name=(?)", (name,))

      print ("Get the Rows from cursor")
      correctPassword = cursor.fetchall() 
      print(correctPassword[0][0])

      print ("Closing the datbase")
      connection.close()

      if password==correctPassword[0][0]:
         return True
      else:
         return False
   except Exception as error:
      print(error)
      return False

@app.route('/', methods=['GET', 'POST'])
def index():
   error= None
   return render_template('index.html', error=error)

@app.route('/artist/<int:pk>', methods=['GET', 'POST'])
def index_user(pk):
   # error= None
   return render_template('index.html', pk=pk)

@app.route('/login', methods=['GET', 'POST'])
def login():
   error = None
   if request.method == 'POST':
      username=request.form['username']
      password=request.form['password']

      if username==app.config['ADMINUSERNAME'] and password== app.config['ADMINPASSWORD']:
         session['admin_logged_in'] = True
         return redirect(url_for('index'))
      elif login_helper(username, password):
         session['artist_logged_in'] = True
         pk=get_pk(username)
         return redirect(url_for('index_user',pk=pk))
      else:
         error='Invalid username/password. Try again!'
   return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    session.pop('artist_logged_in', None)
    error = None
    return render_template('index.html', error=error)


########################ARTISTS#########################

@app.route("/createArtistTable", methods=['POST'])
def createArtistTable():
  
   print ("making a connection")
   connection = sqlite3.connect('artgallery.db')

   print ("Getting a Cursor")
   cursor = connection.cursor()
   
   print ("Executing the DML")
   cursor.execute('''CREATE TABLE IF NOT EXISTS artist
            (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, password TEXT NOT NULL, email VARCHAR, about TEXT, date_created DATE, Profile TEXT, appr INTEGER,date_modified DATE )''') 
   print ("Commiting the changes")
   connection.commit()

   print ("Closing the datbase")
   connection.close()

   return ("Table Created Succssffully")

@app.route("/artist_create", methods=['GET','POST'])
def artist_create():

   if request.method == 'POST':
      name = request.form['name']
      password = request.form['password']
      email = request.form['email']
      about = request.form['about']
      #createdate = request.form['createdate']
      image = request.files['File']  
      createdate=date.today()
      modifiedDate=date.today()
      appr = 0

      try:
         # file url is used for storing images at an absolute location on the os file folder.
         file_url = os.path.join(os.getcwd()+ UPLOAD_FOLDER, image.filename)

         # static url is required for serving images from a static folder. store this on SQL DB
         staic_url = os.path.join(UPLOAD_FOLDER, image.filename)

         image.save(file_url)

         print(staic_url)

         print ("making a connection")
         connection = sqlite3.connect('artgallery.db')

         print ("Getting a Cursor")
         cursor = connection.cursor()
         
         print ("Executing the DML")
         cursor.execute("INSERT into artist (name, password, email, about, date_created, Profile, appr,date_modified) values (?,?,?,?,?,?,?,?)",(name,password,email,about,createdate,staic_url,appr,modifiedDate))  
         
         print ("Commiting the changes")
         connection.commit()

         print ("Closing the datbase")
         connection.close()

         session['artist_logged_in'] = True
         pk=get_pk(name)
         return redirect(url_for('index_user',pk=pk))
   
      except Exception as error:
         return_message = str(error)
         return(return_message)

   else:
      return render_template("profile_create.html")


@app.route("/profilelist", methods=['GET'])
def profilelist():
   print ("making a connection")
   connection = sqlite3.connect('artgallery.db')

   print ("Getting a Cursor")
   cursor = connection.cursor()
   
   print ("Executing the DML")
   cursor.execute("select * from artist")

   print ("Get the Rows from cursor")
   all_profiles = cursor.fetchall() 

   print ("Closing the datbase")
   connection.close()

   # print(all_profiles)
   pk=get_pk
   return render_template("profile_list.html", profile = all_profiles)




@app.route("/profileupdate/<int:id>", methods=['GET','POST'])
def profileupdate(id):
   modifiedDate = date.today()
   if request.method == 'POST':
      name = request.form['name']
      password = request.form['password']
      email = request.form['email']
      about = request.form['about']
      image = request.files['file']  
  
      if(len(image.filename)!=0):

         old_image = request.form['image_file']
         current_dir = os.getcwd()

         old_image_url = current_dir +old_image
         print(old_image_url)
         try:
            # file url is used for storing images at an absolute location on the os file folder.
            file_url = os.path.join(os.getcwd()+ UPLOAD_FOLDER, image.filename)

            # static url is required for serving images from a static folder. store this on SQL DB
            static_url = os.path.join(UPLOAD_FOLDER, image.filename)

            image.save(file_url)

            # Lets delete old image
            os.remove(old_image_url)

            print ("making a connection", id)
            connection = sqlite3.connect('artgallery.db')
         
            print ("Getting a Cursor")
            cursor = connection.cursor()
            
            print ("Executing the DML")
            cursor.execute("UPDATE artist SET name=?, password=?, email=?, about=?, Profile=?, date_modified=? WHERE id=?",(name,password,email,about,static_url,modifiedDate,id))  
            
            print ("Commiting the changes")
            connection.commit()
            pk=get_pk(name)
            return redirect(url_for('profileview',id=pk))
      
         except Exception as error:
            return_message = str(error)
            return(return_message)
      else:
         print ("making a connection", id)
         connection = sqlite3.connect('artgallery.db')
         
         print ("Getting a Cursor")
         cursor = connection.cursor()
            
         print ("Executing the DML")
         cursor.execute("UPDATE artist SET name=?, password=?, email=?, about=?, date_modified=? WHERE id=?",(name,password,email,about,modifiedDate,id))  
            
         print ("Committing the changes")
         connection.commit()
         pk=get_pk(name)
         return redirect(url_for('profileview',id=pk))

   else:
      
      print ("Making a connection")
      connection = sqlite3.connect('artgallery.db')
   
      print ("Getting a Cursor")
      cursor = connection.cursor()
      
      print ("Executing the DML")
      cursor.execute("select * from artist where id=(?)", (id,))

      print ("Get the Rows from cursor")
      show_data = cursor.fetchall()
      
      print ("Closing the database")
      connection.close()

      return render_template("profile_update.html", show_data = show_data, pk=id)


@app.route("/profiledelete/<int:id>", methods=['GET','POST'])
def profiledelete(id):
      
   try:

      print ("making a connection")
      connection = sqlite3.connect('artgallery.db')

      print ("Getting a Cursor")
      cursor = connection.cursor()
      
      print ("Executing the DML")
      cursor.execute("DELETE from artist where id=(?)", (id,))
      
      print ("Committing the changes")
      connection.commit()

      print ("Closing the database")
      connection.close()

      session.pop('artist_logged_in', None)
      return redirect(url_for('index'))
   
   
   except Exception as error:
      return_message = str(error)
      return(return_message)


@app.route("/sendlove/<int:id>",methods=['GET','POST'])
def sendlove(id):
   print ("making a connection")
   connection = sqlite3.connect('artgallery.db')

   print ("Getting a Cursor")
   cursor = connection.cursor()
      
   print ("Executing the DML")
   cursor.execute("UPDATE artist SET appr=appr+1 WHERE id=(?)",(id,))

   print ("Commiting the changes")
   connection.commit()

   print ("Closing the datbase")
   connection.close()

   print ("making a connection")
   connection = sqlite3.connect('artgallery.db')

   print ("Getting a Cursor")
   cursor = connection.cursor()

   print ("Executing the DML")
   cursor.execute("SELECT * from artist where id=(?)",(id,))

   print ("Get the Rows from cursor")
   data = cursor.fetchall() 

   print ("Closing the datbase")
   connection.close()

   return render_template("sendlove.html", item = data)


@app.route("/profileview/<int:id>", methods=['GET'])
def profileview(id):

   print("pk is", id)
   print ("making a connection for userprof")
   connection = sqlite3.connect('artgallery.db')

   print ("Getting a Cursor")
   cursor = connection.cursor()
   
   print ("Executing the DML")
   cursor.execute("select * from artist where id=(?)", (id,))

   print ("Get the Rows from cursor")
   all_rows = cursor.fetchall() 

   print ("Closing the datbase")
   connection.close()

   return render_template("profile_view.html", user = all_rows, pk=id)

###########################ARTWORK###########################
@app.route('/createArtworkTable',methods=['POST'])
def createArtworkTable():
   print("Making a connection")
   connection = sqlite3.connect('artgallery.db')

   print ("Getting a cursor")
   cursor = connection.cursor()
   
   print ("Executing the DML")
   cursor.execute('''CREATE TABLE IF NOT EXISTS Art 
                  (pk INTEGER PRIMARY KEY, Title TEXT, 
                  Artist TEXT FOREIGN KEY REFERENCES artist(name), Genre TEXT, Year INT, Photo TEXT, Appr INTEGER)''')

   print("Committing the changes")
   connection.commit()
   
   print("Closing the database")
   connection.close()
   
   return('Art table created successfully')

@app.route('/artworkcreate', methods = ['GET','POST'])
def artworkcreate():
   if request.method == 'POST':
      title = request.form['title']
      artist = request.form['artist']
      # genre = request.form['genre']
      genre = "arty"
      year = request.form['year']
      image = request.files['file']  
      appr = 0

      try:
         # file url is used for storing images at an absolute location on the os file folder.
         file_url = os.path.join(os.getcwd() + UPLOAD_FOLDER, image.filename)
         print(file_url)
         
         # static url is required for serving images from a static folder. store this on SQL DB
         staic_url = os.path.join(UPLOAD_FOLDER, image.filename)
         print(staic_url)
         
         image.save(file_url)

         print ("Making a connection")
         connection = sqlite3.connect('artgallery.db')

         print ("Getting a Cursor")
         cursor = connection.cursor()
         
         print ("Executing the DML")
         cursor.execute("INSERT into Art (Title, Artist, Genre, Year, Photo, Appr) values (?,?,?,?,?,?)",
                        (title,artist,genre,year,staic_url,appr))  
         
         print ("Committing the changes")
         connection.commit()

         print ("Closing the database")
         connection.close()

         return redirect(url_for('artlist'))
   
      except Exception as error:
         return_message = str(error)
         return(return_message)

   else:
      return render_template("artwork_create.html")

@app.route('/artlist', methods=['GET']) 
def artlist():
   print("Making a connection")
   connection = sqlite3.connect('artgallery.db')

   print ("Getting a cursor")
   cursor = connection.cursor()
   
   print ("Executing the DML")
   cursor.execute("select * from Art")

   print("Get the Rows from cursor")
   rows = cursor.fetchall()
   
   print("Closing the database")
   connection.close()

   print(rows)
   return render_template("art_list.html", art = rows)



@app.route('/createGenreTable',methods=['POST'])
def createGenreTable():
   print("Making a connection")
   connection = sqlite3.connect('artgallery.db')

   print ("Getting a cursor")
   cursor = connection.cursor()
   
   print ("Executing the DML")
   cursor.execute('''CREATE TABLE IF NOT EXISTS Genre
                  (id INTEGER PRIMARY KEY, Name TEXT, 
                  About TEXT, Date_modified DATE)''')
   
   print("Committing the changes")
   connection.commit()
   
   print("Closing the database")
   connection.close()
   
   return('Genre Table created successfully')

if __name__ == '__main__':
   app.run()
   app.debug = True
