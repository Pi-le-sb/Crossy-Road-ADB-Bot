# Online-data preparation and local training (no model produced yet)

This patch adds a reproducible workflow, NOT a trained tree/rock detector. No real dataset download or YOLO training was performed by the assistant. It has no phone/ADB access and does not modify crossy_yolo.pt or calibration profiles. Default working files are under your PC home folder .crossy-road-adb-bot/training, outside Git.

## Source found

CrossyRoad Dataset, creator CrossyRoad, hosted by Roboflow Universe:
https://universe.roboflow.com/crossyroad-q9hpe/crossyroad-e1abn
The source page declares 28 images, CC BY 4.0, and includes Tree in its class list. It does NOT list a rock/stone class. There are two dataset versions; select an actual version from the page rather than assuming its number. Retain source attribution, version and change notices. Check underlying image rights and model/dependency licenses as well. Source page license declaration is not a legal audit of every image.

## Install optional tools

Prefer a separate environment if existing package versions must stay unchanged.
python -m pip install -r requirements-training.txt
python -m unittest -v test_obstacle_training

## Download once onto your PC

Roboflow export may require your account/API key and permission. Never paste keys into chat, source code, commits or screenshots. Set ROBOFLOW_API_KEY only in your local environment. The SDK transmits it to Roboflow for authentication; this code does not save it.

Windows CMD example (replace YOUR_LOCAL_KEY and VERSION with your actual local credential/version; do not run placeholders literally):
set ROBOFLOW_API_KEY=YOUR_LOCAL_KEY
python obstacle_training.py download --version VERSION --out "%USERPROFILE%\.crossy-road-adb-bot\training\raw"
set ROBOFLOW_API_KEY=

Alternatively export/download YOLOv8 from the dataset page yourself and extract into that raw folder. Export credentials/links should not be committed. The downloader refuses an existing target. Partial failed downloads need a new folder or manual review; they are not silently overwritten. There is no paid cloud training call.

## Prepare tree-only experiment with the source currently found

python obstacle_training.py prepare --source "%USERPROFILE%\.crossy-road-adb-bot\training\raw" --tree-only

This can produce ONLY a tree dataset, never a rock model. The default output is training/prepared under the PC home working directory. It refuses existing output directories. Use --out with a new path for another preparation.

The full tree+rock preparation omits --tree-only and intentionally fails until both requested classes have labels in train AND validation. Renaming a class or adding a YAML entry does not generate missing stone annotations. This patch does not search for, scrape or label additional rock images automatically. That remains the unresolved dataset requirement.

Input must have data.yaml with zero-based names and flat train/images + train/labels, valid/images (or val/images) + matching labels; canonical images/train and labels/train also work. Custom YAML path lists and nested image trees are not supported. Exact class aliases: tree/trees -> tree; rock/rocks/stone/stones -> rock. Other classes are removed from the separate obstacle dataset, not the original vehicle model. YOLO boxes must be normalized class/xc/yc/w/h rows. Explicit empty label files are accepted for negatives only after manual review. Missing label files are rejected, not assumed to be background.

Checks include image validity, box bounds, finite coordinates, class IDs, exact byte-duplicate images and labeled instances in both train/val. These checks cannot detect wrong or incomplete human annotations, near-duplicates, train/validation scene leakage or insufficient diversity. Do not call unlabeled rocks negatives in a two-class dataset. Split by recording/scene before augmentation and inspect labels visually.

## Explicit local training

Only after data preparation and visual review, a tree-only experiment can be started with an existing trusted local checkpoint:
python obstacle_training.py train --weights crossy_yolo.pt --trust-weights --tree-only

It defaults to 50 epochs, 640px input, batch 4 and CPU. These are starting parameters, not measured optimal settings. --compute 0 requests a compatible GPU. Training can be slow/resource-intensive. Third-party checkpoint loading requires trust and is not sandboxed. Reusing a checkpoint with another class head creates a separate obstacle model; do not replace the original vehicle weights. With a complete two-class dataset, omit --tree-only for preparation AND training. --data can point to the prepared data.yaml.

Output is saved to a unique run under the PC home working directory. The script validates best.pt on the validation split and writes validation_summary.json. That validation split was used during training selection; this is NOT an independent held-out test or real-device validation. No minimum accuracy guarantee or automatic deployment is applied. Independent scene-level tests and inspection on this phone are still required.

A locally produced model can be inspected separately with the existing object_preview.py --weights PATH_TO_BEST_PT --trust-weights. Combining it with the vehicle detector is not included in this patch. No automatic controls/restart are enabled.

## Validation actually performed

Seven synthetic local PNG/label tests passed: remapping/source preservation, missing rock, missing annotations, duplicate images, invalid coordinates, existing-output preservation and missing validation-class examples. Both scripts passed syntax compilation. Roboflow authentication/download, real source annotations, Ultralytics training, inference and GPU/phone behavior were not executed. There are no new trained weights in this commit.

Format and SDK references:
https://docs.ultralytics.com/datasets/detect/
https://docs.roboflow.com/datasets/create-and-upload/download-a-dataset
https://docs.roboflow.com/reference/platform/python-sdk
