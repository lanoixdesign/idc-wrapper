//! Binaire CLI — enveloppe mince autour de la bibliothèque `idc_wrapper`.

use anyhow::Result;
use idc_wrapper::IdcAgent;

#[tokio::main]
async fn main() -> Result<()> {
    let mut agent = IdcAgent::new(
        "https://api.openai.com/v1/chat/completions".into(),
        std::env::var("OPENAI_API_KEY").unwrap_or_else(|_| "sk-...".into()),
        "gpt-4o-mini".into(),
    );

    let tache = "Explique en 5 points pourquoi la finitude computationnelle peut réduire les hallucinations.";
    let resultat = agent.run(tache).await?;

    println!("\n=== RÉPONSE FINALE (après effondrement) ===\n{}", resultat);
    println!("\n=== JOURNAL APPEND-ONLY ===\n{}", agent.journal.as_context());
    println!("\nRessource finale : {:.1}", agent.resource);

    Ok(())
}
