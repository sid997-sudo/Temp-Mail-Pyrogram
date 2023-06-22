import mysql.connector
import datetime
import config
from zoneinfo import ZoneInfo


# Adding user to the database
def add_user(chat_id, name, username):
    time = datetime.datetime.now(tz=ZoneInfo("Asia/Tehran"))
    sql = "INSERT IGNORE INTO users (ID,Name,Username,Created) VALUES (%s,%s,%s,%s)"
    val = (chat_id, name, username, time)
    mycursor.execute(sql, val)
    mydb.commit()


# adding email for user to the database
def add_email(email, userid):
    sql = 'UPDATE users SET Email=%s WHERE ID=%s'
    val = (email, userid)
    mycursor.execute(sql, val)
    mydb.commit()
    return


# reading user email from data base
def read_email(userid):
    sql = 'SELECT Email FROM users WHERE ID="%s"'
    val = (userid,)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()
    return result


# counting users
def all_users():
    sql = 'SELECT COUNT(ID) FROM users'
    mycursor.execute(sql)
    result = mycursor.fetchone()[0]
    return result


# connecting to database
mydb = mysql.connector.connect(
    host=config.host,
    user=config.user,
    password=config.password,
    database=config.database
)
mycursor = mydb.cursor()
