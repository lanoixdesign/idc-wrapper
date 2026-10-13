use anyhow::{Context, Result};
use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::time::Duration;

/// Journal append-only : on ne peut qu’ajouter.
#[derive(Debug, Default, Clone)]
struct AppendOnlyJournal {
    entries: Vec<String>,
}

impl AppendOnlyJournal {
    fn append(&mut self, entry: impl Into<String>) {
        self.entries.push(entry.into());
    }

    fn as_context(&self) -> String {
        self.entries.join("\n---\n")
    }
}

/// État de l’agent IDC.
#[derive(Debug)]
struct IdcAgent {
    client: Client,
    api_url: String,
    api_key: String,
    model: String,
    resource: f64,
    journal: AppendOnlyJournal,
    seuil_critique: f64,
    cout_par_token: f64,
}

#[derive(Serialize)]
struct ChatRequest {
    model: String,
    messages: Vec<Message>,
    max_tokens: u32,
    temperature: f32,
}

#[derive(Serialize, Deserialize)]
struct Message {
    role: String,
    content: String,
}

#[derive(Deserialize)]
struct ChatResponse {
    choices: Vec<Choice>,
}

#[derive(Deserialize)]
struct Choice {
    message: Message,
}

impl IdcAgent {
    fn new(api_url: String, api_key: String, model: String) -> Self {
        Self {
            client: Client::builder()
                .timeout(Duration::from_secs(60))
                .build()
                .expect("client"),
            api_url,
            api_key,
            model,
            resource: 100.0,
            journal: AppendOnlyJournal::default(),
            seuil_critique: 15.0,
            cout_par_token: 0.8,
        }
    }

    async fn call_model(&self, prompt: &str, max_tokens: u32) -> Result<String> {
        let req = ChatRequest {
            model: self.model.clone(),
            messages: vec![Message {
                role: "user".into(),
                content: prompt.into(),
            }],
            max_tokens,
            temperature: 0.7,
        };

        let resp = self
            .client
            .post(&self.api_url)
            .bearer_auth(&self.api_key)
            .json(&req)
            .send()
            .await
            .context("requête HTTP")?
            .error_for_status()
            .context("statut HTTP")?
            .json::<ChatResponse>()
            .await
            .context("parsing JSON")?;

        Ok(resp
            .choices
            .into_iter()
            .next()
            .map(|c| c.message.content)
            .unwrap_or_default())
    }

    fn vaut_encore_la_peine(&self, gain_estime: f64) -> bool {
        let cout_marginal = self.cout_par_token * 50.0;
        let risque = if self.resource < 30.0 { 2.0 } else { 1.0 };
        gain_estime > cout_marginal * risque
    }

    async fn run(&mut self, tache: &str) -> Result<String> {
        let mut reponse_courante = String::new();
        let mut etape = 0;

        while self.resource > self.seuil_critique && etape < 8 {
            etape += 1;

            let contexte = format!(
                "Journal des engagements précédents :\n{}\n\nTâche : {}\n\nRéponse partielle actuelle :\n{}\n\nContinue ou affine la réponse. Sois concis.",
                self.journal.as_context(),
                tache,
                reponse_courante
            );

            let suite = self.call_model(&contexte, 120).await?;
            let tokens_approx = suite.split_whitespace().count() as f64;
            let cout = tokens_approx * self.cout_par_token;

            self.resource -= cout;
            self.resource = self.resource.max(0.0);

            let gain_estime = if suite.len() > 20 { 25.0 } else { 8.0 };

            println!(
                "[étape {}] R restante = {:.1} | coût = {:.1} | gain estimé = {:.1}",
                etape, self.resource, cout, gain_estime
            );

            if !self.vaut_encore_la_peine(gain_estime) || self.resource <= self.seuil_critique {
                println!("→ Arrêt optimal déclenché.");
                break;
            }

            reponse_courante.push_str(&suite);
            reponse_courante.push('\n');
            self.journal.append(format!("Étape {} : {}", etape, suite.trim()));
        }

        if reponse_courante.trim().is_empty() {
            Ok("Je ne sais pas (ressource insuffisante ou incertitude trop élevée).".into())
        } else {
            Ok(reponse_courante)
        }
    }
}

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
