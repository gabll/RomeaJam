from RomeaJam.traffik import db, Segment
import credentials

#create tables
db.create_all()

#add base segments
l1=(Segment(*credentials.l1))
l2=(Segment(*credentials.l2))
l3=(Segment(*credentials.l3))
l4=(Segment(*credentials.l4))
a1=(Segment(*credentials.a1))
a2=(Segment(*credentials.a2))
a3=(Segment(*credentials.a3))
a4=(Segment(*credentials.a4))
db.session.add(l1)
db.session.add(l2)
db.session.add(l3)
db.session.add(l4)
db.session.add(a1)
db.session.add(a2)
db.session.add(a3)
db.session.add(a4)
db.session.commit()
