# causal-models-in-python_actr

This repo holds four ACT-R models for causal reasoning over a bomb diffusion task.

## Causal Models:

1. causal-bomb-diffusion-blue-then-red-plan-inference-correct.py
2. causal-bomb-diffusion-blue-then-red-using-unittask-correct.py
3. causal-bomb-diffusion-red-then-blue-using-unittask-correct.py
4. causal-bomb-diffusion-blue-then-red-using-unittask-incorrect.py
5. causal-bomb-diffusion-no-prior-knowledge.py

### 1. causal-bomb-diffusion-blue-then-red-plan-inference-correct.py
The agent knows which plan will disarm the bomb prior to the task. Following task completion, the agent infers and reports whether the bomb has been disarmed, which plan it used to disarm it, and which plan would've left the bomb armed. This is the default model used to create the others.

### 2. causal-bomb-diffusion-blue-then-red-using-unittask-correct.py
The agent doesn't know which plan will disarm the bomb, but does know which wire to cut second to disarm the bomb. Using this knowledge, it identifies which plans involve cutting the target wire second, and then selects from those plans. For this model, there is a single plan that matches this requirement, although more could be added.

### 3. causal-bomb-diffusion-red-then-blue-using-unittask-correct.py
The bomb is disarmed by cutting the red wire and then the blue wire, instead. The agent knows which wire to cut second (blue), and performs the same operations as model 2. Changes to lines 43, 44, and 76 allow you to change which wire is cut first/second.

### 4. causal-bomb-diffusion-blue-then-red-using-unittask-incorrect.py
Line 305 in declarative memory under the counterfactuals section controls which wire the agent knows to cut second, prior to the task. The target wire, blue_wire, is the wrong one, so the agent will fail to disarm the bomb, and only realize this afterward. It will then infer and report which plan would disarm the bomb. This last part is only possible because the task has only two options in mutual exclusion. Were the task more complex, and the agent capable of more actions, it might not be able to infer how to disarm the bomb.

### 5. causal-bomb-diffusion-no-prior-knowledge.py
The agent has no prior knowledge about the task, so it randomly tries one of either of its planning units, and then reasons about the result, inferring and reporting the correct plan to disarm the bomb, and the plan that leaves the bomb armed.

## Declarative Memory's (DM) Ladder of Causation
The causal model in DM is stratified using Pearl's Ladder of Causation for convenience. The second rung, Interventions, provides knowledge of state changes based on actions or lower-level interventions taken. These lower-level interventions are used to represent counterfactuals. All key:value pairs in ACT-R allow for matching keys with different values, meaning that key:!value represents all disjunctive values for a specific key:value. Interventions are built using relations similar to classic AI planning: (key:S,key:A,key:S'). These chunks use keys to relate mutually exclusive actions (key:!A) with spreading activation, where (key:S,key:A,key:S') and (key:S,key:!A,key:!S') are counterfactuals. (key:S,key:!A,key:S') expresses a counterfactual without an effect, because the alternate actions/interventions do not cause anything. 

## Kantian Declarative Memory:
Each model uses the same design for Kantian Declarative Memory (KDM).
KDM is built with declarative memory chunks that use key:value pairs for each slot in every chunk.
In KDM, each key represents a Kantian category, and each value is designated to that category.
All relations in declarative memory are defined using terms from the categorical structure built in KDM. Alternate designs to KDM are plausible. Several Kantian categories are still missing, because they were unnecessary for the causal models listed above.
