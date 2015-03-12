from mojibake.main import app, db, Post, Category, Tag

a = Post('Test', 'test')
a.add_tags('test')
db.session.add(a)
db.session.commit()
print(Tag.query.all())
db.session.delete(a)
db.session.commit()
print(Tag.query.all())
