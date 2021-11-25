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
         cursor.execute("UPDATE artist SET name=?, password=?, email=?, about=?,date_modified=? WHERE id=?",(name,password,email,about,modifiedDate,id))  
            
         print ("Commiting the changes")
         connection.commit()
         pk=get_pk(name)
         return redirect(url_for('profileview',id=pk))

   else:
      
      print ("making a connection")
      connection = sqlite3.connect('artgallery.db')
   
      print ("Getting a Cursor")
      cursor = connection.cursor()
      
      print ("Executing the DML")
      cursor.execute("select * from artist where id=(?)", (id,))

      print ("Get the Rows from cursor")
      show_data = cursor.fetchall()
      
      print ("Closing the datbase")
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
      
      print ("Commiting the changes")
      connection.commit()

      print ("Closing the datbase")
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
                  Artist TEXT, Genre TEXT, Year INT, Photo TEXT, Appr INTEGER)''')

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
      genre = request.form['genre']
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
      genrenameslist=genrenames()
      return render_template("artwork_create.html", genrenameslist=genrenameslist)

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

@app.route("/artworkupdate/<int:pk>", methods=['GET','POST'])
def artworkupdate(pk):
   
   if request.method == 'POST':
      title = request.form['title']
      artist = request.form['artist']
      genre = request.form['genre']
      year = request.form['year']
      image = request.files['file']

      if(len(image.filename)!=0): #if no image is selected (in case of updating artwork details)
         old_image = request.form['image_file']
         current_dir = os.getcwd()

         old_image_url = current_dir + old_image
         print(old_image_url)
         
         try:
            # file url is used for storing images at an absolute location on the os file folder.
            file_url = os.path.join(os.getcwd()+ UPLOAD_FOLDER, image.filename)

            # static url is required for serving images from a static folder. store this on SQL DB
            static_url = os.path.join(UPLOAD_FOLDER, image.filename)

            image.save(file_url)

            # Let's delete old image
            os.remove(old_image_url)

            print ("Making a connection", pk)
            connection = sqlite3.connect('artgallery.db')
         
            print ("Getting a Cursor")
            cursor = connection.cursor()
            
            print ("Executing the DML")
            cursor.execute("UPDATE Art SET Title=?, Artist=?, Genre=?, Year=?, Photo=? WHERE pk=?",(title,artist,genre,year,static_url,pk))  
            
            print ("Committing the changes")
            connection.commit()
            return redirect(url_for('artlist'))
   
         except Exception as error:
            return_message = str(error)
            return(return_message)
   
      else:
         
         print ("Making a connection",pk)
         connection = sqlite3.connect('artgallery.db')
      
         print ("Getting a Cursor")
         cursor = connection.cursor()
         
         print ("Executing the DML")
         cursor.execute("UPDATE Art SET Title=?, Artist=?, Genre=?, Year=? WHERE pk=?",(title,artist,genre,year,pk))
        
         print ("Committing the changes")
         connection.commit()
         
         return redirect(url_for('artlist'))
         
   else: #executes first and shows existing data in the form fields
         
      print ("Making a connection")
      connection = sqlite3.connect('artgallery.db')
   
      print ("Getting a Cursor")
      cursor = connection.cursor()
      
      print ("Executing the DML")
      cursor.execute("select * from Art where pk=(?)",(pk,))
      
      print ("Get the Rows from cursor")
      art_data = cursor.fetchall()
      genrenameslist = genrenames()
      
      print(art_data, genrenameslist)

      print ("Closing the database")
      connection.close()
      
      return render_template("artwork_update.html", art_data=art_data, genrenameslist=genrenameslist)

@app.route("/artworkdelete/<int:pk>", methods=['GET','POST'])
def artworkdelete(pk):
      
   try:

      print ("Making a connection")
      connection = sqlite3.connect('artgallery.db')

      print ("Getting a Cursor")
      cursor = connection.cursor()
      
      print ("Executing the DML")
      cursor.execute("DELETE from Art where pk=(?)", (pk,))
      
      print ("Committing the changes")
      connection.commit()

      print ("Closing the database")
      connection.close()
      
      return redirect(url_for('artlist'))
   
   
   except Exception as error:
      return_message = str(error)
      return(return_message)

@app.route("/like/<int:pk>",methods=['GET','POST'])
def like(pk):
   print ("Making a connection")
   connection = sqlite3.connect('artgallery.db')

   print ("Getting a Cursor")
   cursor = connection.cursor()
      
   print ("Executing the DML")
   cursor.execute("UPDATE Art SET Appr=Appr+1 WHERE pk=(?)",(pk,))

   print ("Committing the changes")
   connection.commit()

   print ("Closing the database")
   connection.close()

   print ("Making a connection")
   connection = sqlite3.connect('artgallery.db')

   print ("Getting a Cursor")
   cursor = connection.cursor()

   print ("Executing the DML")
   cursor.execute("SELECT * from Art where pk=(?)",(pk,))

   print ("Get the Rows from cursor")
   data = cursor.fetchall() 

   print ("Closing the database")
   connection.close()

   return render_template("like.html", item = data)


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

@app.route('/creategenre', methods = ['GET','POST'])
def creategenre():
   
   if request.method == 'POST':
      name = request.form['name']
      about = request.form['about']
      datemodified = date.today()

      try:
         print ("making a connection")
         connection = sqlite3.connect('artgallery.db')

         print ("Getting a Cursor")
         cursor = connection.cursor()
         
         print ("Executing the DML")
         # Entry of data into genre table
         cursor.execute("INSERT into Genre (Name, About, Date_modified) values (?,?,?)",
                        (name,about,datemodified))  
      
         print ("Commiting the changes")
         connection.commit()

         print ("Closing the database")
         connection.close()

         return redirect(url_for('genrelist'))
   
      except Exception as error:
         return_message = str(error)
         return(return_message)

   else:
      return render_template("create_genre.html")

@app.route('/genrelist', methods=['GET']) 
def genrelist():
   print("Making a connection")
   connection = sqlite3.connect('artgallery.db')

   print ("Getting a cursor")
   cursor = connection.cursor()
   
   print ("Executing the DML")
   cursor.execute("select * from Genre") #accessing all genre data (name,about,date modified)

   print("Get the Rows from cursor")
   g_rows = cursor.fetchall()
   
   print("Closing the database")
   connection.close()

   print(g_rows)
   return render_template("genre_list.html", g_rows = g_rows)

def genrenames():
   print("Making a connection")
   connection = sqlite3.connect('artgallery.db')

   print ("Getting a cursor")
   cursor = connection.cursor()
   
   print ("Executing the DML")
   cursor.execute("select Name from Genre order by Name") #accessing genre names

   # EITHER THIS
   # gname = []
   # print("Get the Rows from cursor")
   # for i in cursor.fetchall():
   #       for j in i:
   #              gname.append(j)

   # OR THAT
   gname = cursor.fetchall()
   
   print("Closing the database")
   connection.close()

   print(gname)
   return(gname)

@app.route("/genreupdate/<int:id>", methods=['GET','POST'])
def genreupdate(id):
   
   if request.method == 'POST':
      name = request.form['name']
      about = request.form['about']
      datemodified = date.today()
         
      try:
         print ("Making a connection", id)
         connection = sqlite3.connect('artgallery.db')
      
         print ("Getting a Cursor")
         cursor = connection.cursor()
         
         print ("Executing the DML")
         cursor.execute("UPDATE Genre SET Name=?, About=?, Date_modified=? WHERE id=?",(name,about,datemodified,id))  
         
         print ("Committing the changes")
         connection.commit()
         return redirect(url_for('genrelist'))

      except Exception as error:
         return_message = str(error)
         return(return_message)
 
   else:
         
      print ("Making a connection")
      connection = sqlite3.connect('artgallery.db')
   
      print ("Getting a Cursor")
      cursor = connection.cursor()
      
      print ("Executing the DML")
      cursor.execute("select * from Genre where id=(?)",(id,))

      print ("Get the Rows from cursor")
      show_data = cursor.fetchall()
      
      print ("Closing the database")
      connection.close()

      return render_template("genre_update.html", show_data = show_data)

@app.route("/genredelete/<int:id>", methods=['GET','POST'])
def genredelete(id):
      
   try:

      print ("Making a connection")
      connection = sqlite3.connect('artgallery.db')

      print ("Getting a Cursor")
      cursor = connection.cursor()
      
      print ("Executing the DML")
      cursor.execute("DELETE from Genre where id=(?)", (id,))
      
      print ("Committing the changes")
      connection.commit()

      print ("Closing the database")
      connection.close()
      
      return redirect(url_for('genrelist'))
   
   
   except Exception as error:
      return_message = str(error)
      return(return_message)


if __name__ == '__main__':
   app.run()
   app.debug = True