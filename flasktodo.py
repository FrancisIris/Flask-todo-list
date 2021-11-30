from flask import Flask, session, request, url_for, render_template
from datetime import datetime

app = Flask(__name__)
app.secret_key = b'notAGoodSecretKey'
tempKey=""


# Root of the app. We should do at least something here.
@app.route('/')
def view():
    # If the user already has a to-do list, draw it.
    if "todoes" in session:
        if "removed" in session:
            return render_template("todos.html",todos=session["todoes"],added=session["added"],complete=session["complete"],removed=session["removed"])
        else:
            return render_template("todos.html",todos=session["todoes"],added=session["added"])
    else:
        
        # Else, display the new user blank page.
        return render_template("new.html")


# Add task
# Remember, imput from the web is RADIOACTIVE. Validate it like crazy. Then
# validate it some more.
@app.route('/add', methods=["POST"])
def add():
    if "complete" not in session:
        session["complete"]=[]
        complete=[]
    # Just in case a mangled form submission was made
    if "newTask" in request.form:
        # If the user already has todoes, add it..
        if "todoes" in session:
            # We have to do this this way because Flask doesn't properly
            # detect in place updates to members of the session dict
            todoes = session["todoes"]
            todoes.append(request.form["newTask"])
            session["added"] = [request.form["newTask"]]
            session["todoes"] = todoes
            
        else:
            # Make the added task their first todo
            session["todoes"] = [request.form["newTask"]]
            session["added"] = [request.form["newTask"]]

    # If the form was mangled and the user had no todoes before,
    # todoes might still be missing
    if "todoes" not in session:
        return render_template("new.html")
    elif "removed" not in session:
        return render_template("todos.html",todos=session["todoes"],added=session["added"],complete=session["complete"])
    else:
        return render_template("todos.html",todos=session["todoes"],added=session["added"],complete=session["complete"],removed=session["removed"])

# Route for completing a task
@app.route('/complete', methods=["POST"])
def complete():
    # If somehow this got accessed when todoes is blank, bail out.
    if "todoes" not in session:
        return render_template("new.html")

    if "complete" not in session:
        session["complete"]=[]
        complete=[]
    else:
        complete=session["complete"]

    
    # Collect the task numbers to delete by looping through form keys.
    delTaskNums = []
    for key in request.form:
       if key.startswith("complete_"):
           # C O M P L E T E _ is 9 characters, so the rest of the key after
           # that should be the task index
           taskNumString = key[9:]
           # As usual, since web input is radioactive we have to allow for
           # it not being a number or being an invalid number before we
           # try to use it
           try:
               realTaskNum = int(taskNumString)
               if realTaskNum >= 0:
                   if realTaskNum < len(session["todoes"]):
                       delTaskNums.append(realTaskNum)
           except ValueError:
               pass
    # Delete the todoes in reverse order so that the indices of later entries
    # aren't changed by the deletion of earlier entries
    delTaskNums.reverse()

    todoes = session["todoes"]
    removed=[]
    for delTask in delTaskNums:
        removed.append(todoes[delTask])
        cell=[todoes.pop(delTask)]
        cell.append(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        complete.insert(0,cell)
    session["complete"]=complete
    session["todoes"]=todoes
    session["removed"]=removed
    return render_template("todos.html",todos=session["todoes"],added=session["added"],complete=session["complete"],removed=session["removed"])

@app.route('/clear', methods=["POST"])
def clear():
    session["complete"]=[]
    if "todoes" not in session:
        return render_template("new.html")
    elif "removed" not in session:
        return render_template("todos.html",todos=session["todoes"],added=session["added"],complete=session["complete"])
    else:
        return render_template("todos.html",todos=session["todoes"],added=session["added"],complete=session["complete"],removed=session["removed"])
