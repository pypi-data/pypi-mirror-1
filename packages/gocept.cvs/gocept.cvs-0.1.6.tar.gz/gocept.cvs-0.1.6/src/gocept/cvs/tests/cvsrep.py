import os
import subprocess
import tempfile


class CVSTestRepository(object):

    def __init__(self, dirname="testrepos"):
        self.name = dirname
        self.cvsrep_path = tempfile.mkdtemp()
        self.projects = {}

    def import_project(self, projectpath, name):
        """Imports the project given by path to the repository."""
        if not os.path.exists(projectpath):
            return ValueError("Given projectpath is not accessable.")
        if not os.getenv("CVSROOT"):
            os.putenv("CVSROOT", self.cvsrep_path)

        os.chdir(projectpath)
        logmessage = "Initial testimport."
        commandlist = ["cvs", "import", "-m '%s'" % logmessage,
                       name, "HEAD", "test"]
        subprocess.Popen(
            commandlist, stdout=subprocess.PIPE).communicate()
        self.projects[name] = projectpath

    def create_testproject(self):
        """Creates a test project."""
        testproject_path = os.path.join(os.path.dirname(__file__),
                                        "testdata")
        self.import_project(testproject_path, "gocept.test")

    def create(self):
        """Creates and initializes the cvs repository."""
        os.putenv("CVSROOT", self.cvsrep_path)
        subprocess.Popen(["cvs", "init"],
                         stdout=subprocess.PIPE).communicate()

