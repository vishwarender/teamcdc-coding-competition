import os
import csv
import json
from datetime import datetime, timedelta
from io import StringIO
from flask import render_template, redirect, url_for, request, flash, jsonify, send_file, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import or_, desc, func

from app import app, db
from models import Admin, School, Registration, TeamMember, Submission, Setting
from forms import LoginForm, SchoolForm, RegistrationForm, SubmissionForm

ALLOWED_CODE_EXTENSIONS = {'zip', 'rar', '7z', 'html', 'css', 'py', 'js', 'sb3'}
ALLOWED_PRESENTATION_EXTENSIONS = {'jpg', 'png', 'pdf', 'mp4', 'pptx'}

def allowed_code_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_CODE_EXTENSIONS

def allowed_presentation_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_PRESENTATION_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    # Populate school dropdown
    form.school_id.choices = [(school.id, school.name) for school in School.query.order_by(School.name).all()]

    if form.validate_on_submit():
        # Create new registration
        registration = Registration(
            full_name=form.full_name.data,
            grade=form.grade.data,
            whatsapp_number=form.whatsapp_number.data,
            school_id=form.school_id.data,
            team_members_count=form.team_members_count.data,
            society_name=form.society_name.data,
            president_name=form.president_name.data,
            president_number=form.president_number.data,
            teacher_name=form.teacher_name.data,
            teacher_number=form.teacher_number.data
        )

        db.session.add(registration)
        db.session.commit()

        # Get team members data from form
        team_members_data = []
        for i in range(1, form.team_members_count.data):
            member_name = request.form.get(f'member_name_{i}')
            member_whatsapp = request.form.get(f'member_whatsapp_{i}')

            if member_name and member_whatsapp:
                member = TeamMember(
                    name=member_name,
                    whatsapp_number=member_whatsapp,
                    registration_id=registration.id
                )
                team_members_data.append(member)

        # Add team members to database
        if team_members_data:
            db.session.add_all(team_members_data)
            db.session.commit()

        flash('Registration successful!', 'success')
        return redirect(url_for('index'))

    return render_template('register.html', form=form)

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    form = SubmissionForm()

    # Populate participants dropdown
    registrations = Registration.query.join(School).all()
    form.participant.choices = [(r.id, f"{r.full_name} - {r.school.name}") for r in registrations]

    if form.validate_on_submit():
        # Check if files were uploaded
        if 'code_file' not in request.files:
            flash('No code file uploaded', 'danger')
            return redirect(request.url)

        code_file = request.files['code_file']
        presentation_file = request.files.get('presentation_file')

        if code_file.filename == '':
            flash('No code file selected', 'danger')
            return redirect(request.url)

        if not allowed_code_file(code_file.filename):
            flash('Invalid code file format. Allowed formats: zip, rar, 7z, html, css, py, js, sb3', 'danger')
            return redirect(request.url)

        # Save code file locally
        code_filename = secure_filename(code_file.filename)
        code_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{form.participant.data}_code_{datetime.now().strftime('%Y%m%d%H%M%S')}_{code_filename}")
        code_file.save(code_path)

        # Save presentation file if provided
        presentation_path = None
        if presentation_file and presentation_file.filename != '':
            if not allowed_presentation_file(presentation_file.filename):
                flash('Invalid presentation file format. Allowed formats: jpg, png, pdf, mp4, pptx', 'danger')
                return redirect(request.url)

            presentation_filename = secure_filename(presentation_file.filename)
            presentation_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{form.participant.data}_presentation_{datetime.now().strftime('%Y%m%d%H%M%S')}_{presentation_filename}")
            presentation_file.save(presentation_path)

        # Create submission record
        submission = Submission(
            registration_id=form.participant.data,
            description=form.description.data,
            code_file_path=code_path,
            presentation_file_path=presentation_path
        )

        db.session.add(submission)
        db.session.commit()

        flash('Project submitted successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('submit.html', form=form)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and check_password_hash(admin.password_hash, form.password.data):
            login_user(admin)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('admin/login.html', form=form)

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    # Count statistics for dashboard
    total_schools = School.query.count()
    total_registrations = Registration.query.count()
    total_submissions = Submission.query.count()

    # Get current date and deadline
    now = datetime.now()
    deadline_setting = Setting.query.get('submission_deadline')
    current_deadline = datetime.fromisoformat(deadline_setting.value) if deadline_setting else None

    return render_template('admin/dashboard.html', 
                          total_schools=total_schools,
                          total_registrations=total_registrations,
                          total_submissions=total_submissions,
                          now=now,
                          current_deadline=current_deadline)

@app.route('/admin/set-deadline', methods=['POST'])
@login_required
def set_deadline():
    date_str = request.form.get('deadline_date')
    time_str = request.form.get('deadline_time')
    send_notification = request.form.get('send_notification') == 'on'

    try:
        deadline = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        db.session.add_all([
            Setting(key='submission_deadline', value=deadline.isoformat())
        ])
        db.session.commit()

        if send_notification:
            # TODO: Implement notification system
            pass

        flash('Deadline updated successfully!', 'success')
    except Exception as e:
        flash('Error setting deadline: ' + str(e), 'danger')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/schools', methods=['GET', 'POST'])
@login_required
def admin_schools():
    form = SchoolForm()
    if form.validate_on_submit():
        school = School(name=form.name.data)
        db.session.add(school)
        db.session.commit()
        flash('School added successfully!', 'success')
        return redirect(url_for('admin_schools'))

    schools = School.query.order_by(School.name).all()
    return render_template('admin/schools.html', schools=schools, form=form)

@app.route('/admin/schools/delete/<int:id>', methods=['POST'])
@login_required
def delete_school(id):
    school = School.query.get_or_404(id)
    if Registration.query.filter_by(school_id=id).first():
        flash('Cannot delete school that has registrations', 'danger')
    else:
        db.session.delete(school)
        db.session.commit()
        flash('School deleted successfully', 'success')
    return redirect(url_for('admin_schools'))

@app.route('/admin/participants')
@login_required
def admin_participants():
    # Get filter parameters
    grade = request.args.get('grade', type=int)
    school_id = request.args.get('school_id', type=int)
    search = request.args.get('search', '')

    # Base query
    query = Registration.query.join(School)

    # Apply filters
    if grade:
        query = query.filter(Registration.grade == grade)
    if school_id:
        query = query.filter(Registration.school_id == school_id)
    if search:
        query = query.filter(
            or_(
                Registration.full_name.ilike(f'%{search}%'),
                School.name.ilike(f'%{search}%')
            )
        )

    registrations = query.order_by(Registration.registration_date.desc()).all()
    schools = School.query.order_by(School.name).all()

    return render_template('admin/participants.html', 
                          registrations=registrations, 
                          schools=schools)

@app.route('/admin/participant/<int:id>')
@login_required
def view_participant(id):
    registration = Registration.query.get_or_404(id)
    return jsonify({
        'id': registration.id,
        'full_name': registration.full_name,
        'grade': registration.grade,
        'whatsapp_number': registration.whatsapp_number,
        'school': registration.school.name,
        'team_members_count': registration.team_members_count,
        'society_name': registration.society_name,
        'president_name': registration.president_name,
        'president_number': registration.president_number,
        'teacher_name': registration.teacher_name,
        'teacher_number': registration.teacher_number,
        'registration_date': registration.registration_date.strftime('%Y-%m-%d %H:%M'),
        'team_members': [
            {
                'name': member.name,
                'whatsapp_number': member.whatsapp_number
            } for member in registration.team_members
        ]
    })

@app.route('/admin/export/participants')
@login_required
def export_participants():
    registrations = Registration.query.join(School).order_by(Registration.registration_date.desc()).all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Full Name', 'Grade', 'WhatsApp Number', 'School', 
                    'Team Members Count', 'Society Name', 'President Name',
                    'President Number', 'Teacher Name', 'Teacher Number',
                    'Registration Date'])

    for reg in registrations:
        writer.writerow([
            reg.id, reg.full_name, f"Grade {reg.grade}", reg.whatsapp_number,
            reg.school.name, reg.team_members_count, reg.society_name or '',
            reg.president_name or '', reg.president_number or '',
            reg.teacher_name or '', reg.teacher_number or '',
            reg.registration_date.strftime('%Y-%m-%d %H:%M')
        ])

    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name=f'participants_{datetime.now().strftime("%Y%m%d")}.csv',
        mimetype='text/csv'
    )

