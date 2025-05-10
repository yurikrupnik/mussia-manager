use std::io;
use crossterm::{
  event::{self, DisableMouseCapture, EnableMouseCapture, Event, KeyCode},
  execute,
  terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use ratatui::{
  backend::{Backend, CrosstermBackend},
  layout::{Constraint, Layout},
  widgets::{Block, Borders, Paragraph},
  Terminal,
};
use tokio::process::Command;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
  // Init terminal
  enable_raw_mode()?;
  let mut stdout = io::stdout();
  execute!(stdout, EnterAlternateScreen, EnableMouseCapture)?;
  let backend = CrosstermBackend::new(stdout);
  let mut terminal = Terminal::new(backend)?;

  let status = match check_cluster().await {
    Ok(true) => "Kind cluster already exists.".to_string(),
    Ok(false) => {
      match create_cluster().await {
        Ok(_) => "Kind cluster created.".to_string(),
        Err(e) => format!("Failed to create cluster: {}", e),
      }
    }
    Err(e) => format!("Error checking cluster: {}", e),
  };

  loop {
    terminal.draw(|f| {
      let chunks = Layout::default()
        .constraints([Constraint::Percentage(100)].as_ref())
        .split(f.area());

      let block = Block::default().title("Kind Cluster Check").borders(Borders::ALL);
      let paragraph = Paragraph::new(status.as_str()).block(block);
      f.render_widget(paragraph, chunks[0]);
    })?;

    if event::poll(std::time::Duration::from_millis(500))? {
      if let Event::Key(key) = event::read()? {
        if key.code == KeyCode::Char('q') {
          break;
        }
      }
    }
  }

  // Restore terminal
  disable_raw_mode()?;
  execute!(
        terminal.backend_mut(),
        LeaveAlternateScreen,
        DisableMouseCapture
    )?;
  terminal.show_cursor()?;

  Ok(())
}

async fn check_cluster() -> Result<bool, Box<dyn std::error::Error>> {
  let output = Command::new("kind")
    .args(["get", "clusters"])
    .output()
    .await?;
  if !output.status.success() {
    return Err("Failed to run 'kind get clusters'".into());
  }

  let output_str = String::from_utf8_lossy(&output.stdout);
  Ok(!output_str.trim().is_empty())
}

async fn create_cluster() -> Result<(), Box<dyn std::error::Error>> {
  let status = Command::new("kind")
    .args(["create", "cluster"])
    .status()
    .await?;

  if !status.success() {
    return Err("kind cluster creation failed".into());
  }

  Ok(())
}
