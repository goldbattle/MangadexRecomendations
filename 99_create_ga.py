import yaml  # pip install PyYAML
import os
import shutil

# static should not change
hours_in_a_week = 24 * 7
export_folder = ".github/workflows/"

# main parameters needed
hours_between = 4
max_manga_id = 65000
num_to_run = round(max_manga_id / (hours_in_a_week / hours_between))

# assert that we will be able to get all mangas in this time period
hours_to_complete = hours_between * round(max_manga_id / num_to_run)
if hours_to_complete > hours_in_a_week:
    print("ERROR: not enough hours in a week to complete...")
    print("\t- hours_to_complete =  " + str(hours_to_complete))
    print("\t- hours_in_a_week =  " + str(hours_in_a_week))
    exit(-1)

# we are good so lets start to loop through each week
print("we will be able to update all mangas:")
print("\t- hours_between =  " + str(hours_between))
print("\t- max_manga_id =  " + str(max_manga_id))
print("\t- num_to_run =  " + str(num_to_run))
print("\t- hours_to_complete =  " + str(hours_to_complete))
print("\t- hours_in_a_week =  " + str(hours_in_a_week))

# delete old files
if os.path.exists(export_folder):
    shutil.rmtree(export_folder)
os.makedirs(export_folder)

# create all the configuration yaml files
current_manga_id = 1
current_hour_of_week = 0
while current_manga_id < max_manga_id:
    # calculate what day and time in that we we will have
    day = int(current_hour_of_week / 24)
    hour = current_hour_of_week - day * 24
    assert (day < 7)
    assert (hour < 23)
    print("creating " + str(day) + " at hour " + str(hour))

    # our github action format
    config = {
        "name": "mangas " + str(current_manga_id) + " - " + str(current_manga_id + num_to_run),
        "on": {
            "schedule": [{
                "cron": "0 " + str(hour) + " * * " + str(day)
            }]
        },
        "jobs": {
            "build": {
                "runs-on": "ubuntu-latest",
                "timeout-minutes": 360,
                "steps": [
                    {
                        "uses": "actions/checkout@v2"
                    },
                    {
                        "name": "Set up Python 3.8",
                        "uses": "actions/setup-python@v1",
                        "with": {"python-version": 3.8},
                    },
                    {
                        "name": "Install dependencies",
                        "run": "python -m pip install --upgrade pip && pip install requests bs4 scikit-learn",
                    },
                    {
                        "name": "Pull latest manga information",
                        "run": "python 01_scrape_mangas.py " + str(current_manga_id) + " "
                               + str(current_manga_id + num_to_run),
                    },
                    {
                        "name": "Calculate similar mangas",
                        "run": "python 02_calc_similarities.py " + str(current_manga_id) + " "
                               + str(current_manga_id + num_to_run),
                    },
                    {
                        "name": "Commit changed files",
                        "run": "git config --local user.email \"action@github.com\" && "
                               "git config --local user.name \"GitHub Action\" && "
                               "git commit -m \"Updated Manga " + str(current_manga_id) + " - "
                               + str(current_manga_id + num_to_run) + "\" -a ",
                    },
                    {
                        "name": "Push changes to master branch",
                        "uses": "ad-m/github-push-action@master",
                        "with": {"github_token": "${{ secrets.GITHUB_TOKEN }}"},
                    },
                ]
            }
        },
    }

    # save to file
    file = export_folder + str(day) + "_" + format(hour, '02') + ".yaml"
    with open(file, 'w') as file:
        yaml.dump(config, file, sort_keys=False)

    # move forward in time
    current_manga_id = current_manga_id + num_to_run
    current_hour_of_week = current_hour_of_week + hours_between
