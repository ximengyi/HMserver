#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import sqlite3
app = Flask(__name__)
@app.route('/')
def hello_world():
    return render_template('index.html',title='欢迎使用HM作业快速收评系统')

#目前这一段代码没有使用（主页面中没有view的链接）
@app.route('/view',methods=['GET','POST'])
def view():
  conn = sqlite3.connect('test.db')
  c = conn.cursor()
  # b =conn.cursor()
  if request.method=='POST':
     grade=request.form['grade']
     stuclass=request.form['stuclass']
     subject=request.form['subject']
     sub_type =request.form['sub_type']

     print grade, stuclass, subject,sub_type,result
     # curclass=c.execute("SELECT STUNUM,NAME,CLASS,GRADE FROM STUDENT WHERE GRADE=:grade AND CLASS=:stuclass",{'grade':grade ,'stuclass':stuclass})
     # curcom =b.execute("SELECT * FROM STUDENT INNER JOIN COMSTU ON STUDENT.STUNUM=COMSTU.STUNUM AND COMNUM=:comnum AND SUBJECT=:subject AND CLASS=:stuclass AND GRADE=:grade",{'comnum':comnum,'grade':grade,'stuclass':stuclass,'subject':subject})
     # cursor= list(set(curclass).difference(set(curcom)))

     cursor= c.execute("select * FROM STUDENT WHERE STUNUM NOT IN (select STUNUM FROM COMSTU WHERE SUBJECT=:subject AND SUB_TYPE=:sub_type)",{'subject':subject,'sub_type':sub_type} )
     return render_template('view.html', entries=cursor)
  else:
     cursor = c.execute("SELECT STUNUM, NAME, CLASS,GRADE  from STUDENT")
     return render_template('view.html', entries=cursor)

@app.route('/statistics',methods=['GET','POST'])
def statistics():
  conn = sqlite3.connect('test.db')
  c = conn.cursor()
  b =conn.cursor()

  if request.method=='POST':
     grade=request.form['grade']
     stuclass=request.form['stuclass']
     subject=request.form['subject']
     sub_type =request.form['sub_type']
     result = request.form['result']
     comdate = request.form['comdate']
     str = " "
     str =  grade + stuclass + subject + sub_type + result + comdate

     sql = "select STUNUM,NAME,CLASS,GRADE,'已交',:comdate FROM STUDENT WHERE CLASS=:stuclass AND  (STUNUM "
     sql = sql+ " IN (select STUNUM FROM COMSTU WHERE SUBJECT=:subject "
     if result == "所有": # 20180312 add ，所有成绩，包括已交和未交的作业都要统计
        sql = sql+ "AND SUB_TYPE=:sub_type AND COMDATE=:comdate))"
        sql1 = "select STUNUM,NAME,CLASS,GRADE,'未交',:comdate FROM STUDENT WHERE CLASS=:stuclass AND  (STUNUM "
        sql1 = sql1+ "NOT IN (select STUNUM FROM COMSTU WHERE SUBJECT=:subject "
        sql1 = sql1+ "AND SUB_TYPE=:sub_type AND COMDATE=:comdate))"
        sql = sql + ' UNION ' + sql1
     else: # 当选择某个成绩的进行统计时，只需要统计已交的作业即可
        sql = sql + "AND SUB_TYPE=:sub_type AND RESULT=:result AND COMDATE=:comdate))"

     #sql1 = "select STUNUM,NAME,CLASS,GRADE,'未交',:comdate FROM STUDENT WHERE CLASS=:stuclass AND  (STUNUM "
     #sql1 = sql1+ "NOT IN (select STUNUM FROM COMSTU WHERE SUBJECT=:subject "
     #sql1 = sql1+ "AND SUB_TYPE=:sub_type AND COMDATE=:comdate))"
     #sql = sql + ' UNION ' + sql1
     sqlb = "select count(*) FROM STUDENT  WHERE CLASS=:stuclass AND GRADE=:grade "
     cursor= c.execute(sql,  {'stuclass':stuclass,'subject':subject,'sub_type':sub_type, 'result':result,'comdate':comdate} )
     worknum = len(cursor.fetchall())
     cursor= c.execute(sql,  {'stuclass':stuclass,'subject':subject,'sub_type':sub_type, 'result':result,'comdate':comdate} )
     cursor2 =b.execute(sqlb,{'stuclass':stuclass,'grade':grade})
     # print len(cursor.fetchall())
     #context={'subject':subject,'comdate':comdate}
     ####endif
     return render_template('statistics.html', entries=cursor, grade = grade, stuclass=stuclass ,stucount=cursor2.fetchone()[0],worknum=worknum)
  else:
     #cursor = c.execute("SELECT STUNUM, NAME, CLASS,GRADE  from STUDENT")
     #context={'subject':'','comdate':''}
     cursor=c.execute("select  comdate , sub_type from comstu as a1 where cid = (SELECT max(cid) from comstu)")
     rows = cursor.fetchall()
     comdate =rows[0][0]
     sub_type = rows[0][1]
     sql ="select student.stunum ,name,subject, class,grade,sub_type,comdate from STUDENT, COMSTU where STUDENT.STUNUM=COMSTU.STUNUM AND COMSTU.sub_type=:sub_type AND COMSTU.comdate=:comdate ORDER BY student.stunum  ASC "
     cursor= c.execute(sql,{'sub_type':sub_type,'comdate':comdate})



     #return render_template('statistics.html')
     return render_template('getstatistics.html', entries=cursor, **locals())

