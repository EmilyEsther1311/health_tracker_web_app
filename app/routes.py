import os

from datetime import datetime, timedelta

from flask import render_template, redirect, url_for, flash, request, current_app, send_from_directory
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
import sqlalchemy as sa
from flask_login import login_user, current_user, login_required, logout_user
from urllib.parse import urlsplit
from werkzeug.utils import secure_filename

from app import app, db
from app.models import *
from app.forms import *



@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html')

@app.route("/support-groups")
@login_required
def support_groups():
    support_groups = SupportGroup.query.order_by(SupportGroup.name).all()

    return render_template('view_support_groups.html', support_groups=support_groups, title='Support Groups')

@app.route("/support-group/new", methods=["GET", "POST"])
@login_required
def support_group_new():
    form = SupportGroupForm()
    if form.validate_on_submit():
        s_group = SupportGroup(name = form.name.data, leader_id=current_user.id)

        try:
            db.session.add(s_group)
            db.session.commit()
            flash(f"You are now the leader of the support group {s_group.name}")
            return redirect(url_for('support_groups'))
        except IntegrityError:
            db.session.rollback()
            flash(f"Support group has already been added")

    return render_template("support_group_form.html", form=form, title='Add Support Group')

@app.route("/support-group/<int:s_group_id>/join", methods=["GET", "POST"])
@login_required
def support_group_join(s_group_id):
    s_group = SupportGroup.query.get_or_404(s_group_id)
    u_group = UserGroup(user_id = current_user.id, s_group_id=s_group_id)

    try:
        db.session.add(u_group)
        db.session.commit()
        flash(f"You are now a member of the support group {s_group.name}")
    except IntegrityError:
        db.session.rollback()
        flash(f"You are already a member of the support group {s_group.name}")

    return redirect(url_for('support_groups'))

@app.route("/view-members/<int:s_group_id>", methods=["GET", "POST"])
@login_required
def view_members(s_group_id):
    s_group = SupportGroup.query.get_or_404(s_group_id)
    members = [ug.member for ug in s_group.members]

    return render_template("view_members.html", members=members, s_group=s_group)

@app.route("/remove-member/<int:s_group_id>/<int:member_id>", methods=["GET", "POST"])
@login_required
def remove_member(s_group_id, member_id):
    s_group = SupportGroup.query.get_or_404(s_group_id)
    member = User.query.get_or_404(member_id)
    if current_user.id == s_group.leader_id:
        u_group = db.session.scalar(select(UserGroup).where(UserGroup.user_id==member_id, UserGroup.s_group_id==s_group_id))
        if u_group is None:
            flash(f"Cannot remove {member.username} as they are not a member of {s_group.name}")
        else:
            db.session.delete(u_group)
            db.session.commit()
            flash(f"{member.username} successfully removed from {s_group.name}")
    else:
        flash(f"Only the leader is allowed to remove group members")

    return redirect(url_for("view_members", s_group_id=s_group_id))

@app.route("/support-group/<int:s_group_id>/delete", methods=["GET", "POST"])
@login_required
def support_group_delete(s_group_id):
    s_group = SupportGroup.query.get_or_404(s_group_id)

    if current_user.id == s_group.leader_id:
        db.session.delete(s_group)
        db.session.commit()
        flash(f"Support group {s_group.name} has been successfully deleted")
    else:
        flash(f"Only the leader is allowed to delete the support group")

    return redirect(url_for('support_groups'))

@app.route("/exercise-types")
@login_required
def exercise_types():
    intensity = request.args.get("intensity")

    query = ExerciseType.query #Create the query object

    if intensity:
        exercise_types = query.filter(ExerciseType.intensity == int(intensity)).all()
    else:
        exercise_types = query.order_by(ExerciseType.intensity).all()

    return render_template('view_exercise_types.html', exercise_types=exercise_types, intensity=intensity, title='Exercise Types') #Pass through 'intensity' to ensure dropdown selection persistence

