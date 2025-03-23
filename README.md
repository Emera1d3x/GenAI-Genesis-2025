# SwiftCareAI

## Real-time AI-powered decision support for healthcare professionals in high-pressure environments


## Overview

SwiftCareAI is a cutting-edge real-time decision support tool designed to assist healthcare professionals in high-pressure environments such as field hospitals, disaster zones, and emergency departments. Built on the modular Pocket Flow framework, SwiftCareAI leverages AI to automate triage processes, optimize resource allocation, and provide critical insights when every second counts.

## Why SwiftCareAI?

In emergency situations, healthcare professionals face immense challenges:
- Manual triage processes are slow and error-prone
- Information overload makes it difficult to focus on critical cases
- Resource allocation decisions must be made rapidly with limited data
- Conditions change dynamically, requiring constant reassessment

SwiftCareAI addresses these challenges by:
- Automating patient prioritization based on severity and urgency
- Filtering inputs to present only the most relevant information
- Recommending optimal resource allocation in real-time
- Adapting to changing conditions while keeping humans in the loop

## Key Features

### 🔄 AI-Powered Triage
Automatically prioritizes patients based on symptoms, vital signs, age, and other factors, ensuring critical cases receive immediate attention.

### 🏥 Smart Resource Allocation
Recommends optimal treatment centers and transport routes based on hospital capacity, distance, and specialized care availability.

### 📊 User-Friendly Dashboard
Intuitive Streamlit-based interface provides doctors with prioritized patient lists, key metrics, and real-time alerts.

### 🔍 Filtered Information
Reduces cognitive load by highlighting only the most critical information for each patient.

### ⚡ Real-Time Adaptability
Adjusts recommendations based on changing conditions such as hospital capacity and transport availability.

### 👩‍⚕️ Human-in-the-Loop Design
Provides AI-driven recommendations while leaving final decisions to healthcare professionals.

## Technical Architecture

SwiftCareAI is built on the modular Pocket Flow framework, which provides:

### Modularity
- Vendor-agnostic design allows for easy integration with various tools and services
- Components can be swapped without disrupting the entire workflow

### Expressibility
- Minimal but powerful API handles complex workflows with minimal code
- Supports multi-agent systems and retrieval-augmented generation

### Information Hiding
- Internal implementation of nodes is hidden, allowing for seamless updates
- Clean interfaces between components enhance maintainability

## Core Components

### Data Ingestion Node
Collects and processes data from multiple sources including first responders, nurses, wearable devices, and transport teams.

### Preprocessing Node
Cleans, normalizes, and organizes data for analysis, removing duplicates and handling missing values.

### Triage Node
Uses AI models (powered by Cohere) to assign priority scores based on symptom severity, vital signs, and other factors.

### Resource Allocation Node
Analyzes hospital capacity and distance to recommend optimal treatment centers and transport routes.

### Filtering Node
Identifies and highlights critical data points for immediate attention.

### Visualization Node
Presents filtered, prioritized data through an intuitive Streamlit dashboard.

## Technology Stack

- **Backend**: Python, Firebase, Firestore
- **NLP**: Cohere API for symptom analysis
- **Frontend**: Streamlit
- **External APIs**: OpenStreetMap for hospital location data
- **Architecture**: Pocket Flow for modular workflow design
- **Cloud**: Google Cloud Platform

## Getting Started

### Prerequisites
- Python 3.8+
- Google Cloud account with Firestore enabled
- Cohere API key

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/swiftcareai.git
cd swiftcareai
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and credentials
```

### Running the Application

1. Start the backend:
```bash
python backend.py
```

2. Launch the Streamlit frontend:
```bash
streamlit run frontend.py
```

## Future Development

SwiftCareAI is under active development with several planned enhancements:

1. **MLOps Integration**: CI/CD pipelines and model registries for automated deployment
2. **Real-Time Adaptive Flows**: Dynamic workflow adjustments based on performance metrics
3. **Advanced Debugging & Logging**: Enhanced visualization tools and granular monitoring
4. **Extended Durability Features**: Support for long-running, distributed tasks
5. **Wearable Device Integration**: Direct data collection from patient monitoring devices

## Contributing

We welcome contributions from the community! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Team

- Backend Development
- Frontend Development
- Data Science
- Project Management

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Pocket Flow framework for providing the modular architecture
- Cohere for NLP capabilities
- Google Cloud Platform for hosting and infrastructure
# GenAI-Genesis-2025
 GenAI-Genesis-2025
## Acknowledgments
This project uses the [Pocket Flow](https://github.com/pocketflow/pocketflow) framework, developed by [Helena Zhang](https://github.com/helenaeverl) and contributors. Pocket Flow is a minimalistic AI framework designed for modular and scalable workflows.