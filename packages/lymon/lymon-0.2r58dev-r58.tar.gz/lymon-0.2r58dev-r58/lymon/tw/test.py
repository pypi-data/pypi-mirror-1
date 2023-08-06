#from sqlalchemy import *
#from sqlalchemy.orm import *
#from sqlalchemy.ext.declarative import declarative_base
#engine = create_engine('sqlite://')
#Session = scoped_session(sessionmaker(autoflush=True, bind=engine))
#Base = declarative_base(engine, mapper=Session.mapper)



#class Order(Base):
#	__tablename__ = 'orders'
#	id = Column('id', Integer, primary_key=True)
#	user_id = Column('user_id', Integer, ForeignKey('users.id'), nullable=False)
#	quantity = Column('quantity', Integer, nullable=False)
#	def __str__(self):
#		return 'Quantity: %s' % self.quantity

#class User(Base):
#	__tablename__ = 'users'
#	id = Column('id', Integer, primary_key=True)
#	name = Column('name', Unicode(30))
#	orders = relation(Order, backref='user')
#	def __str__(self):
#		return self.name

#Base.metadata.create_all()
#session = Session()

#bill = User(name='Bill')
#john = User(name='John')
#order1 = Order(user=bill, quantity=10)
#session.commit()

##from formalchemy import FieldSet
##FieldSet(order1).render()

#from lymon.tw import ModelFields, ModelTable

#w = ModelFields(model=order1)
#print w.display()



