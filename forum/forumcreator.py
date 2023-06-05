import os
from flask import Flask, render_template, request, render_template_string
from nbconvert.filters import markdown2html

app = Flask(__name__, template_folder='./')

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
    page_directory = "solutions"
    os.makedirs(page_directory, exist_ok=True)
    
    content = f"<h3>Comments</h3>{ISSO_CONFIG}"
    
    with open(os.path.join(page_directory, page_filename), "w") as file:
        file.write(HTML_HEADER)
        file.write(f"<h1>{page_title}</h1>\n\n")
        file.write(page_contents)
        file.write(content)
        file.write(HTML_FOOTER)

    markdown_string = f"[Discussion](https://abdullahkhalid.com/qecft/solutions/{page_filename})"

    return page_filename, markdown_string


@app.route("/", methods=["GET", "POST"])
def create_page():
    if request.method == "POST":
        section_number = request.form.get("section_number")
        task_number = request.form.get("task_number")
        question = request.form.get("question")
        page_filename, markdown_string = create_new_page(section_number, task_number, question)
        link_output = f"/solutions/{page_filename}"
        return render_template("createpage/index.html", markdown_output=markdown_string, link_output=link_output)

    return render_template("createpage/index.html")

@app.route("/solutions/<path:name>")
def view_comments(name):
    return render_template(f'solutions/{name}')

if __name__ == '__main__':
    app.run(host='localhost', port=8000)
