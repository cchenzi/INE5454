import os
import pandas as pd


def prepare_sisacad_data(data_path):
    sisacad = pd.read_json(data_path)

    # A course can have more than one version.
    # For now, we just want the most recent one.
    sisacad = sisacad.drop_duplicates(subset=["course_code"], keep="last")

    exploded = sisacad.explode("optatives", ignore_index=True)
    sisacad = exploded.join(pd.DataFrame(pd.json_normalize(exploded["optatives"])))

    return sisacad[
        ["course_name", "course_code", "version_code", "class_code", "class_name"]
    ]


def prepare_cagr_data(data_path):
    cagr = pd.read_json(data_path)

    exploded = cagr.explode("subjects", ignore_index=True).dropna(subset=["subjects"])
    cagr = exploded.join(pd.DataFrame(exploded["subjects"].tolist()))

    return cagr[
        [
            "semester",
            "campus",
            "class",
            "total_hours",
            "open_slots",
            "taken_slots",
            "out_slots",
            "schedules",
            "id",
            "professors",
        ]
    ]


def get_optatufsc_data():
    curr_dir = os.path.dirname(__file__)
    sisacad_data_path = os.path.join(curr_dir, "../../../data/sisacad.json")
    cagr_data_path = os.path.join(curr_dir, "../../../data/cagr_total.json")

    sisacad = prepare_sisacad_data(sisacad_data_path)

    cagr = prepare_cagr_data(cagr_data_path)

    optatufsc = cagr.merge(
        right=sisacad, left_on="id", right_on="class_code", how="inner"
    )
    optatufsc = optatufsc[optatufsc["course_code"] == 208]

    optatufsc.to_csv(
        os.path.join(curr_dir, "../../../data/optatufsc_cco2.csv"), index=False
    )


if __name__ == "__main__":
    get_optatufsc_data()
