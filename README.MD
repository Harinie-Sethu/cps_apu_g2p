# Towards a Common Phone Space for Arabic, Persian, and Urdu: Leveraging Shared Phonology for Low-Resource G2P

This repo contains a Python toolkit for building a Common Phone Space (CPS) for Arabic–Persian–Urdu (APU).

## File Structure

- ```common_apu.map``` contains stage A rules
- ```common_apu_stageB.map``` contains stage B rules
- ```src/g2p_parser.py``` provides greedy maximal-munch segmentation (core cps-apu parser) 
- ```src/run_stageA.py``` gives Stage A evaluation on WikiTron gold 
- ```src/run_stageB.py``` gives Rule mining + Stage B evaluation 
- ```src/metrics.py``` implements token-level Levenshtein distance, Phoneme Error Rate (PER) and Top-1 Accuracy 
- ```data/raw``` contains wikipron TSVs (including words and their outputs)
- ```data/onlywords``` contains wikipron TSVs (only words, no outputs)
- ```llmPowered/common``` contains outputs of OpenAI o3's outputs using arabic, persian and urdu
- ```llmPowered/monolingual``` contains outputs of OpenAI o3's outputs using the particular language

## How to run code

#### 1) run Stage A evaluation
```python3 -m src.run_stageA  --map common_apu.map  --raw_dir data/raw```

#### 2) run Stage B evaluation
``` python3 -m src.run_stageB --base_map common_apu.map  --raw_dir data/raw --min_freq 20  --out_map common_apu_stageB.map ```

#### 4) epitran comparison
```python -m src.run_epitran --raw_dir data/raw```



