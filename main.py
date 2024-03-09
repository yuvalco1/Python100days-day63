from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float

app = Flask(__name__)

app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR'
bootstrap = Bootstrap5(app)


class Base(DeclarativeBase):
    pass


all_books = []


class BookForm(FlaskForm):
    book_name = StringField('Book Name', validators=[DataRequired()])
    book_author = StringField('Author Name', validators=[DataRequired()])
    book_rating = SelectField('Rating', choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], validators=[DataRequired()])
    submit = SubmitField('Add book')


class EditRatingForm(FlaskForm):
    book_name = HiddenField('Book Name')
    current_rating = HiddenField('Current Rating')
    new_rating = SelectField('New Rating', choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], validators=[DataRequired()])
    submit = SubmitField('Update book rating')


@app.route('/user/<int:id>/', methods=['GET', 'POST'])
def edit(id):
    book_to_update = db.get_or_404(Book, id)
    form = EditRatingForm()
    form.book_name.data = book_to_update.title
    form.current_rating.data = book_to_update.rating
    new_rating = form.new_rating.data
    if form.validate_on_submit():
        book_to_update.rating = new_rating
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit_rating.html', form=form)


@app.route("/delete")
def delete():
    book_id = request.args.get('id')

    # DELETE A RECORD BY ID
    book_to_delete = db.get_or_404(Book, book_id)
    # Alternative way to select the book to delete.
    # book_to_delete = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/')
def home():
    result = db.session.execute(db.select(Book).order_by(Book.title))
    all_books = result.scalars()
    return render_template('index.html', books=all_books)


@app.route("/add", methods=['GET', 'POST'])
def add():
    form = BookForm()
    book_name = form.book_name.data
    book_author = form.book_author.data
    book_rating = form.book_rating.data
    if form.validate_on_submit():
        all_books.append({'title': book_name, 'author': book_author, 'rating': book_rating})
        new_book = Book(title=book_name, author=book_author, rating=book_rating)
        db.session.add(new_book)
        try:
            db.session.commit()
        except:
            print("An error occurred adding the book")

        return redirect(url_for('home'))
    return render_template('add.html', form=form)


# # CREATE RECORD
# with app.app_context():
#     new_book = Book(id=1, title="Harry and Potter 10", author="J. K. Rowling", rating=9.1)
#     db.session.add(new_book)
#     db.session.commit()
#     print("write complete")


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-books-collection.db"

db = SQLAlchemy(model_class=Base)
# configure the SQLite database, relative to the app instance folder
# initialize the app with the extension
db.init_app(app)


class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)


# Optional: this will allow each book object to be identified by its title when printed.
def __repr__(self):
    return f'<Book {self.title}>'


with app.app_context():
    db.create_all()
    print('test')

if __name__ == "__main__":
    app.run(debug=True)
