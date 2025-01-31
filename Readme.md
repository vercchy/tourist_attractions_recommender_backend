1. Clone the repository locally (Make sure you have python version 3.12.* https://www.python.org/downloads/release/python-3123/ (Ideally 3.12.3)), to avoid troubles with dependencies.
2. At the root of the project set up a virtual environment.
3. Activate the virtual environment (.\env\Scripts\activate).
3. Install the required dependencies by running "pip install -r requirements.txt".
4. Create the .env file in the root of the project, it should contain a secret key.
5. Download the database and load it in pgAdmin4, and change the database connection settings accordingly in the app/db/session.py file.
6. Download Redis In-Memory Database (https://github.com/tporadowski/redis/releases)
7. Unzip the folder, enter it, and run redis-server.exe redis.windows.conf.
8. Before running the application locally always make sure you have redis running in the background, achievable by following the previous step.
9. Visit GloVe's site https://nlp.stanford.edu/projects/glove/ and download glove.6B.zip, unzip it, then copy the glove.6B.100d file from the unzipped directory and paste it in the folder ml-models under the exact same name (glove.6B.100d).
10. Before running the application for the very first time, manually run the script precompute_embeddings.py located in the scripts folder.
12. For this script to succeed, redis has to be running in the background on the proper default port, and you need to have the txt file placed in ml-models folder, so it's necessary to follow the previous steps.
13. The script often needs to be ran once. In case redis 0 db contents get deleted, after PC shutdown, do it again.
