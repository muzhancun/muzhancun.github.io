---
title: "MineStudio: A Streamlined Package for Minecraft AI Agent Development"
authors: ["Shaofei Cai*", "Zhancun Mu*", "Kaichen He", "Bowei Zhang", "Xinyue Zheng", "Anji Liu", "Yitao Liang"]
venue: "arXiv preprint"
year: 2024
publishDate: 2024-12-18
type: preprint
abstract: "MineStudio is a streamlined package for Minecraft AI agent development, released on GitHub and PyPI."
teaser: "/images/minestudio.png"
links:
  paper: "https://arxiv.org/abs/2412.18293"
  code: "https://github.com/CraftJarvis/MineStudio"
  project: "https://craftjarvis.github.io/MineStudio/"
tags: ["Minecraft", "Agent", "Reinforcement Learning"]
---

## Abstract

MineStudio is a streamlined package for Minecraft AI agent development, released on GitHub and PyPI. This package provides researchers and developers with a comprehensive toolkit for building and testing AI agents in the Minecraft environment.

## Features

### 🚀 Easy Installation
- Simple pip install process
- Minimal dependencies
- Cross-platform support

### 🛠️ Comprehensive Tools
- Agent development framework
- Environment setup utilities
- Evaluation metrics and benchmarks
- Visualization tools

### 📊 Benchmarking Suite
- Standard evaluation protocols
- Multiple task categories
- Performance metrics
- Comparison baselines

## Getting Started

```bash
pip install minestudio
```

```python
import minestudio as ms

# Create a new agent
agent = ms.Agent()

# Set up environment
env = ms.Environment()

# Start training
agent.train(env)
```

## Use Cases

1. **Research**: Rapid prototyping of new AI agent architectures
2. **Education**: Teaching AI concepts through interactive Minecraft environments
3. **Development**: Building production-ready Minecraft AI applications

## Community

MineStudio has an active community of researchers and developers contributing to the project. We welcome contributions, bug reports, and feature requests.

## Citation

If you use MineStudio in your research, please cite:

```bibtex
@article{cai2024minestudio,
  title={MineStudio: A Streamlined Package for Minecraft AI Agent Development},
  author={Cai, Shaofei and Mu, Zhancun and He, Kaichen and Zhang, Bowei and Zheng, Xinyue and Liu, Anji and Liang, Yitao},
  journal={arXiv preprint arXiv:2412.18293},
  year={2024}
}
```
