from flask import Flask, render_template, request, redirect
from nbconvert.filters import markdown2html
import os


app = Flask(__name__)

ISSO_CONFIG = """
<div id="isso-thread"></div>
<script src="//localhost:8017/js/embed.min.js"></script>
<script>
    var issoConfig = {
        'host': 'http://localhost:8017/',
        'target': 'isso-thread',
        'thread': '{{ request.path }}',
    };
</script>
"""

# Function to create a new page with Isso comments
def create_new_page(section_number, task_number, question):
    page_title = f"Section {section_number} Task {task_number}"

    page_contents = markdown2html(question)

    page_filename = f"section_{section_number}_task_{task_number}.html"

    page_directory = "templates"
    os.makedirs(page_directory, exist_ok=True)

    with open(os.path.join(page_directory, page_filename), "w") as file:
        file.write(f"<h1>{page_title}</h1>\n\n")
        file.write(page_contents)

        # Add Isso comments section
        file.write("\n\n")
        file.write("<h2>Comments</h2>\n\n")
        file.write(ISSO_CONFIG)

    return page_filename


@app.route("/", methods=["GET", "POST"])
def create_page():
    if request.method == "POST":
        section_number = request.form.get("section_number")
        task_number = request.form.get("task_number")
        question = request.form.get("question")

        page_filename = create_new_page(section_number, task_number, question)

        return redirect(f"/comments/{page_filename}")

    return render_template("index.html")


@app.route("/comments/<path:name>")
def view_comments(name):
    return render_template(f"{name}")


if __name__ == "__main__":
    app.run(debug=True)
