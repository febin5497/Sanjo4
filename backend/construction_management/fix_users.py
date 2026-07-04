from app import create_app
from extensions import db, bcrypt
app = create_app()
with app.app_context():
    from models_loader import User
    for user in User.query.all():
        pw = user.username.replace('_test', '').replace('STF-', '')
        if pw in ('demo', 'admin', 'staffone', 'stafftwo'):
            pw = pw
        user.password = bcrypt.generate_password_hash(pw).decode()
        print(f'  {user.username}: password = {pw}')
    db.session.commit()
    print('\nDone! Passwords set.')
