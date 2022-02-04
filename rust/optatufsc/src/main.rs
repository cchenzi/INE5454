use std::{fs::File, io::BufWriter};

use optatufsc::scrapper::Cagr;

#[actix_web::main]
async fn main() {
    let mut cagr = Cagr::new().await;

    let semesters: Vec<String> = cagr.get_semesters().await.into_iter().take(4).collect();

    let content =
        optatufsc::scrapper::get_subjects_from_semesters(&mut cagr, semesters.to_vec()).await;

    let file_name = "cagr.json";

    let writer = BufWriter::new(File::create(file_name).unwrap());
    serde_json::to_writer_pretty(writer, &content).expect("Unable to save results");
}
