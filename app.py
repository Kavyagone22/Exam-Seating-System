from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam_seating.db'
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    roll_no = db.Column(db.String(50), unique=True)
    department = db.Column(db.String(100))
    semester = db.Column(db.Integer)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_no = db.Column(db.String(50), unique=True)
    capacity = db.Column(db.Integer)

@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form['name']
    roll_no = request.form['roll_no']
    department = request.form['department']
    semester = request.form['semester']

    existing_student = Student.query.filter_by(roll_no=roll_no).first()
    if existing_student:
        flash('Student with this Roll No already exists!')
        return redirect(url_for('index'))

    new_student = Student(
        name=name,
        roll_no=roll_no,
        department=department,
        semester=semester
    )
    try:
        db.session.add(new_student)
        db.session.commit()
        flash('Student added successfully!')
    except IntegrityError:
        db.session.rollback()
        flash('Error: Student with this Roll No already exists!')
    return redirect(url_for('index'))

@app.route('/add_room', methods=['POST'])
def add_room():
    room_no = request.form['room_no']
    capacity = request.form['capacity']

    existing_room = Room.query.filter_by(room_no=room_no).first()
    if existing_room:
        flash('Room with this number already exists!')
        return redirect(url_for('index'))

    new_room = Room(
        room_no=room_no,
        capacity=capacity
    )
    try:
        db.session.add(new_room)
        db.session.commit()
        flash('Room added successfully!')
    except IntegrityError:
        db.session.rollback()
        flash('Error: Room with this number already exists!')
    return redirect(url_for('index'))

@app.route('/generate_seating')
def generate_seating():
    students = Student.query.all()
    rooms = Room.query.all()
    seating = []
    seat_number = 1

    # Simple assignment: all students to first room, increment seat numbers
    if students and rooms:
        room = rooms[0]
        for student in students:
            seating.append({
                'roll_no': student.roll_no,
                'room_no': room.room_no,
                'seat_number': seat_number
            })
            seat_number += 1

    return render_template('seating.html', seating=seating)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)