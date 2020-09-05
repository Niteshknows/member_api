from flask import Flask, g, request, jsonify
from database import get_db
from functools import wraps

app = Flask(__name__)

api_username = 'admin'
api_password = 'password'


def auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == api_username and auth.password == api_password:
            return f(*args, **kwargs)
        else:
            return jsonify({'message': 'Authentication Failed'}), 403

    return decorated


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/member', methods=['GET'])
@auth
def get_members():

    db = get_db()
    members_cur = db.execute('select id, name, email, level from members')
    members = members_cur.fetchall()

    result_values = []

    for member in members:
        member_dict = {}
        member_dict['id'] = member['id']
        member_dict['name'] = member['name']
        member_dict['email'] = member['email']
        member_dict['level'] = member['level']

        result_values.append(member_dict)

    return jsonify({'members': result_values})


@app.route('/member/<int:member_id>', methods=['GET'])
@auth
def get_member(member_id):

    db = get_db()
    member_cur = db.execute(
        'select id, name, email, level from members where id = ?', [member_id])
    member = member_cur.fetchone()

    return jsonify({'member': {'id': member['id'], 'name': member['name'], 'email': member['email'], 'level': member['level']}})


@app.route('/member', methods=['POST'])
@auth
def add_member():
    new_member_data = request.get_json()

    name = new_member_data['name']
    email = new_member_data['email']
    level = new_member_data['level']

    db = get_db()
    db.execute('insert into members (name, email, level) values (?,?,?)', [
               name, email, level])
    db.commit()

    member_cur = db.execute(
        'select id, name, email, level from members where name = ?', [name])
    new_member = member_cur.fetchone()

    return jsonify({'member': {'id': new_member['id'], 'name': new_member['name'], 'email': new_member['email'], 'level': new_member['level']}})


@app.route('/member/<int:member_id>', methods=['PUT', 'PATCH'])
@auth
def edit_member(member_id):

    update_member_data = request.get_json()

    name = update_member_data['name']
    email = update_member_data['email']
    level = update_member_data['level']

    db = get_db()
    db.execute('update members set name = ?, email = ?, level = ? where id = ?', [
               name, email, level, member_id])
    db.commit()

    member_cur = db.execute(
        'select id, name, email, level from members where id = ?', [member_id])
    member = member_cur.fetchone()

    return jsonify({'member': {'id': member['id'], 'name': member['name'], 'email': member['email'], 'level': member['level']}})


@app.route('/member/<int:member_id>', methods=['DELETE'])
@auth
def delete_member(member_id):

    db = get_db()

    db.execute('delete from members where id = ?', [member_id])
    db.commit()

    return jsonify({'message': 'The member has been deleted'})


if __name__ == "__main__":
    app.run(debug=True)
