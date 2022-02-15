use std::{fs::File, io::BufWriter};

use optatufsc::{
    scrapper::{Cagr, Campus},
    subject::Semester,
};

#[actix_web::main]
async fn main() {
    let mut cagr = Cagr::new().await;
    let mut content: Vec<Semester> = Vec::new();

    let semesters: Vec<String> = cagr.get_semesters().await.into_iter().take(16).collect();
    for campus in Campus::VALUES {
        let data = optatufsc::scrapper::get_subjects_from_semesters(
            &mut cagr,
            semesters.to_vec(),
            &campus,
        )
        .await;
        content.extend(data);
    }

    let file_name = "cagr_total.json";
    let writer = BufWriter::new(File::create(file_name).unwrap());
    serde_json::to_writer_pretty(writer, &content).expect("Unable to save results");
}