@app.route('/singlest',methods=['GET','POST'])
def singlest():
  conn = sqlite3.connect('test.db')
  c = conn.cursor()
  b = conn.cursor()
  d = conn.cursor()

  # b =conn.cursor()
  if request.method=='POST':
     #grade=request.form['grade']
     #stuclass=request.form['stuclass']
     stunum=request.form['stunum']
     subject=request.form['subject']
     sub_type =request.form['sub_type']
     begindate = request.form['begindate']
     enddate = request.form['enddate']

     #str = " "
     #str =  grade + stuclass + stunum + subject + sub_type + begindate + enddate
     # STUNUM,SUBJECT,SUB_TYPE,
     sql = "select RESULT,count(RESULT) from COMSTU "
     #if sub_type == "所有":
     #   sql = sql + "where COMDATE<=:enddate and COMDATE>=:begindate and STUNUM=:stunum  and SUBJECT=:subject "
     #   sql = sql + " group by SUBJECT,SUB_TYPE,RESULT "
     #   cursor= c.execute(sql,  { 'begindate':begindate,'enddate':enddate,'stunum':stunum,'subject':subject} )
     #else:
     sql = sql + "where COMDATE<=:enddate and COMDATE>=:begindate and STUNUM=:stunum  and SUBJECT=:subject  and SUB_TYPE=:sub_type"
     sql = sql + " group by SUBJECT,SUB_TYPE,RESULT "
     sqlb = "select * from comstu where  stunum=:stunum and comdate>=:begindate and comdate<=:enddate and SUBJECT=:subject  and SUB_TYPE=:sub_type"
     sqld = "select * from comstu where  comdate>=:begindate and comdate <=:enddate and subject=:subject and sub_type=:sub_type group by comdate HAVING count(comdate)>1"
     sqle = "select * from comstu where stunum=:stunum and comdate =:comdate and sub_type=:sub_type and subject=:subject"
     cursor= c.execute(sql,  { 'begindate':begindate,'enddate':enddate,'stunum':stunum,'subject':subject,'sub_type':sub_type} )
     cursor2 =b.execute(sqlb, {'stunum':stunum,'begindate':begindate,'enddate':enddate,'subject':subject,'sub_type':sub_type} )
     cursor3 =d.execute(sqld, {'begindate':begindate,'enddate':enddate,'subject':subject,'sub_type':sub_type} )
     rows = cursor3.fetchall()
     listdate =[]
     entries3 =[]
     cwork=0
     for value in rows:

         e = conn.cursor()
         comdate = value[3]
         print value[3]
         cursor4 =e.execute(sqle, {'stunum':stunum,'comdate':comdate,'subject':subject,'sub_type':sub_type})
         wrow = cursor4.fetchone()
         # # for val in wrow:
         #      print val

         if wrow==None:
              cwork =cwork+1
              listdate.append(stunum)
              listdate.append(subject)
              listdate.append(sub_type)
              listdate.append(value[3])
              entries3.append(listdate)
         else:
             print wrow
         cursor4.close()
         e.close()
     print listdate
     print entries3
     return render_template('singlest.html', entries=cursor,entries2=cursor2, weijiao =entries3,cworks=cwork, **locals())

  else:
      sql = "select RESULT,count(RESULT) from COMSTU group by RESULT"
      #sql = sql + " group by SUBJECT,SUB_TYPE,RESULT "
      cursor = c.execute(sql)
      return render_template('singlest.html', entries=cursor, **locals())


