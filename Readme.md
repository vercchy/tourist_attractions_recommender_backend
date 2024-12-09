1. Clone the repository locally
2. Cd into the root of the project and Set up a python virtual environment
3. Activate the virtual environment (.\env\Scripts\activate)
3. Install the required dependencies by running "pip install -r requirements.txt", or simply open the file in PyCharm and click on the suggestion for installing all dependencies
4. Create the .env file in the root of the project, and text me to send you the contents of .env file
5. You would need to download the zipped database and load it into pgAdmin4, and make sure you use the exact same credentials, and have it running on the same port, or change these in the app/db/session.py file
6. You would also need to download Redis locally (https://github.com/tporadowski/redis/releases)
7. Download the zipped folder, unzip it, cd into it, and run redis-server.exe redis.windows.conf
8. Before running the application locally always make sure you have redis running in the background, achievable by following the previous step
9. Visit GloVe's site https://nlp.stanford.edu/projects/glove/ and download glove.6B.zip, unzip it, then copy the glove.6B.100d file in the unzipped directory and paste it in the folder ml-models under the exact same name (glove.6B.100d)
10. Now before running the application for the first time, and then only, manually run the script precompute_embeddings.py located in the scripts folder.
12. For this script to succeed, redis has to be running in the background on the proper default port, and you need to have the txt file placed in ml-models folder, so it's necessary to follow the previous steps.
13. You would probably need to run this script only once, but if the redis 0 db contents get deleted after you shut down your PC you would need to run it again before starting the application
14. If you run it for a second time, and any other subsequent time, make sure you first delete the automatically generated file embeddings.pkl in the scripts folder.
That should be it :)
