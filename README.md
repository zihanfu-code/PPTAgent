# PPTAgent: Generating and Evaluating Presentations Beyond Text-to-Slides

PPTAgent is an innovative system that automatically generates presentations from documents. Drawing inspiration from human presentation creation methods, the system employs a two-step process to ensure excellence in overall quality. Additionally, it includes **PPTEval**, a comprehensive evaluation framework that assesses presentations across multiple dimensions.

> [!TIP]
> 🚀 Get started quickly with our pre-built Docker image - [See Docker instructions](DOC.md/#docker-)

## Distinctive Features ✨

- **Dynamic Content Generation**: Creates slides with seamlessly integrated text and images
- **Smart Reference Learning**: Leverages existing presentations without requiring manual annotation
- **Comprehensive Quality Assessment**: Evaluates presentations through multiple quality metrics

## Case Study 💡

- #### [Iphone 16 Pro](https://www.apple.com/iphone-16-pro/)

<div style="display: flex; flex-wrap: wrap; gap: 10px;">

  <img src="resource/iphone16pro/0001.jpg" alt="图片1" width="200"/>

  <img src="resource/iphone16pro/0002.jpg" alt="图片2" width="200"/>

  <img src="resource/iphone16pro/0003.jpg" alt="图片3" width="200"/>

  <img src="resource/iphone16pro/0004.jpg" alt="图片4" width="200"/>

  <img src="resource/iphone16pro/0005.jpg" alt="图片5" width="200"/>

  <img src="resource/iphone16pro/0006.jpg" alt="图片6" width="200"/>

  <img src="resource/iphone16pro/0007.jpg" alt="图片7" width="200"/>

</div>

- #### [Build Effective Agents](https://www.anthropic.com/research/building-effective-agents)

<div style="display: flex; flex-wrap: wrap; gap: 10px;">

  <img src="resource/build_effective_agents/0001.jpg" alt="图片1" width="200"/>

  <img src="resource/build_effective_agents/0002.jpg" alt="图片2" width="200"/>

  <img src="resource/build_effective_agents/0003.jpg" alt="图片3" width="200"/>

  <img src="resource/build_effective_agents/0004.jpg" alt="图片4" width="200"/>

  <img src="resource/build_effective_agents/0005.jpg" alt="图片5" width="200"/>

  <img src="resource/build_effective_agents/0006.jpg" alt="图片6" width="200"/>

  <img src="resource/build_effective_agents/0007.jpg" alt="图片7" width="200"/>

  <img src="resource/build_effective_agents/0008.jpg" alt="图片8" width="200"/>

<img src="resource/build_effective_agents/0009.jpg" alt="图片9" width="200"/>

<img src="resource/build_effective_agents/0010.jpg" alt="图片10" width="200"/>

</div>

## PPTAgent 🤖

PPTAgent follows a two-phase approach:
1. **Analysis Phase**: Extracts and learns from patterns in reference presentations
2. **Generation Phase**: Develops structured outlines and produces visually cohesive slides

Our system's workflow is illustrated below:


![PPTAgent Workflow](resource/fig2.jpg)

## PPTEval ⚖️

PPTEval evaluates presentations across three dimensions:
- **Content**: Check the accuracy and relevance of the slides.
- **Design**: Assesses the visual appeal and consistency.
- **Coherence**: Ensures the logical flow of ideas.

The workflow of PPTEval is shown below:
<p align="center">
<img src="resource/fig3.jpg" alt="PPTEval Workflow" style="width:70%;"/>
</p>

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
