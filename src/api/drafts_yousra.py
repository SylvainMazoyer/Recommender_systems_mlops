import csv

def create_fichier2():
    unique_user_ids = set()

    with open("../../data/ratings.csv", mode='r', newline='', encoding='utf-8') as csv_file_1:
        csv_reader_1 = csv.DictReader(csv_file_1)

        # Open fichier2.csv in write mode ('w')
        with open("../../data/users.csv", mode='w', newline='', encoding='utf-8') as csv_file_2:
            fieldnames = ['userId', 'name']
            csv_writer = csv.DictWriter(csv_file_2, fieldnames=fieldnames)
            csv_writer.writeheader()

            # Iterate over rows in fichier1.csv
            for row in csv_reader_1:
                # Extract userId from each row
                userId = row['userId']
                if userId not in unique_user_ids:

                    # Construct the name by concatenating 'user' and userId
                    name = f"user_{userId}"

                    # Write id and name to fichier2.csv
                    csv_writer.writerow({'userId': userId, 'name': name})
                    unique_user_ids.add(userId)

create_fichier2()