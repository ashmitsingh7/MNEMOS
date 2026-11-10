# MNEMOS Research Problem

## Core Question

Can a mobile robot interpret human navigation interventions, associate them with spatial and semantic context, store them as episodic experiences, and use those experiences to improve future autonomous navigation while recognizing when previously learned experiences are no longer valid?

## Research Hypothesis

A navigation architecture combining spatial understanding, intervention interpretation, contextual episodic memory and memory validation can reduce repeated navigation mistakes and unnecessary human interventions in previously encountered situations.

## Hypothesis Treatise

This is treated as a hypothesis to test, not an established result. The platform must demonstrate through experimentation whether episodic memory-based navigation provides measurable benefits over conventional Nav2 navigation alone.

## Experimental Framework

Five experiments test different aspects of the hypothesis:

1. **Experiment 1 - Conventional Baseline**: SLAM + Nav2 navigation only. Measures navigation success, path length, time-to-goal, collision count, navigation failures, and intervention count.

2. **Experiment 2 - Human Intervention Learning**: Enables intervention capture and interpretation. Measures classification accuracy against human-labelled data, interpretation confidence, repeated intervention frequency, and navigation success.

3. **Experiment 3 - Episodic Memory**: Enables contextual memory and retrieval. Measures retrieval precision, retrieval relevance, repeated navigation mistakes, human interventions per task, and navigation success.

4. **Experiment 4 - Memory Validation**: Changes the environment between sessions (move furniture, clear blocked passages, block clear corridors, introduce temporary obstacles). Measures outdated memory reuse, memory invalidation accuracy, adaptation time, and navigation success after environmental changes.

5. **Experiment 5 - Ablation Study**: Compares four configurations:
   - A. Baseline navigation (SLAM + Nav2)
   - B. Navigation with intervention learning
   - C. Navigation with intervention learning + episodic memory
   - D. Navigation with intervention learning + episodic memory + memory validation
   Results reported separately for each configuration.

## Expected Contributions

If the hypothesis is supported, MNEMOS will demonstrate that:
- Robots can convert human corrections into structured experiences
- Contextual retrieval of experiences improves navigation decisions
- Memory validation prevents stale or contradicted memories from influencing navigation
- Ablated configurations show measurable differences in performance

If the hypothesis is not supported, the platform still provides value as a testbed for understanding the limits of experience-based navigation.