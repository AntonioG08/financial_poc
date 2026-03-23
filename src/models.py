from database import db

class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

class Checklist(db.Model):
    __tablename__ = "checklists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))

class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False, unique=True)
    prompt = db.Column(db.Text, nullable=False)

class ChecklistQuestion(db.Model):
    __tablename__ = "checklist_questions"

    id = db.Column(db.Integer, primary_key=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey("checklists.id"))
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))

class Factor(db.Model):
    __tablename__ = "factors"
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255), nullable=False, unique=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey("checklists.id"))

class Reference(db.Model):
    __tablename__ = "references"
    id = db.Column(db.Integer, primary_key=True)
    reference_title = db.Column(db.String(255), nullable=False, unique=True)
    reference_url = db.Column(db.String(255), nullable=False, unique=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey("checklists.id"))
