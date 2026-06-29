







# PPTAgent: Generating and Evaluating Presentations Beyond Text-to-Slides
<p align="center">
  📄 <a href="https://arxiv.org/abs/2501.03936" target="_blank">Paper</a> &nbsp; | &nbsp;
  🤗 <a href="https://huggingface.co/datasets/Forceless/Zenodo10K" target="_blank">Dataset</a> &nbsp; | &nbsp;
  📝 <a href="./DOC.md" target="_blank">Documentation</a> &nbsp; | &nbsp;
  🙏 <a href="#citation-" target="_blank">Citation</a>
</p>

We present PPTAgent, an innovative system that automatically generates presentations from documents. Drawing inspiration from human presentation creation methods, our system employs a two-step process to ensure excellence in overall quality. Additionally, we introduce **PPTEval**, a comprehensive evaluation framework that assesses presentations across multiple dimensions.

> [!TIP]
> 🚀 Get started quickly with our pre-built Docker image - [See Docker instructions](DOC.md/#docker-)

## Demo Video 🎥

https://github.com/user-attachments/assets/c3935a98-4d2b-4c46-9b36-e7c598d14863

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


## Citation 🙏

If you find this project helpful, please use the following to cite it:
```bibtex
@article{zheng2025pptagent,
  title={PPTAgent: Generating and Evaluating Presentations Beyond Text-to-Slides},
  author={Zheng, Hao and Guan, Xinyan and Kong, Hao and Zheng, Jia and Zhou, Weixiang and Lin, Hongyu and Lu, Yaojie and He, Ben and Han, Xianpei and Sun, Le},
  journal={arXiv preprint arXiv:2501.03936},
  year={2025}
}
```

[![Star History Chart](https://api.star-history.com/svg?repos=icip-cas/PPTAgent&type=Date)](https://star-history.com/#icip-cas/PPTAgent&Date)
