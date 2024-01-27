import json
import shutil
import sys
from collections import defaultdict

from git import Repo

from file_analizer import analyze_spotbugs_results
from spotbugs import spotbugs, spotbugs_bin
from utils import *


def clean():
    try:
        shutil.rmtree(PROJECT_PATH, ignore_errors=True)
        os.remove(XML_FILE_NAME)
        shutil.rmtree(RESULTS_PATH, ignore_errors=True)
    except Exception as e:
        pass


def menu():
    print("\n1. START ANALIZING GROOVY")
    print("2. EXTRACT FINAL RESULTS")
    print("3. SEE FINAL RESULTS")
    print("0. EXIT")
    user_input = str(input("-: "))
    if user_input == '1':
        clean()
        analyze()
    elif user_input == '2':
        get_result()
        menu()
    elif user_input == '3':
        see_results()
        menu()
    elif user_input == '0':
        print('Closing...')
        sys.exit(0)
    else:
        print('Invalid input')
        menu()


def analyze():
    print("\nDownloading groovy repository...")
    bug_categories_counter = defaultdict(int)
    file_bug_count = defaultdict(int)
    repo = Repo.clone_from(LINK_TO_REPO, PROJECT_PATH)
    print("Done")

    master_branch = repo.branches["master"]
    commit_iter = list(repo.iter_commits(master_branch.commit, reverse=True))
    total_commits = len(commit_iter)
    start_from = 1500
    end_to = total_commits

    print("\nDISCLAIMER: FIRST 1500 commits are empty")
    print(f"DISCLAIMER: The repository has {total_commits} commits\n")
    user_input = str(input("Do you want to choose a range of commits to analyze? Yes/No: ")).lower()
    if user_input == 'y' or user_input == 'yes':
        start_from = int(input("Start from commit: "))
        end_to = int(input("End to commit: "))

        if (start_from < 0 or end_to > total_commits) or start_from > end_to:
            print('Invalid input')
            menu()
            return
    elif user_input == 'n' or user_input == 'no':
        print(f"Analyzing all repository commits")
    else:
        print('Invalid input')
        menu()
        return

    user_input = str(input("\nWanna see full log? Yes/Anything else: ")).lower()
    if user_input == 'y' or user_input == 'yes':
        param = ""
    else:
        param = "> /dev/null 2>&1"

    current_commit = start_from
    exception_num = 0
    commit_iter = commit_iter[(start_from - 1):end_to]

    for commit in commit_iter:
        try:
            print(f"Analyzing commit {current_commit}/{total_commits}")
            repo.git.checkout(commit.hexsha, force=True)

            if not check_jdk_is_installed():
                download_and_extract_java()
            set_environment_variables()

            analisi_done = spotbugs(param)
            if analisi_done:
                bug_categories_counter = defaultdict(int)
                file_bug_count = defaultdict(int)

                bug_categories_counter, file_bug_count = analyze_spotbugs_results(XML_FILE_NAME, bug_categories_counter,
                                                                                  file_bug_count)
                if len(bug_categories_counter) == len(file_bug_count) == 0:
                    exception_num += 1
                else:
                    os.makedirs(RESULTS_PATH, exist_ok=True)
                    path = f"{current_commit}"
                    current_result_dir = os.path.join(RESULTS_PATH, str(current_commit))
                    os.makedirs(os.path.join(RESULTS_PATH, path), exist_ok=True)

                    with open(os.path.join(current_result_dir, f"{CATEGORIES_FILENAME}"), 'w') as file:
                        json.dump(bug_categories_counter, file)

                    with open(os.path.join(current_result_dir, f"{BUGCOUNT_FILENAME}"), 'w') as file:
                        json.dump(file_bug_count, file)
                current_commit += 1
            else:
                current_commit += 1
                raise Exception()
        except Exception:
            print(f"Can't build commit {current_commit - 1}")

    print("\nAnalysis finished")
    bug_categories_counter, file_bug_count = get_result()
    if len(bug_categories_counter) == 0 and len(file_bug_count) == 0:
        print("No bug found, maybe an error occured during the builds")
    else:
        print(f"TOTAL BUGS IN COMMITS {start_from}-{end_to} FOR CATEGORY:\n")
        print(row for row in bug_categories_counter)
        print(f"\nTOTAL BUGS IN COMMITS {start_from}-{end_to} FOR FILE:\n")
        print(row for row in file_bug_count)


