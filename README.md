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

## Architecture Overview

The system is designed as a modular API-driven platform:

1.  **Inbound API Gateway**: Handles incoming requests, enforces rate limiting, and validates API keys.
2.  **Multi-Modal Analysis Engine**: Orchestrates the detection process by routing data to specialized processors.
    -   **Text Processor**: Leverages BERT to analyze urgency, sentiment, and impersonation attempts.
    -   **Speech Processor**: Utilizes Wav2Vec2 for speech analysis including stress and emotion detection.
3.  **Persistence & Cache Layer**:
    -   **PostgreSQL**: Stores logs, results, and configuration data.
    -   **Redis**: Provides high-speed caching for real-time processing performance.

## Future Roadmap

- [ ] **Real-time Streaming**: Implement WebSockets for live audio and text analysis.
- [ ] **Multi-language Support**: Extend detection capabilities to a broader range of languages.
- [ ] **Containerization**: Provide Docker and Kubernetes configurations for simplified deployment.
- [ ] **Admin Dashboard**: A visual interface for monitoring system performance and scam statistics.
- [ ] **Browser Extension**: Real-time phishing and scam detection for web browsers.

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

### Gmail API Integration

This project includes a Gmail API integration that allows you to fetch and analyze emails for potential scams.

#### Prerequisites

To use the Gmail API integration, you need:

1.  **A Google Cloud Project**: Create it in the [Google Cloud Console](https://console.cloud.google.com/).
2.  **Enabled Gmail API**: Enable the Gmail API for your project.
3.  **OAuth 2.0 Credentials**:
    *   Create "OAuth client ID" of type "Desktop app".
    *   Download the JSON file and rename it to `credentials.json`.
    *   Place `credentials.json` in the root directory of this project.

#### Troubleshooting

If you encounter network or protocol issues (e.g., `ERR_QUIC_PROTOCOL_ERROR` or `ERR_CONNECTION_TIMED_OUT` on Firebase), please refer to [NEURAL_LINKS.md](NEURAL_LINKS.md) for solutions, including:
- Disabling QUIC in Chrome.
- Using a manual access token override.
- Running the **Local Sandbox Mode** via `python start_sandbox.py` or using the **All-in-One Portable Script** `python anti_scam_ai_portable.py`.

## Security

- API Key authentication required.
- Rate limiting enabled to prevent abuse.
- Support for multiple file types: `.wav`, `.mp3`, `.txt`, `.pdf`.

## Related Projects

Here are some related open-source projects and resources in the field of AI-driven scam detection and multi-modal analysis:

- **[MultiModal_Scam_Detct](https://github.com/Codexx121/MultiModal_Scam_Detct)**: A multi-modal system that detects scam phone calls by analyzing both audio and text using a fusion of deep learning models.
- **[BlockSafe](https://github.com/bhargava562/block-safe)**: An autonomous cognitive firewall that fingerprints text-based scam strategies in real time using multimodal AI and voice intelligence.
- **[Fraud Detection Engine](https://github.com/dionysc/fraud-detection-engine)**: A mobile-first fraud detection engine for identifying phishing, scam messages, and malicious links with explainable risk analysis.
- **[Nuvoice Fraud Detection API](https://github.com/nuvoice-ai/fraud-detection-api)**: A REST API to protect voice login and authentication systems against AI-generated voice fraud.

## License

[Add License Information Here]
