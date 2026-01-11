import uuid
from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import get_user_by_name, create_user, save_stash, get_user_stashes, delete_stash
from gemini_service import summarize_content
import os

app = Flask(__name__)
app.secret_key = 'stash_secret_key_change_in_prod'

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    user_name = request.form.get('user_name').strip()
    
    if not user_name:
        flash("Please enter a valid name.", "danger")
        return redirect(url_for('index'))

    existing_user = get_user_by_name(user_name)
    
    if existing_user:
        session['user_id'] = existing_user['user_id']
        session['user_name'] = existing_user['user_name']
    else:
        new_id = str(uuid.uuid4())
        if create_user(new_id, user_name):
            session['user_id'] = new_id
            session['user_name'] = user_name
        else:
            flash("Database error creating user.", "danger")
            return redirect(url_for('index'))
            
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    stashes = get_user_stashes(session['user_id'])
    return render_template('dashboard.html', user_name=session['user_name'], stashes=stashes)

@app.route('/stash_url', methods=['POST'])
def stash_url():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    url_link = request.form.get('url_link')
    if not url_link:
        flash("Please enter a URL.", "warning")
        return redirect(url_for('dashboard'))
    
    # 1. Process with Gemini
    ai_result = summarize_content(url_link)
    
    # 2. Prepare Data
    url_id = str(uuid.uuid4())
    summary = ai_result.get('summary', 'No summary available.')
    tags = ai_result.get('tags', '')
    
    # 3. Save to DB
    if save_stash(url_id, session['user_id'], url_link, summary, tags):
        flash("URL Stashed and Summarized!", "success")
    else:
        flash("Database error.", "danger")
        
    return redirect(url_for('dashboard'))

@app.route('/delete_stash/<url_id>', methods=['POST'])
def remove_stash(url_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    if delete_stash(url_id):
        flash("Stash deleted.", "success")
    else:
        flash("Error deleting stash.", "danger")
        
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001) # Using 5001 to avoid conflict if previous app is running