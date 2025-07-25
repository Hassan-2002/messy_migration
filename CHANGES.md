The inhertied legacy user managment system API runs and each end point has been tested for displaying, creating, selecting, deleting and searchign Users.


The primary changes include 
-Seperation of concerns and proper structuring
          In the legacy version, the routes and controllers were both defined in the app/py file.
          In the new version all these seperate concerns have been modularised into seperate files for easier debugging and maintainence.
          These are the file the app has been modularised into :
          1. App.py
          2. Routes.py3
          3.
