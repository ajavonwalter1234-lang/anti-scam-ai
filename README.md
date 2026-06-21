# Anti-Scam AI

Anti-Scam AI is a comprehensive security tool designed to detect and prevent scam attempts through multi-modal analysis of text and speech. It leverages advanced machine learning models to identify suspicious patterns in real-time communication.

## Features

### Text Analysis
- **Urgency Detection**: Identifies high-pressure tactics commonly used in scams.
- **Financial Keywords**: Monitors for suspicious financial requests or sensitive terms.
- **Impersonation Detection**: Detects attempts to mimic legitimate entities.
- **Link Detection**: Analyzes URLs for potential phishing or malicious content.
- **Sentiment Analysis**: Evaluates the tone of the communication.

### Speech Analysis
- **Stress Detection**: Monitors vocal indicators of stress in speakers.
- **Speech Rate Analysis**: Analyzes the pace of speech for anomalies.
- **Emotion Detection**: Identifies emotional states that may indicate fraudulent intent.
- **Accent Analysis**: Analyzes speech patterns for consistency.

## Technical Stack

- **NLP Model**: BERT (`bert-base-uncased`)
- **Speech Model**: Wav2Vec2 (`wav2vec2-base`)
- **Database**: PostgreSQL
- **Cache**: Redis
- **API Framework**: High-performance API with CORS support and rate limiting.

## Project Structure

- `config.yaml`: Central configuration for model settings, database, API, and analysis parameters.

## Getting Started

> **Note**: This project is in its early stages of development.

### Configuration

Customize the application behavior by editing `config.yaml`. Key settings include:
- `model`: Adjust model types and thresholds.
- `text_analysis` / `speech_analysis`: Enable or disable specific detection features.
- `database` / `cache`: Configure connection settings for PostgreSQL and Redis.
- `api`: Set host, port, and security parameters.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ajavonwalter1234-lang/anti-scam-ai.git
   cd anti-scam-ai
   ```
2. (In development) Install dependencies and set up the environment.

## Security

- API Key authentication required.
- Rate limiting enabled to prevent abuse.
- Support for multiple file types: `.wav`, `.mp3`, `.txt`, `.pdf`.

## License

[Add License Information Here]
