Chess Tracker

Description:

Chess Tracker is a web application I built as my CS50x final project. It's a personal tool for logging my own chess games and automatically seeing how I'm actually performing — my overall win rate, how I do playing white versus black, and which openings are actually working for me. I play chess casually and wanted something better than just remembering vague impressions of "I think I do better with this opening" — I wanted real numbers pulled from real games I'd logged myself.

The project is built with Flask and Python on the backend, SQLite for the database (via CS50's own SQL library), Jinja for templating, and plain HTML, CSS, and JavaScript on the frontend — no frontend frameworks like Bootstrap or React. I deliberately wrote all the CSS myself instead of using a framework, because I wanted full control over the design and because it forced me to actually understand what I was building rather than just applying pre-made classes. The one exception is Chart.js, which I used for the rating-over-time chart on the Progress page, since building a charting library from scratch was well outside the scope of this project.

Features

A user registers with a username and password. Passwords are hashed with Werkzeug's generate_password_hash before being stored — the raw password is never saved anywhere. I also added a regex check requiring a minimum length of 8 characters.

Once logged in, the home page (/) shows three summary cards: overall win rate, win rate with white, and win rate with black, each calculated live from the games table using SQL COUNT queries. Below that is a table breaking down win rate by opening. I made a specific design decision here to only show an opening once it's been played at least three times — with only one or two games logged, a "100% win rate" or "0% win rate" for an opening is statistically meaningless and would be misleading rather than useful. All of these win rate calculations are wrapped in try/except blocks so that a brand new user with zero games logged doesn't crash the page with a division-by-zero error — they just see 0% until they've logged something.

The Add Game page (/add) lets me log a new game: the color I played, the result (win, loss, or draw), the opening name, my opponent's rating, my own rating at the time, and the date. I validate all of this server-side — checking the color and result are from an allowed list, that both ratings are actually valid integers, and that the date is a real, correctly formatted date using Python's datetime.strptime.

The History page (/history) lists every game I've logged in a table, most recent first, with an Edit and a Delete action on each row. Edit takes me to a pre-filled form (/edit/<id>) where every field already shows the game's current values, including the correct dropdown option pre-selected for color and result. Delete removes a game immediately — this is deliberately implemented as a small POST-only form rather than a plain link, since a GET request shouldn't be able to trigger a destructive action like deleting data. Both Edit and Delete check that the game actually belongs to the logged-in user before making any changes, so one user can never modify or delete another user's data, even if they somehow guessed another game's ID.

The Progress page (/progress) is a line chart, built with Chart.js, plotting my rating over time based on every game I've logged. I originally considered putting this chart directly on the home dashboard, but decided against it — the dashboard already had three stat cards plus an opening breakdown table, and adding a chart on top of that felt visually crowded. Giving the chart its own dedicated page let it be properly sized and readable instead of squeezed into an already busy layout.

Files

app.py contains the entire Flask backend — every route, all the validation logic, and every SQL query. chess.db is the SQLite database, with two tables: users (id, username, hashed password) and games (id, a foreign key linking to the user who logged it, date, color, result, opening, opponent rating, and my own rating at the time). I store the rating on every single game individually, rather than only saving some kind of average, specifically so that the Progress chart could plot it over time — averaging first would have thrown away the information needed for a trend line.

The templates/ folder holds every Jinja template. layout.html is the shared base template that every other page extends — it holds the navigation bar (which changes depending on whether you're logged in) and the overall page structure. register.html and login.html handle authentication. home.html is the dashboard. add.html, edit.html, and history.html handle the actual game-logging CRUD. apology.html is a simple shared error page. progress.html holds the Chart.js visualization.

static/styles.css contains every style rule for the whole site. I built a small design system using CSS custom properties (:root variables) for my color palette — a dark brown and cream, chess-board-inspired theme — and reusable classes like .card, .input, and .button so that every page automatically looks consistent without me rewriting the same styles over and over.

requirements.txt lists every Python package the project depends on (Flask, Flask-Session, cs50, python-dotenv, Werkzeug, and their sub-dependencies), so the project can be set up identically on another machine with pip install -r requirements.txt.

Design decisions

I built and tested this project entirely on my own computer rather than in the CS50 Codespace, after running into repeated networking and certificate errors trying to preview Flask apps through the Codespace's port forwarding. Working locally with a Python virtual environment turned out to be more reliable, and it also meant the project was portable from day one rather than tied to CS50's infrastructure.

I also deliberately kept this project separate from a bigger machine learning project I'm planning to build later — a chess win-probability predictor trained on a large public dataset of Lichess games. That's a fundamentally different kind of project, built on different data, with a different goal. Trying to force both into one codebase from the start would have meant either over-engineering this tracker with speculative "future ML" code paths I didn't need yet, or under-building the ML side. Keeping them separate let me build this project properly as what it actually is: a personal stats tracker, not a machine learning pipeline.
