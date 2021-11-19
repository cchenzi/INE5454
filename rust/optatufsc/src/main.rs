use select::{
    document::Document,
    predicate::{Attr, Name, Predicate},
};

#[actix_web::main]
async fn main() {
    // NOTE: This function creates a new internal Client on each call,
    // and so should not be used if making many requests. Create a Client instead.
    let body = reqwest::get("https://cagr.sistemas.ufsc.br/modules/comunidade/cadastroTurmas/")
        .await
        .expect("bla")
        .text()
        .await
        .expect("bla");
    let document = Document::from(body.as_ref());

    let predicate = Name("select")
        .and(Attr("name", "formBusca:selectCursosGraduacao"))
        .child(Name("option"));

    let courses: Vec<(String, String)> = document
        .find(predicate)
        .into_iter()
        .map(|node| (node.attr("value").unwrap().to_string(), node.text()))
        .collect();
    println!("{:?}", courses);
}
