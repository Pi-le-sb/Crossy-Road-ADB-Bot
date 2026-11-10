# Existing CrossyRoad v2 export: no validation folder

The dataset version page confirms 28 training images, 0 validation images and 0 test images:
https://universe.roboflow.com/crossyroad-q9hpe/crossyroad-e1abn/dataset/2
Do not create an empty valid folder or copy the same images into train and val. The user's YAML has Tree at zero-based class 12 and no rock class.

From C:\Users\pile\Crossy-Road-ADB-Bot:
.venv-training\Scripts\python.exe -m unittest -v test_split_tree_export
.venv-training\Scripts\python.exe split_tree_export.py --source "training-data\raw" --out "training-data\tree-prepared"

This single command both splits and prepares a TREE-ONLY dataset. Do not run the old prepare step on the raw train-only export first. The output contains data.yaml, train/images, train/labels, val/images, val/labels and split_report.json. The original export, profile and vehicle model are unchanged. Existing output directories are refused. To rerun safely use a different --out folder.

All labels are checked before writing; only Tree labels are retained and remapped to class 0. Actual image files are copied, not moved. SHA-256 exact duplicate images are dropped if their tree annotations agree, otherwise the command fails. Files sharing the part of the stem before .rf. stay in one group; this avoids splitting common Roboflow variants of the same named original. The split uses seed 42 and aims for 20 percent validation GROUPS, so image counts can differ from 80/20. At least one tree-containing group is reserved for each split. Missing labels, invalid boxes and insufficient positive groups cause an error.

This is a small experimental split, NOT proof of independent scene-level validation. Similar screenshots under different names can still leak between splits. Human review/grouping by recording and more data are required before accuracy claims. There is no held-out test split.

After reviewing the generated labels, explicit local tree training can use the existing trusted checkpoint:
.venv-training\Scripts\python.exe obstacle_training.py train --data "training-data\tree-prepared\data.yaml" --weights crossy_yolo.pt --trust-weights --tree-only

Training is not started by splitting. No new weights are included. Rocks are not learned. The source version was preprocessed with stretch to 1920x1080 according to its page; check whether this distortion differs from your phone before trusting model accuracy. No automatic phone movement or restart is added. No files are saved on the phone. Keep raw data and trained weights out of Git commits.

Validation performed: seven synthetic local-export tests and syntax compilation passed in the assistant environment, including a 14-class source with Tree=12. No access to the user's actual local export, no actual dataset training and no device tests were performed.
