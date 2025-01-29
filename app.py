from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Создание объекта Flask
app = Flask(__name__)

# Настройки для подключения к базе данных PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1212@localhost/newtable'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Отключаем уведомления об изменениях в базе данных

# Инициализация SQLAlchemy
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    category = db.Column(db.String)
    description = db.Column(db.String)
    cook_time = db.Column(db.Integer)
    ingredients = db.Column(db.String)


with app.app_context():
    db.create_all()
    print("База данных создана успешно!")


@app.route('/')
def index():
    category = request.args.get('category')
    search = request.args.get('search')
    query = Recipe.query
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter((Recipe.title.contains(search)) | (Recipe.ingredients.contains(search)))
    recipes = query.all()
    return render_template('index.html', recipes=recipes)


@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('recipe.html', recipe=recipe)


@app.route('/add', methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        description = request.form['description']
        cook_time = request.form['cook_time']
        ingredients = request.form['ingredients']
        new_recipe = Recipe(title=title, category=category, description=description,
                            cook_time=cook_time, ingredients=ingredients)
        db.session.add(new_recipe)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_recipe.html')

@app.route('/edit/<int:recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if request.method == 'POST':
        recipe.title = request.form['title']
        recipe.category = request.form['category']
        recipe.description = request.form['description']
        recipe.cook_time = request.form['cook_time']
        recipe.ingredients = request.form['ingredients']
        db.session.commit()
        return redirect(url_for('recipe_detail', recipe_id=recipe.id))
    return render_template('edit_recipe.html', recipe=recipe)

@app.route('/delete/<int:recipe_id>')
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    db.session.delete(recipe)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
