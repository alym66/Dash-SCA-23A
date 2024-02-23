import sqlite3 as sq
from datetime import datetime


async def db_start():
    global db, cur
    db = sq.connect('tg.db')
    cur = db.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS staff("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "full_name TEXT,"
                "about TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS project("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "name TEXT,"
                "description TEXT,"
                "performers TEXT,"
                "department TEXT,"
                "complete TEXT,"
                "deadline DATE)")
    db.commit()


async def add_staff(state):
    async with state.proxy() as data:
        cur.execute("INSERT INTO staff (full_name, about) VALUES (?, ?)",
                    (data['full_name'], data['about']))
        db.commit()


async def add_project(state):
    async with state.proxy() as data:
        cur.execute("INSERT INTO project (name, description, performers, department, complete, deadline) VALUES (?, ?, ?, ?, ?, ?)",
                    (data['name'], data['description'], data['performers'], data['department'], data['complete'], data['deadline']))
        db.commit()


async def show_staff(message):
    cur.execute("SELECT id, full_name, about FROM staff")
    staff = cur.fetchall()
    if staff:
        for member in staff:
            id, full_name, about = member
            member_info = (f'''ID сотрудника: {id}
        
Имя и фамилия: {full_name}
Область: {about}''')
            await message.answer(member_info)
    else:
        await message.answer('Сотрудников не найдено')

    db.commit()


async def show_projects(message):
    if message.text in ['Digitals', 'Education', 'Commerce']:
        department = message.text

        cur.execute(
            f"SELECT id, name, description, performers, complete, deadline FROM project where department = '{department}'")
        projects = cur.fetchall()

        if projects:
            for project in projects:
                id, name, description, performers, complete, deadline = project
                formatted_deadline = str(deadline)[:10]


                project_info = (f'''ID Проекта: {id}
*Название: {name}*

Описание: {description}

Выполняют: {performers}
-----------------------
Завершенность: {complete}%
Дедлайн: {formatted_deadline}''')
                await message.answer(project_info, parse_mode="Markdown")
        else:
            await message.answer(f"Не найдено проектов для отдела {department}.")

    db.commit()


async def update_project_field(project_id, field, new_value):
    cur.execute(f"UPDATE project SET {field} = ? WHERE id = ?", (new_value, project_id))
    db.commit()


async def get_staff_names():
    cur.execute("SELECT full_name FROM staff")
    rows = cur.fetchall()
    return [row[0] for row in rows]


async def delete_project(project_id):
    cur.execute("DELETE FROM project WHERE id = ?", (project_id,))
    db.commit()

async def delete_staff(staff_id):
    cur.execute("DELETE FROM staff WHERE id = ?", (staff_id,))
    db.commit()

async def check_project_exists(project_id):
    cur.execute("SELECT COUNT(*) FROM project WHERE id = ?", (project_id,))
    count = cur.fetchone()[0]
    return count > 0

async def check_staff_exists(staff_id):
    cur.execute("SELECT COUNT(*) FROM staff WHERE id = ?", (staff_id,))
    count = cur.fetchone()[0]
    return count > 0

