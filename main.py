# main.py

from processors.regression_progress_updater import RegressionProgressUpdater

if __name__ == "__main__":
    updater = RegressionProgressUpdater()
    updater.update_progress()
