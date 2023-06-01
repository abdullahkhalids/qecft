Commenting System using Isso
To set up and run the commenting system with Isso, follow these steps:

Start the Flask server by running the following command in your terminal or command prompt:

```bash
python app.py
```
This will start the Flask server and make your website accessible.

Next, start the Isso server. Run the following command in your terminal or command prompt:

```bash
Copy code
isso -c isso.cfg run
```
This command starts the Isso server using the provided configuration file (isso.cfg).

The Isso server is now running and ready to handle comments. You can visit the host website and test the commenting functionality by leaving comments on the pages.

The dbpath option is set to isso.db, which means the Isso database will be stored in the current directory.

Note: Ensure that the Isso server has write permissions in the current directory to create and access the database file.
