import os
from datetime import datetime
from nbconvert.filters import markdown2html


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
    # Generate page title
    page_title = f"Section {section_number} Task {task_number}"

    # Generate page contents (markdown to HTML)
    page_contents = markdown2html(question)

    # Generate page filename
    page_filename = f"section_{section_number}_task_{task_number}.html"

    # Create page directory if it doesn't exist
    page_directory = "pages"
    os.makedirs(page_directory, exist_ok=True)

    # Create the new page file
    with open(os.path.join(page_directory, page_filename), "w") as file:
        # Write page title and contents
        file.write(f"<h1>{page_title}</h1>\n\n")
        file.write(page_contents)

        # Add Isso comments section
        file.write("\n\n")
        file.write("<h2>Comments</h2>\n\n")
        file.write(ISSO_CONFIG)

    # Print success message
    print(f"Page created: {os.path.join(page_directory, page_filename)}")

# User inputs
section_number = "2.1"
task_number = "3"
question = '''#### Task 1
Complete the function repetition_encode that when passed a bit string, encodes it according to the repetition code.

Parameters:\message a str, guaranteed to only contain 0 or 1.
Returns:\
A str that is the the encoded version of the message'''


# Create new page with Isso comments
create_new_page(section_number, task_number, question)
