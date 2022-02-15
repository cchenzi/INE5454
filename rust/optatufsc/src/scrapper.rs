use select::{
    document::Document,
    predicate::{Attr, Name, Predicate},
};
use serde::{Deserialize, Serialize};

use crate::subject::{Semester, Subject};

pub const CAGR_URL: &str = "https://cagr.sistemas.ufsc.br/modules/comunidade/cadastroTurmas/";

#[derive(Serialize)]
pub struct RequestForm {
    #[serde(rename = "formBusca")]
    pub form_busca: String,
    #[serde(rename = "javax.faces.ViewState")]
    pub view_state: String,
    #[serde(rename = "formBusca:selectSemestre")]
    pub semester: String,
    #[serde(rename = "formBusca:selectCampus")]
    pub campus: String,
    #[serde(rename = "formBusca:dataScroller1")]
    pub page: String,
}

#[derive(Deserialize, Serialize, Clone, Copy, Debug)]
pub enum Campus {
    FLO = 1,
    JOI = 2,
    CBS = 3,
    ARA = 4,
    BLN = 5,
}

impl Campus {
    pub const VALUES: [Campus; 5] = [
        Campus::FLO,
        Campus::JOI,
        Campus::CBS,
        Campus::ARA,
        Campus::BLN,
    ];
}

pub struct Cagr<'a> {
    pub client: awc::Client,
    pub session_cookie: actix_web::cookie::Cookie<'a>,
}

impl<'a> Cagr<'a> {
    pub async fn new() -> Cagr<'static> {
        let client = awc::Client::new();
        let first_request = client
            .post(CAGR_URL)
            .send()
            .await
            .expect("Unable to perform request to retrieve session cookie");
        let session_cookie = first_request
            .cookie("JSESSIONID")
            .expect("Unable to get session cookie!");
        Cagr {
            client,
            session_cookie,
        }
    }

    pub async fn refresh_cookie(&mut self) {
        let first_request = self
            .client
            .post(CAGR_URL)
            .send()
            .await
            .expect("Unable to perform request to retrieve session cookie");
        let session_cookie = first_request
            .cookie("JSESSIONID")
            .expect("Unable to get session cookie!");
        self.session_cookie = session_cookie;
    }

    pub async fn perform_request(&self, req: &RequestForm) -> String {
        let body = self
            .client
            .post(CAGR_URL)
            .cookie(self.session_cookie.clone())
            .send_form(req)
            .await
            .expect("Unable to read response request!")
            .body()
            .await
            .expect("Unable to get body response as bytes!");
        std::str::from_utf8(&body).unwrap().to_string()
    }

    pub async fn get_n_subject_pages_from_semester(
        &self,
        semester: &str,
        pages: u32,
        campus: &Campus,
    ) -> Vec<Subject> {
        let mut subjects: Vec<Subject> = Vec::new();
        let campus_str = (*campus as u32).to_string();
        for page in 1..(pages + 1) {
            let req = RequestForm {
                form_busca: "formBusca".to_string(),
                view_state: "j_id1".to_owned(),
                semester: semester.to_string(),
                campus: campus_str.clone(),
                page: page.to_string(),
            };
            let body_as_str = self.perform_request(&req).await;
            subjects.extend(subjects_from_page(&body_as_str));
        }
        subjects
    }

    pub async fn get_number_of_pages(&self, semester: String, campus: &Campus) -> u32 {
        let req = RequestForm {
            form_busca: "formBusca".to_string(),
            view_state: "j_id1".to_owned(),
            semester: semester.to_string(),
            campus: (*campus as u32).to_string(),
            page: "2".to_string(),
        };
        let body_as_str = self.perform_request(&req).await;
        number_of_pages(&body_as_str)
    }

    pub async fn get_semesters(&self) -> Vec<String> {
        let req = RequestForm {
            form_busca: "formBusca".to_string(),
            view_state: "j_id1".to_owned(),
            semester: "20221".to_string(),
            campus: "1".to_string(),
            page: "1".to_string(),
        };
        let body_as_str = self.perform_request(&req).await;
        semesters(&body_as_str)
    }
}

pub fn subjects_from_page(html_as_str: &str) -> Vec<Subject> {
    let document = Document::from(html_as_str);
    let subjects_table = document
        .find(Name("tbody").and(Attr("id", "formBusca:dataTable:tb")))
        .next()
        .expect("Unable to get subjects table!");

    subjects_table
        .find(Name("tr"))
        .map(|row| Subject::from_row(&row))
        .collect()
}

pub fn semesters(html_as_str: &str) -> Vec<String> {
    let document = Document::from(html_as_str);
    let subjects_table = document
        .find(Name("select").and(Attr("name", "formBusca:selectSemestre")))
        .next()
        .expect("Unable to get semester selector!");

    subjects_table
        .find(Name("option"))
        .into_iter()
        .map(|node| node.text())
        .collect()
}

pub fn number_of_pages(html_as_str: &str) -> u32 {
    let document = Document::from(html_as_str);
    let total_entries_string = match document
        .find(Name("span").and(Attr("id", "formBusca:dataTableGroup")))
        .next()
        .expect("Unable to get dataTable span!")
        .find(Name("span"))
        .next()
    {
        Some(n) => n.text(),
        None => "0".to_string(),
    };
    let total_entries = match total_entries_string.parse::<u32>() {
        Ok(v) => v,
        Err(_) => 0,
    };
    let pages = total_entries as f32 / 50_f32;
    pages.ceil() as u32
}

pub async fn get_subjects_from_semesters(
    cagr: &mut Cagr<'_>,
    semesters: Vec<String>,
    campus: &Campus,
) -> Vec<Semester> {
    let mut content: Vec<Semester> = Vec::new();
    for semester in semesters {
        cagr.refresh_cookie().await;
        let s = Semester::get_subjects_from_semester(cagr, semester, campus).await;
        content.push(s);
    }
    content
}
