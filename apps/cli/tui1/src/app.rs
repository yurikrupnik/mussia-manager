use std::{io, time::Duration};
use crossterm::{event::{self, DisableMouseCapture, EnableMouseCapture, Event, KeyCode}, execute, terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen}};
use ratatui::{prelude::*, widgets::*};

enum AppState {
  Main,
  Status,
}

struct App {
  state: AppState,
  prometheus_installed: bool,
}

impl App {
  fn new() -> Self {
    Self {
      state: AppState::Main,
      prometheus_installed: false,
    }
  }

  fn install_prometheus(&mut self) {
    // Placeholder for actual cluster creation & Prometheus install logic
    // Could be shelling out to `kind`/`kubectl` or using a library
    self.prometheus_installed = true;
  }
}

fn main() -> Result<(), io::Error> {
  enable_raw_mode()?;
  let mut stdout = io::stdout();
  execute!(stdout, EnterAlternateScreen, EnableMouseCapture)?;
  let backend = CrosstermBackend::new(stdout);
  let mut terminal = Terminal::new(backend)?;

  let mut app = App::new();
  let tick_rate = Duration::from_millis(200);

  loop {
    terminal.draw(|f| match app.state {
      AppState::Main => draw_main(f, &app),
      AppState::Status => draw_status(f, &app),
    })?;

    if event::poll(tick_rate)? {
      if let Event::Key(key) = event::read()? {
        match key.code {
          KeyCode::Char('q') => break,
          KeyCode::Char('i') => app.install_prometheus(),
          KeyCode::Char('s') => app.state = AppState::Status,
          KeyCode::Esc => app.state = AppState::Main,
          _ => {}
        }
      }
    }
  }

  disable_raw_mode()?;
  execute!(terminal.backend_mut(), LeaveAlternateScreen, DisableMouseCapture)?;
  terminal.show_cursor()?;
  Ok(())
}

fn draw_main(f: &mut Frame, app: &App) {
  let size = f.size();
  let block = Block::default().title("Prometheus Installer").borders(Borders::ALL);
  let text = vec![
    Line::from("[i] Install Prometheus"),
    Line::from("[s] Status"),
    Line::from("[q] Quit"),
  ];
  let paragraph = Paragraph::new(text).block(block).alignment(Alignment::Left);
  f.render_widget(paragraph, size);
}

fn draw_status(f: &mut Frame, app: &App) {
  let size = f.size();
  let status = if app.prometheus_installed {
    "Prometheus is installed."
  } else {
    "Prometheus is NOT installed."
  };
  let block = Block::default().title("Status").borders(Borders::ALL);
  let paragraph = Paragraph::new(status).block(block).alignment(Alignment::Center);
  f.render_widget(paragraph, size);
}
