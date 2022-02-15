use select::{node::Node, predicate::Name};
use serde::{Deserialize, Serialize};

use crate::scrapper::{Cagr, Campus};

#[derive(Serialize, Deserialize)]
pub struct Subject {
    pub id: String,
    pub class: String,
    pub total_hours: String,
    pub open_slots: String,
    pub taken_slots: String,
    pub out_slots: String,
    pub schedules: String,
    pub professors: String,
}

impl Subject {
    pub fn from_row(row: &Node) -> Subject {
        let content: Vec<String> = row
            .find(Name("td"))
            .map(|field| field.text().trim().to_string())
            .collect();

        let id = content.get(3).expect("bla").to_string();
        let class = content.get(4).expect("bla").to_string();
        let total_hours = content.get(6).expect("bla").to_string();
        let open_slots = content.get(7).expect("bla").to_string();
        let taken_slots = content.get(8).expect("bla").to_string();
        let out_slots = content.get(11).expect("bla").to_string();
        let schedules = content.get(12).expect("bla").to_string();
        let professors = content.get(13).expect("bla").to_string();

        Subject {
            id,
            class,
            total_hours,
            open_slots,
            taken_slots,
            out_slots,
            schedules,
            professors,
        }
    }
}

#[derive(Serialize, Deserialize)]
pub struct Semester {
    pub semester: String,
    pub campus: Campus,
    pub subjects: Vec<Subject>,
}

impl Semester {
    pub async fn get_subjects_from_semester(
        cagr: &Cagr<'_>,
        semester: String,
        campus: &Campus,
    ) -> Semester {
        let pages = &cagr.get_number_of_pages(semester.clone(), campus).await;
        println!("Doing for {:?}/{}. #pages={}", campus, semester, pages);
        let subjects: Vec<Subject> = cagr
            .get_n_subject_pages_from_semester(&semester, pages.to_owned(), campus)
            .await;

        Semester {
            semester,
            campus: *campus,
            subjects,
        }
    }
}
