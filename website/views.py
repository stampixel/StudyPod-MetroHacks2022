from flask import Blueprint, render_template, redirect, request, flash, url_for
from flask_login import login_required, current_user
from . import db
from website.models import Notes, User, Checklist
import random
import string
import requests

views = Blueprint('views', __name__)


# Home
@views.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('views.main'))
    else:
        return render_template('home.html', user=current_user)


# MAIN: Everything will be here
@views.route('/main', methods=['GET', 'POST'])  # DONE
@login_required
def main():
    if request.method == 'POST':
        try:
            if request.form['create_note'] == "Create Note":
                return redirect(url_for('views.edit_note'))
        except:
            pass
        try:
            # Use code from ryptical
            if request.form['add_task']:
                note_content = request.form['add_task']
                task = Checklist(content=note_content, user_id=current_user.id)
                db.session.add(task)
                db.session.commit()
        except:
            pass

    return render_template("main.html", user=current_user)


# NOTE EDITOR
@views.route('/editor', methods=['GET', 'POST'])
@login_required
def edit_note():
    if request.method == 'POST':
        # try:
        if request.form['save'] == "Save":  # Saves to db
            title = request.form['title']
            paste_content = request.form['paste_content']
            if paste_content == "":
                flash("Paste Something First!", category='error')
                return redirect(url_for('views.edit_note'))

            else:
                if title == "":
                    title = "New Paste"
                url_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(7))
                note = Notes(url_id=url_id, title=title, content=paste_content, user_id=current_user.id)
                db.session.add(note)
                db.session.commit()
                flash('New Paste Created!', category='success')
                return redirect(url_for('views.main'))
        # except:
        #     flash("Something went wrong!", category='error')
    return render_template("note_editor.html", user=current_user)


# UPDATING NOTE
@views.route('/edit/note/<int:id>', methods=['POST', 'GET'])
@login_required
def update_note(id):
    note_to_update = Notes.query.get_or_404(id)
    if request.method == 'POST':
        note_to_update.content = request.form['paste_content']

        if request.form['title'] is not "":
            note_to_update.title = request.form['title']
        try:
            db.session.commit()
            return redirect('/')
        except:
            flash("An error has occurred!", category='error')
    return render_template('note_updater.html', note=note_to_update, user=current_user)


# DELETING THE NOTE
@views.route('/delete/note/<int:id>')  # DONE
@login_required
def delete_note(id):
    note_to_delete = Notes.query.get_or_404(id)
    try:
        db.session.delete(note_to_delete)
        db.session.commit()
        return redirect(url_for('views.main'))
    except:
        flash('Try again later.', category='error')


# SHOW NOTE
@views.route('/<url_id>')
def show_note(url_id):
    note = Notes.query.filter_by(url_id=url_id).first_or_404()
    return render_template('show_note.html', note=note)  # fix show_not


# DELETING THE task
@views.route('/delete/task/<int:id>')
@login_required
def delete_task(id):
    task_to_delete = Checklist.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect(url_for('views.main'))
    except:
        flash('Try again later.', category='error')


# SUMMARY
@views.route('/note/summary/<int:id>')
@login_required
def note_summary(id):
    # flash message saying the note is to short to be summarized, return redirect... if it goes wrong
    note_to_summarize = Notes.query.get_or_404(id)
    if len(note_to_summarize.content) < 50:
        flash('Must have over 50 chars in order to summarize properly.', category='error')
        return render_template('text_summary.html', note=note_to_summarize, user=current_user,
                               summary=note_to_summarize.content)
    elif len(note_to_summarize.content) > 3000:
        flash('Text is to over the char limit (5000).', category='error')
        return render_template('text_summary.html', note=note_to_summarize, user=current_user,
                               summary=note_to_summarize.content)
    else:
        YOUR_API_KEY = "API KEY GOES HERE"

        long_text = note_to_summarize.content

        out = requests.post(
            "https://api.ai21.com/studio/v1/experimental/summarize",
            headers={"Authorization": f"Bearer {YOUR_API_KEY}"},
            json={
                "text": long_text
            }
        )
        return render_template('text_summary.html', note=note_to_summarize, user=current_user,
                               summary=out.json()["summaries"][0]["text"])
