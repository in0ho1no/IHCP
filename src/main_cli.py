import glob
import os

from core import convert_file2hcp_info_list


def main() -> None:
    input_folder = ".\\src\\input\\"
    hcp_file_list = glob.glob(input_folder + "**\\*.hcp", recursive=True)
    for hcp_file in hcp_file_list:
        # ファイルを読み込んでSVG画像として保存する
        hcp_info_list = convert_file2hcp_info_list(hcp_file)
        for hcp_info in hcp_info_list:
            # SVG画像として保存
            file_path = hcp_file.replace(input_folder, "")
            rename_path = "_".join(file_path.split("\\"))
            basename = os.path.basename(rename_path).split(".")[0]
            with open(f"./src/output/{basename}_{hcp_info.name}.svg", "w", encoding="utf-8") as f:
                f.write(hcp_info.svg_img)


if __name__ == "__main__":
    main()
