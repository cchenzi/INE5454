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

    exploded = cagr.explode("subjects", ignore_index=True)
    cagr = exploded.join(pd.DataFrame(exploded["subjects"].tolist()))

    return cagr[
        [
            "semester",
            "class",
            "total_hours",
            "open_slots",
            "taken_slots",
            "out_slots",
            "schedules",
            "id",
        ]
    ]


def get_optatufsc_data():
    sisacad_data_path = "../../data/sisacad.json"
    cagr_data_path = "../../data/cagr.json"

    sisacad = prepare_sisacad_data(sisacad_data_path)

    cagr = prepare_cagr_data(cagr_data_path)

    optatufsc = cagr.merge(
        right=sisacad, left_on="id", right_on="class_code", how="inner"
    )
    optatufsc = optatufsc[optatufsc["course_code"] == 208]

    optatufsc.to_csv("../../data/optatufsc_cco.csv", index=False)


if __name__ == "__main__":
    get_optatufsc_data()