def see_results():
    category_bug = defaultdict(int)
    file_bug = defaultdict(int)
    if os.path.exists(FINAL_RESULT_PATH):
        with open(os.path.join(FINAL_RESULT_PATH, RESULT_CATEGORIES), 'r', encoding='utf-8') as f:
            data = json.load(f)
            for category, num_of_bugs in data.items():
                category_bug[category] += num_of_bugs

        with open(os.path.join(FINAL_RESULT_PATH, RESULT_FILE_COUNT), 'r', encoding='utf-8') as f:
            data = json.load(f)
            for category, num_of_bugs in data.items():
                file_bug[category] += num_of_bugs

        user_input = int(input("Do you want to see:\n1. All results\n2. Only the top 5?\n:-"))
        if user_input == 1:
            start_category = 0
            end_category = len(category_bug)
            start_file = 0
            end_file = len(file_bug)
        elif user_input == 2:
            start_category = 0
            end_category = 5
            start_file = 0
            end_file = 5
        else:
            print("Wrong input.")
            return

        category_bug = list(category_bug.items())[start_category:end_category]
        file_bug = list(file_bug.items())[start_file:end_file]
        print("\nTOTAL NUMBER OF BUGS FOR CATEGORY:")
        for category, num_of_bugs in category_bug:
            print(f"{category}: {num_of_bugs}")

        print("\nTOTAL NUMBER OF BUGS FOR FILE:")
        for file, num_of_bugs in file_bug:
            print(f"{file}: {num_of_bugs}")
    else:
        print("\nNO RESULTS FOUND\n")
        menu()


def get_result():
    try:
        somma_categorie_bug = defaultdict(int)
        somma_file_bug = defaultdict(int)

        # Ricerca ricorsiva dei file JSON nelle sottocartelle
        for dirpath, _, filenames in os.walk(RESULTS_PATH):
            for filename in filenames:
                if filename == CATEGORIES_FILENAME:
                    path_bug_categories = os.path.join(dirpath, filename)
                    with open(path_bug_categories, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        for categoria, numero_bug in data.items():
                            somma_categorie_bug[categoria] += numero_bug

                elif filename == BUGCOUNT_FILENAME:
                    path_file_bug_count = os.path.join(dirpath, filename)
                    with open(path_file_bug_count, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        for nome_file, numero_bug in data.items():
                            somma_file_bug[nome_file] += numero_bug

        # Ordinamento in ordine decrescente
        sorted_categories = dict(sorted(somma_categorie_bug.items(), key=lambda x: x[1], reverse=True))
        sorted_file_counts = dict(sorted(somma_file_bug.items(), key=lambda x: x[1], reverse=True))

        # Salvataggio dei risultati in nuovi file JSON
        os.makedirs(FINAL_RESULT_PATH, exist_ok=True)
        with open(os.path.join(FINAL_RESULT_PATH, RESULT_CATEGORIES), 'w', encoding='utf-8') as output_cat_file:
            json.dump(sorted_categories, output_cat_file, indent=2)

        with open(os.path.join(FINAL_RESULT_PATH, RESULT_FILE_COUNT), 'w', encoding='utf-8') as output_file_file:
            json.dump(sorted_file_counts, output_file_file, indent=2)

        print("Results extracted successfully")
        return sorted_categories, sorted_file_counts
    except Exception as e:
        print("\nNO DATA FOUND\n", e)
        menu()


if __name__ == '__main__':
    menu()
