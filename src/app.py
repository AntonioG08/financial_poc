import os
from flask import Flask, jsonify, request, render_template
from config import Config
from database import db
import models

app = Flask(__name__, template_folder='pages')
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()
    print("Base de datos SQLite y tablas creadas exitosamente.")

@app.route('/api/data', methods=['GET'])
def get_all_data():
    categories = models.Category.query.all()
    checklists = models.Checklist.query.all()
    questions = models.Question.query.all()
    checklist_questions = models.ChecklistQuestion.query.all()

    question_dict = {q.id: q for q in questions}
    checklist_q_map = {}
    for cq in checklist_questions:
        if cq.checklist_id not in checklist_q_map:
            checklist_q_map[cq.checklist_id] = []
        q = question_dict.get(cq.question_id)
        if q:
            checklist_q_map[cq.checklist_id].append({
                "question_text": q.text,
                "prompt": q.prompt
            })
    category_c_map = {}
    for c in checklists:
        if c.category_id not in category_c_map:
            category_c_map[c.category_id] = []
        category_c_map[c.category_id].append({
            "name": c.name,
            "questions": checklist_q_map.get(c.id, [])
        })
    data = []
    for cat in categories:
        data.append({
            "category": cat.name,
            "checklists": category_c_map.get(cat.id, [])
        })
    return jsonify({"data": data})

@app.route('/api/data', methods=['POST'])
def create_data():
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "No se recibió cuerpo JSON"}), 400

    category_input = payload.get('category')
    checklist_input = payload.get('checklist')
    question_text = payload.get('question')
    prompt_text = payload.get('prompt')

    if category_input is None or checklist_input is None or question_text is None or prompt_text is None:
        return jsonify({"error": "Faltan campos requeridos (category, checklist, question, prompt)"}), 400

    try:
        category_obj = None
        if isinstance(category_input, int):
            category_obj = models.Category.query.get(category_input)
            if not category_obj:
                return jsonify({"error": f"No se encontró la categoría con ID: {category_input}"}), 404
        else:
            category_obj = models.Category.query.filter_by(name=str(category_input)).first()
            if not category_obj:
                category_obj = models.Category(name=str(category_input))
                db.session.add(category_obj)
                db.session.flush()

        checklist_obj = None
        if isinstance(checklist_input, int):
            checklist_obj = models.Checklist.query.get(checklist_input)
            if not checklist_obj:
                return jsonify({"error": f"No se encontró el checklist con ID: {checklist_input}"}), 404
        else:
            checklist_obj = models.Checklist.query.filter_by(name=str(checklist_input)).first()
            if not checklist_obj:
                checklist_obj = models.Checklist(name=str(checklist_input), category_id=category_obj.id)
                db.session.add(checklist_obj)
                db.session.flush()

        question_obj = models.Question.query.filter_by(text=str(question_text)).first()
        if not question_obj:
            question_obj = models.Question(text=str(question_text), prompt=str(prompt_text))
            db.session.add(question_obj)
            db.session.flush()

        cq_obj = models.ChecklistQuestion.query.filter_by(
            checklist_id=checklist_obj.id,
            question_id=question_obj.id
        ).first()
        if not cq_obj:
            cq_obj = models.ChecklistQuestion(checklist_id=checklist_obj.id, question_id=question_obj.id)
            db.session.add(cq_obj)

        db.session.commit()
        return jsonify({"message": "Registro completado de forma exitosa", "status": "success"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Ocurrió un error en la transacción SQLite: {str(e)}"}), 500

@app.route('/registro', methods=['GET'])
def registro_page():
    return render_template('create.html')

@app.route('/consulta', methods=['GET'])
def consulta_page():
    return render_template('view.html')

if __name__ == '__main__':
    app.run(debug=True)
