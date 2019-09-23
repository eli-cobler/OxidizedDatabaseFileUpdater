#
#  main.py
#  MikrotikBackup
#
#  Created by Eli Cobler on 11/18/18.
#  Copyright © 2018 Eli Cobler. All rights reserved.
#
#  This project allows you to add and remove routers to your Oxidized Router database file.
#
#  Runs the main flask app.

from flask import Flask, render_template, redirect, request, abort, send_file, flash, url_for
import os, sys
current_directory = os.getcwd()
sys.path.insert(1,current_directory.replace('/mikrotik_backup',''))

import mikrotik_backup.services.backup as backup
import mikrotik_backup.services.database as database
import mikrotik_backup.services.add_file as add_file

app = Flask(__name__)
app.secret_key = 'some_secret'

@app.route('/', methods=['GET', 'POST'])
def index():
    router_list = database.get()
    routers = []
    for item in router_list:
        data = item.split(':')
        routers.append(data[0])

    routers_dict = {}
    for item in router_list:
        data = item.split(':')
        routers_dict[data[0]] = [data[1], data[2], data[3], data[4], data[5], data[6],data[7]]    

    return render_template('home/index.html', routers=routers_dict)

# takes input form from user to add needed info to the database file
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':                    
        name = request.form['name']
        router_ip = request.form['router_ip']
        username = request.form['username']
        password = request.form['password']

        exists = database.add(name, router_ip, username, password)
        add_file.autoUpdater(name, router_ip, username, password)
        add_file.ssh_key(username, password, router_ip)

        if exists:
            flash("This has already be Added or the folder already exists in backups directory.")
        else:
            return redirect(url_for('index'))

    return render_template('home/add.html')

# allows user to select which location to remove viva dropdown menu
@app.route('/remove', methods=['GET', 'POST'])
def remove():
    router_list = database.get()
    routers = []
    for item in router_list:
        data = item.split(':')
        routers.append(data[0])
        routers.sort()

    if request.method == 'POST':
        router_to_remove = request.form.get('selected router')
        database.complete_removal(router_to_remove)
        return redirect(url_for('index'))
    
    return render_template('home/remove.html', routers=routers)

# allows users to update already existing routers in the database file
# I know there is a more pythonic way to do this but for now it works ¯\_(ツ)_/¯
@app.route('/update', methods=['GET', 'POST'])
def update():
    router_list = database.get()
    routers_list = []
    for item in router_list:
        data = item.split(':')
        routers_list.append(data[0])
        router_list.sort()

    routers_dict = {}
    for item in router_list:
        data = item.split(':')
        routers_dict[data[0]] = [data[1], data[2], data[3], data[4]]

    if request.method == 'POST':
        router_to_update = request.form.get('selected router')

        if request.form['name'] == '':
            name = router_to_update
        else:
            name = request.form['name']
        
        if request.form['router_ip'] == '':
            router_ip_list = routers_dict.get(router_to_update)
            router_ip = router_ip_list[0]
        else:
            router_ip = request.form['router_ip']

        if request.form['username'] == '':
            username_list = routers_dict.get(router_to_update)
            username = username_list[1]
        else:
            username = request.form['username']

        if request.form['password'] == '':
            password_list = routers_dict.get(router_to_update)
            password = password_list[2]
        else:
            password = request.form['password']
        
        backup_status = "Not Set"
        config_status = "Not Set"
        backup_date = "Not Set"
        version = "Not Set"

        database.update(name, router_ip, username, password, router_to_update, backup_status, config_status, backup_date, version)
        return redirect(url_for('index'))

    return render_template('home/update.html', routers=routers_list)

@app.route('/run-backup', methods=['GET', 'POST'])
def run_backup():
    if request.method == 'POST':
        backup.run()
    
    return render_template('home/run_backup.html')

@app.route('/single-backup', methods=['GET', 'POST'])
def single_backup():
    router_list = database.get()
    routers = []
    for item in router_list:
        data = item.split(':')
        routers.append(data[0])
    
    if request.method == 'POST':
        router_to_remove = request.form.get('selected router')
        database.complete_removal(router_to_remove)
        return redirect(url_for('index'))
    
    return render_template('home/single_backup.html', routers=routers)

@app.route('/', defaults={'req_path': ''})
@app.route('/<path:req_path>')
def dir_listing(req_path):
    BASE_DIR = os.getcwd()
    
    # Joining the base and the requested path
    abs_path = os.path.join(BASE_DIR, req_path)
    
    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        return send_file(abs_path)

    backup_folder = os.path.basename(req_path)

    # Show directory contents
    files = os.listdir(abs_path)
    files.sort(reverse=True)
    return render_template('home/files.html', files=files, backups=backup_folder)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')