@app.route('/score',methods=['GET','POST'])
def score():
  conn = sqlite3.connect('test.db')
  c = conn.cursor()
  # b =conn.cursor()
  if request.method=='POST':
     #grade=request.form['grade']
     stuclass=request.form['stuclass']
     #stunum=request.form['stunum']
     subject=request.form['subject']
     #sub_type =request.form['sub_type']
     begindate = request.form['begindate']
     enddate = request.form['enddate']


     sql = "select stunum,subject, sum(rescount*mark)*20/sum(rescount) as totalscore from v_score "
     sql = sql + "where class=:stuclass  and subject=:subject and comdate>= :begindate and comdate<=:enddate "
     sql = sql + "group by stunum,subject"


     cursor= c.execute(sql,  {'stuclass':stuclass,'subject':subject, 'begindate':begindate,'enddate':enddate} )

     return render_template('score.html', entries=cursor, **locals())

  else:
      sql = "select stunum,subject, sum(rescount*mark)*20/sum(rescount) as totalscore from v_score group by stunum,subject"

      cursor = c.execute(sql)
      return render_template('score.html', entries=cursor, **locals())

@app.route('/student')
def student():
    return render_template('student.html')

@app.route('/instu', methods=['GET','POST'])
def instu():
    if request.method=='POST':
        stunum=request.form['stunum']
        name=request.form['name']
        stuclass=request.form['stuclass']
        grade=request.form['grade']

    else:
        stunum=request.args['stunum']
        name=request.args['name']
        stuclass=request.args['stuclass']
        grade=request.args['grade']

    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute("INSERT INTO STUDENT (STUNUM,NAME,CLASS,GRADE) VALUES (:stuname,:name,:stuclass,:grade,:rfid)",{'stuname':stunum,'name':name,'stuclass':stuclass,'grade':grade});
    conn.commit()
    print ("插入成功")
    conn.close()
    return render_template('student.html')

@app.route('/check')
def check():

  return render_template('check.html')


@app.route('/docheck', methods=['GET','POST'])
def docheck():
  if request.method=='POST':
        print "------"
        rfid=request.form['rfid']
        subject=request.form['subject']
        com = "已交"
        sub_type=request.form['sub_type']
  conn = sqlite3.connect('test.db')
  conn.text_factory = str
  c = conn.cursor()
  c.execute("INSERT INTO COMSTU (RFID,SUBJECT,COM,SUB_TYPE) VALUES (:rfid,:subject,:com,:sub_type)",{'rfid':rfid,'subject':subject,'com':com,'sub_type':sub_type});
  conn.commit()
  print "插入成功"
  conn.close()
  return render_template('check.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
