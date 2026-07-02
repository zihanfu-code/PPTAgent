# PPTAgent: Generating and Evaluating Presentations Beyond Text-to-Slides

PPTAgent is an innovative system that automatically generates presentations from documents. Drawing inspiration from human presentation creation methods, the system employs a two-step process to ensure excellence in overall quality. Additionally, it includes **PPTEval**, a comprehensive evaluation framework that assesses presentations across multiple dimensions.

> [!TIP]
> 🚀 Get started quickly with our pre-built Docker image - [See Docker instructions](DOC.md/#docker-)

## Project Background

Mainstream document-to-PPT tools on the market generally suffer from content redundancy, monotonous visuals, and rigid structures. In particular, they are unable to automatically reproduce images and tables from the source document, making them inadequate for high-quality presentation needs in real-world office and academic scenarios.

## Solution

- **Reference-driven editing-based generation framework**: Models slide generation as a batch of insert, delete, and update operations (function call API sequences) on reference PPTs, supporting automatic editing and self-correction of text, images, and other multi-type elements. This significantly improves content structure, visual style adaptability, and system robustness.
- **Automatic visual layout grouping via ViT + hierarchical clustering**: Extracts slide image embeddings using a ViT model, groups visual layouts through hierarchical clustering, and leverages GPT-4o to extract structured content schemas for each layout category, enabling efficient style transfer.
- **HTML-based slide parsing and editing environment**: Converts raw XML slide structures into HTML, substantially reducing the difficulty for GPT-4o to understand and manipulate page layouts.
- **Multi-dimensional automatic evaluation framework**: Integrates content richness, design aesthetics, and structural coherence into an automatic scoring system, achieving a correlation of over 0.7 with human evaluation scores.

## Project Results

Tested on Zenodo10K and other multi-domain public datasets, the system achieves an average improvement of 13%–29% over template-based and rule-based baselines across content, design, and coherence metrics, with structural coherence scores improving by over 25%. The final average score reaches **3.67/5**.

## Distinctive Features ✨

- **Dynamic Content Generation**: Creates slides with seamlessly integrated text and images
- **Smart Reference Learning**: Leverages existing presentations without requiring manual annotation
- **Comprehensive Quality Assessment**: Evaluates presentations through multiple quality metrics

## PPTAgent 🤖

PPTAgent follows a two-phase approach:
1. **Analysis Phase**: Extracts and learns from patterns in reference presentations
2. **Generation Phase**: Develops structured outlines and produces visually cohesive slides

## PPTEval ⚖️

PPTEval evaluates presentations across three dimensions:
- **Content**: Check the accuracy and relevance of the slides.
- **Design**: Assesses the visual appeal and consistency.
- **Coherence**: Ensures the logical flow of ideas.

## Quick Start 🚀

### Requirements

- Python 3.11+
- LibreOffice, Chrome, poppler-utils, NodeJS
- 8GB+ RAM (GPU recommended for faster processing)

### Installation

```bash
pip install git+https://github.com/zihanfu-code/PPTAgent.git
```

Or install from source:

```bash
git clone https://github.com/zihanfu-code/PPTAgent.git
cd PPTAgent
pip install -e .
```

### Usage

#### Via Web UI

```bash
cd pptagent_ui
npm install
npm run serve
```

Then start the backend:

```bash
python pptagent_ui/backend.py
```

#### Via Code

```python
from pptagent import PPTAgentAsync
from pptagent.document import Document
from pptagent.model_utils import ModelManager

models = ModelManager()
agent = PPTAgentAsync(
    models.text_model,
    models.language_model,
    models.vision_model,
)
# See pptagent_ui/backend.py and test/test_pptgen.py for detailed examples
```

## Project Structure 📂

```
PPTAgent/
├── pptagent/                     # Core Python package
│   ├── agent.py                  # Agent and AsyncAgent framework
│   ├── llms.py                   # LLM and AsyncLLM wrappers
│   ├── apis.py                   # CodeExecutor and API functions
│   ├── induct.py                 # Presentation analysis (Stage I)
│   ├── pptgen.py                 # Presentation generation (Stage II)
│   ├── ppteval.py                # PPTEval evaluation framework
│   ├── model_utils.py            # Model management utilities
│   ├── multimodal.py             # Multi-modal processing
│   ├── prompts/                  # Prompt templates
│   ├── roles/                    # Agent role definitions
│   ├── document/                 # Document parsing and structuring
│   └── presentation/             # PowerPoint file operations
├── pptagent_ui/                  # Web UI
│   ├── backend.py                # FastAPI backend server
│   └── src/                      # Vue.js frontend
├── test/                         # Test suite
├── docker/                       # Docker configuration
└── resource/                     # Images and templates
```

## Documentation 📝

See [DOC.md](DOC.md) for detailed documentation on setup, usage, and configuration.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
