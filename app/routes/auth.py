from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.database import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()
        action = request.form.get('action', 'login')

        if not phone:
            flash('कृपया अपना मोबाइल नंबर दर्ज करें।', 'danger')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(phone=phone).first()

        if action == 'register':
            if user:
                flash('यह मोबाइल नंबर पहले से पंजीकृत है। कृपया लॉगिन करें।', 'warning')
                return redirect(url_for('auth.login'))
            
            # Register with standard rules
            user = User(
                phone=phone,
                name=f"User_{phone[-4:]}",
                role='admin' if phone == '9829943216' else 'user'
            )
            reg_password = password if password else phone
            user.set_password(reg_password)
            db.session.add(user)
            db.session.commit()
            
            login_user(user, remember=True)
            flash('सफलतापूर्वक पंजीकरण हो गया है! अपनी प्रोफ़ाइल अपडेट करें।', 'success')
            return redirect(url_for('auth.profile'))

        # Login action
        if not user:
            # Auto register for convenience
            user = User(
                phone=phone,
                name=f"User_{phone[-4:]}",
                role='admin' if phone == '9829943216' else 'user'
            )
            login_password = password if password else phone
            user.set_password(login_password)
            db.session.add(user)
            db.session.commit()

        if user.check_password(password) or user.check_password(phone):
            login_user(user, remember=True)
            flash(f'स्वागत है {user.name or user.phone}!', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('main.index'))
        else:
            flash('गलत पासवर्ड। कृपया पुनः प्रयास करें।', 'danger')

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('आप सफलतापूर्वक लॉग आउट हो गए हैं।', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        action = request.form.get('action', 'update_profile')

        if action == 'change_password':
            current_pass = request.form.get('current_password', '').strip()
            new_pass = request.form.get('new_password', '').strip()
            confirm_pass = request.form.get('confirm_password', '').strip()

            if not current_user.check_password(current_pass) and not current_user.check_password(current_user.phone):
                flash('वर्तमान पासवर्ड गलत है।', 'danger')
                return redirect(url_for('auth.profile'))

            if len(new_pass) < 6 or not any(c.isalpha() for c in new_pass) or not any(c.isdigit() for c in new_pass):
                flash('पासवर्ड कम से कम 6 अक्षरों का होना चाहिए और उसमें अक्षर और अंक दोनों होने चाहिए।', 'warning')
                return redirect(url_for('auth.profile'))

            if new_pass != confirm_pass:
                flash('नया पासवर्ड और पुष्टि पासवर्ड मेल नहीं खाते।', 'danger')
                return redirect(url_for('auth.profile'))

            current_user.set_password(new_pass)
            db.session.commit()
            flash('आपका पासवर्ड सफलतापूर्वक बदल दिया गया है!', 'success')
            return redirect(url_for('auth.profile'))

        # Update Profile Details (Name, Email, Location, DOB, Lat, Long)
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        location = request.form.get('location', '').strip()
        dob = request.form.get('dob', '').strip()
        lat = request.form.get('latitude')
        lng = request.form.get('longitude')

        current_user.name = name
        current_user.email = email
        current_user.location = location
        current_user.dob = dob

        if lat:
            try:
                current_user.latitude = float(lat)
            except ValueError:
                pass

        if lng:
            try:
                current_user.longitude = float(lng)
            except ValueError:
                pass

        db.session.commit()
        flash('आपकी प्रोफ़ाइल सफलतापूर्वक अपडेट हो गई है!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('profile.html')
