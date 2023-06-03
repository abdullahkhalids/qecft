import os
from flask import Flask, render_template, request, redirect
from nbconvert.filters import markdown2html


app = Flask(__name__)

ISSO_CONFIG = """
<div id="isso-thread"></div>

<script src="//localhost:8017/js/embed.min.js"></script>
<script>
    var issoConfig = {
        // Isso server endpoint
        'host': 'http://localhost:8017/',
        'target': 'isso-thread',
        'thread': '{{ request.path }}',
    };
</script>
"""

HTML_HEADER = """
<!DOCTYPE html>
<html>
<head>
    <title>Task Forum</title>
</head>
<body>
"""

HTML_FOOTER = """
</body>
</html>
"""

def create_new_page(section_number, task_number, question):
    page_title = f"Section {section_number} Task {task_number}"

    page_contents = markdown2html(question)

    page_filename = f"section_{section_number}_task_{task_number}.html"

    page_directory = "templates"
    os.makedirs(page_directory, exist_ok=True)
    content = f"<h3>Comments</h3>{ISSO_CONFIG}"
    with open(os.path.join(page_directory, page_filename), "w") as file:
        file.write(HTML_HEADER)
        file.write(f"<h1>{page_title}</h1>\n\n")
        file.write(page_contents)
        # adding Isso comment section
        file.write(content)
        file.write(HTML_FOOTER)

    return page_filename


@app.route("/", methods=["GET", "POST"])
def create_page():
    if request.method == "POST":
        section_number = request.form.get("section_number")
        task_number = request.form.get("task_number")
        question = request.form.get("question")

        page_filename = create_new_page(section_number, task_number, question)

        return redirect(f"/comments/{page_filename}")

    # clearing the cache
    template_directory = "templates"
    for filename in os.listdir(template_directory):
        file_path = os.path.join(template_directory, filename)
        if filename != "index.html":
            os.remove(file_path)

    return render_template("index.html")


@app.route("/comments/<path:name>")
def view_comments(name):
    return render_template(name)


if __name__ == '__main__':
    app.run(host='localhost', port=8000)