@app.route('/admin/submissions')
@login_required
def admin_submissions():
    # Get filter parameters
    grade = request.args.get('grade', type=int)
    school_id = request.args.get('school_id', type=int)
    search = request.args.get('search', '')

    # Base query
    query = Submission.query.join(Registration).join(School)

    # Apply filters
    if grade:
        query = query.filter(Registration.grade == grade)
    if school_id:
        query = query.filter(Registration.school_id == school_id)
    if search:
        query = query.filter(
            or_(
                Registration.full_name.ilike(f'%{search}%'),
                School.name.ilike(f'%{search}%'),
                Submission.description.ilike(f'%{search}%')
            )
        )

    submissions = query.order_by(Submission.submission_date.desc()).all()
    schools = School.query.order_by(School.name).all()

    return render_template('admin/submissions.html', 
                          submissions=submissions, 
                          schools=schools)

@app.route('/admin/export/submissions')
@login_required
def export_submissions():
    submissions = Submission.query.join(Registration).join(School).order_by(Submission.submission_date.desc()).all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Participant Name', 'Grade', 'School', 
                    'Description', 'Code File', 'Presentation File',
                    'Submission Date'])

    for sub in submissions:
        writer.writerow([
            sub.id, sub.registration.full_name, f"Grade {sub.registration.grade}",
            sub.registration.school.name, sub.description[:50] + '...' if len(sub.description) > 50 else sub.description,
            os.path.basename(sub.code_file_path), 
            os.path.basename(sub.presentation_file_path) if sub.presentation_file_path else 'None',
            sub.submission_date.strftime('%Y-%m-%d %H:%M')
        ])

    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name=f'submissions_{datetime.now().strftime("%Y%m%d")}.csv',
        mimetype='text/csv'
    )

@app.route('/admin/download/<path:filename>')
@login_required
def download_file(filename):
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        app.logger.error(f"Error downloading file: {e}")
        abort(404)
@app.route('/admin/reset_db')
@login_required
def reset_db():
    try:
        # Drop all tables
        db.session.close()
        db.drop_all()
        db.session.commit()
        
        # Recreate all tables
        db.create_all()
        
        # Re-create admin user
        admin = Admin(
            username="Vishwa1214",
            password_hash=generate_password_hash("bcgvishwa@1214@")
        )
        db.session.add(admin)
        db.session.commit()

        # Clear uploads folder
        for file in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                app.logger.error(f"Error deleting file {file_path}: {e}")
        
        flash('Database and uploads reset successfully!', 'success')
        return redirect(url_for('admin_logout'))
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Database reset error: {str(e)}")
        flash(f'Error resetting database: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))