@app.route("/exercise-types/new", methods=["GET", "POST"])
@login_required
def exercise_type_new():
    form = ExerciseTypeForm()
    if form.validate_on_submit():

        file = form.attachment.data

        if file:  # Check if a file was uploaded
            filename = secure_filename(file.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            file.save(os.path.join(upload_folder, filename))
        else:
            filename = None

        type = ExerciseType(description = form.description.data, duration = form.duration.data, intensity=form.intensity.data, attachment_filename=filename)

        try:
            db.session.add(type)
            db.session.commit()
            flash(f"New exercise type has been successfully added")
            return redirect(url_for('exercise_types'))
        except IntegrityError:
            db.session.rollback()
            flash(f"Exercise type has already been added")

    return render_template("exercise_types_form.html", form=form, title='Add Exercise Type')

@app.route("/exercise-types/<int:type_id>/edit", methods=["GET", "POST"])
@login_required
def exercise_type_edit(type_id):
    type = ExerciseType.query.get_or_404(type_id)
    form = ExerciseTypeForm(obj=type)

    if form.validate_on_submit():
        try:
            type.description = form.description.data
            type.duration = form.duration.data
            type.intensity = form.intensity.data

            file = form.attachment.data

            # Update only if a new file is provided
            if file and file.filename:
                filename = secure_filename(file.filename)
                upload_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(upload_path)
                type.attachment_filename = filename

            db.session.commit()
            flash(f"Exercise type has been successfully updated")
            return redirect(url_for('exercise_types'))

        except IntegrityError:
            db.session.rollback()
            flash(f"Exercise type already exists")

    return render_template('exercise_types_form.html', form=form, type=type, title='Update Exercise Type')

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_folder,filename,as_attachment=True)

@app.route("/exercise-types/<int:type_id>/delete", methods=["GET","POST"])
@login_required
def exercise_type_delete(type_id):
    type = ExerciseType.query.get_or_404(type_id)
    db.session.delete(type)
    db.session.commit()
    flash(f"Exercise type has been successfully deleted")
    return redirect(url_for('exercise_types'))


@app.route('/record_activity', methods=['GET', 'POST'])
@login_required
def record_activity():
    form = ActivityForm()
    form.exercise_type_id.choices = [
        (type.id, type.description) for type in
        ExerciseType.query.all()
    ]
    if form.validate_on_submit():
        activity = Activity(start_time=form.start_time.data, end_time=form.end_time.data, notes=form.notes.data, user_id=current_user.id, exercise_type_id = form.exercise_type_id.data)

        try:
            db.session.add(activity)
            db.session.commit()
            flash(f"New activity has been successfully recorded")
            return redirect(url_for('calendar'))
        except IntegrityError:
            db.session.rollback()
            flash(f"This activity has already been recorded")

    return render_template('record_activity.html', form=form, title='Record Activity')

@app.route('/body_measurement', methods=['GET', 'POST'])
@login_required
def body_measurement():
    form = BodyMeasurementForm()
    if form.validate_on_submit():
        measurement = BodyMeasurement(user_id=current_user.id, timestamp=datetime.now().date(), weight = form.weight.data, pulse = form.pulse.data)

        try:
            db.session.add(measurement)
            db.session.commit()
            flash(f"New body measurement has been successfully recorded")
            return redirect(url_for('index'))
        except IntegrityError:
            db.session.rollback()
            flash(f"Today's body measurement has already been recorded")
            return redirect(url_for('index'))
    return render_template("body_measurement_form.html", form=form, title = 'Record Body Measurement')

@app.route('/calendar', methods=['GET', 'POST'])
@login_required
def calendar():
    form = CalendarForm()
    days = None
    activities = []
    measurements = []
    if form.validate_on_submit():

        delta = form.end_date.data - form.start_date.data
        days = [form.start_date.data + timedelta(days=i) for i in range(delta.days + 1)]

        activities = Activity.query.filter(
            Activity.start_time >= form.start_date.data,
            Activity.end_time < form.end_date.data + timedelta(days=1)
        ).all()

        measurements = BodyMeasurement.query.filter(
            BodyMeasurement.timestamp >= form.start_date.data,
            BodyMeasurement.timestamp <= form.end_date.data
        ).all()

        return render_template('calendar.html', days=days, activities=activities, measurements=measurements, form=form, title = ' Activity Calendar')
    return render_template('calendar.html', days=days, activities=activities, measurements=measurements, form=form, title = 'Activity Calendar')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
