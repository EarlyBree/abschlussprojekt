from flask import Flask, redirect, request, render_template, url_for
import queue_handler

# Definieren der App als Flask Applikation
app = Flask(__name__)


# Standardroute /app festlegen
@app.route('/app', methods=['GET', 'POST'])
def index():
    # Checken ob die Queue gerade pausiert ist oder nicht
    queueon = queue_handler.check_queueon()
    # Alle laufenden und abgeschlossenen Prozesse der Queue abfragen
    tasks = queue_handler.queue_handler_function()
    # Die html Datei definieren und die Werte übergeben(ob Queue läuft/pausiert ist und alle tasks)
    return render_template('index.html', queueon=queueon, tasks=tasks)

# Route für den Click auf restart mit Funktion aus dem QueueHandler verknüpfen
@app.route('/restart_queue/')
def restart_queue():
    queue_handler.restart_queue()
    return redirect('/app')

# Route für den Click auf pausieren mit Funktion aus dem QueueHanlder verknüpfen
@app.route('/pause_queue/')
def pause_queue():
    queue_handler.pause_queue()
    return redirect('/app')

# Lässt app nur laufen wenn sie direkt aufgerufen wird
if __name__ == '__main__':
    app.run(debug=True)