import dbconnect
import sys

class recall:
	def __init__(self):
		self.year=''
		self.make=''
		self.make=''
		self.model=''
		self.component=''
		self.connection=''
		self.cursor=''
		self.year_sql='select yeartxt from recall_db group by yeartxt'
		self.make_sql='select maketxt from recall_db where yeartxt=%s group by maketxt'
		self.model_sql='select modeltxt from recall_db where yeartxt=%s and maketxt=%s group by modeltxt'
	def get_connection(self):
		self.connection=dbconnect.get_connection()
		self.cursor=self.connection.cursor()
	def show_year(self):
		self.cursor.execute(self.year_sql)
		year_list=self.cursor.fetchall()
		return year_list
	def set_year(self,year):
		self.year=int(year)
	def show_make(self):
		if not self.year:
			make_list='No year selected'
		else:
			self.cursor.execute(self.make_sql,(self.year))
			make_list=self.cursor.fetchall()
			return make_list
	def set_make(self,make):
		self.make=make
	def show_model(self):
		if not self.year:
			model_list='No Year selected'
		elif not self.make:
			model_list='No Make selected'
		else:
			self.cursor.execute(self.model_sql,(self.year,self.make))
			model_list=self.cursor.fetchall()
			return model_list
		



r=recall()
r.get_connection()
r.set_year('1998')
r.set_make('cadillac')
r.show_model()
		
