from pathlib import Path

from wealth_pb_ee_models.models.pretrained_models import multi_taks_7classes_AP
from wealth_pb_ee_models.utils.utils import predict_single_file_AP

INPUT_DIR = Path("/app/input")
OUTPUT_DIR = Path("/app/output")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def predict_file(input_file: Path) -> Path:
    """Run WEALTH activPAL prediction for a single DATX file."""

    print(f"Processing: {input_file.name}")

    loaded_model, encoding_dict_PB, encoding_dict_EE = multi_taks_7classes_AP()

    df_predicted, _ = predict_single_file_AP(
        str(input_file),
        loaded_model,
        encoding_dict_PB,
        encoding_dict_EE,
    )

    output_file = OUTPUT_DIR / f"{input_file.stem}_predictions.csv"

    df_predicted.to_csv(output_file, index=False)

    print(f"Saved predictions to: {output_file}")

    return output_file


def main():

    input_files = sorted(INPUT_DIR.glob("*.datx"))

    if not input_files:
        raise RuntimeError(
            "No DATX files found in /app/input"
        )

    print(f"Found {len(input_files)} input files.")

    for input_file in input_files:
        predict_file(input_file)


if __name__ == "__main__":
    main()