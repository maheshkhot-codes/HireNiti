import csv

from app.database.database import SessionLocal
from app.applications.models import Application


def build_dataset():

    db = SessionLocal()

    try:

        applications = (
            db.query(Application)
            .all()
        )

        with open(
            "ranking_dataset.csv",
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "candidate_id",
                "job_id",
                "status"
            ])

            for application in applications:

                writer.writerow([
                    str(
                        application.candidate_id
                    ),

                    str(
                        application.job_id
                    ),

                    application.status
                ])

        print(
            f"Created dataset with "
            f"{len(applications)} applications"
        )

    finally:

        db.close()


if __name__ == "__main__":

    build_dataset()